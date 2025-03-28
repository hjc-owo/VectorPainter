from typing import Union, Tuple
import copy
import shutil
import time
from pathlib import Path

from tqdm.auto import tqdm
import torch
import torch.nn.functional as F
from torchvision import transforms
from torchvision.utils import save_image
from PIL import Image
from transformers import Blip2ForConditionalGeneration, Blip2Processor

from vectorpainter.diffusers_warp import init_sdxl_pipeline
from vectorpainter.libs.engine import ModelState
from vectorpainter.painter import Painter, SketchPainterOptimizer, inversion, SinkhornLoss, \
    get_relative_pos, bezier_curve_loss
from vectorpainter.utils.plot import plot_couple, plot_img
from vectorpainter.utils import mkdirs, create_video


class VectorPainterPipeline(ModelState):
    def __init__(self, args):
        _exp = f"seed{args.seed}" \
               f"-canvas-{args.canvas_w}-{args.canvas_h}" \
               f"-{args.x.model_id}" \
               f"-{time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))}"
        super().__init__(args, log_path_suffix=_exp)

        self.imit_cfg = self.x_cfg.imit_stage
        self.synt_cfg = self.x_cfg.synth_stage

        # create log dir
        self.style_dir = self.result_path / "style_image"
        self.sd_sample_dir = self.result_path / "sd_sample"
        self.imit_png_logs_dir = self.result_path / "imit_png_logs"
        self.imit_svg_logs_dir = self.result_path / "imit_svg_logs"
        self.png_logs_dir = self.result_path / "png_logs"
        self.svg_logs_dir = self.result_path / "svg_logs"
        mkdirs([self.result_path, self.style_dir, self.sd_sample_dir,
                self.imit_png_logs_dir, self.imit_svg_logs_dir,
                self.png_logs_dir, self.svg_logs_dir])

        self.make_video = self.args.mv
        if self.make_video:
            self.frame_idx = 0
            self.frame_log_dir = self.result_path / "frame_logs"
            mkdirs([self.frame_log_dir])

        self.g_device = torch.Generator(device=self.device).manual_seed(args.seed)

    def painterly_rendering(self, text_prompt, negative_prompt, style_fpath, style_prompt):
        self.print(f"text prompt: {text_prompt}")
        self.print(f"negative prompt: {negative_prompt}")

        # load and preprocess style
        style_tensor = self.load_img_to_tensor(style_fpath)
        self.print(f"load style file from: {style_fpath}")
        shutil.copy(style_fpath, self.style_dir)  # copy style file
        plot_img(style_tensor, self.style_dir, fname="style_image_input")
        self.print(f"style_input shape: {style_tensor.shape}")

        # load and init renderer
        renderer = self.load_render(style_tensor)
        img = renderer.init_canvas(random=self.x_cfg.random_init)
        plot_img(img, self.style_dir, fname="stroke_init_style")
        renderer.save_svg(self.style_dir.as_posix(), fname="stroke_init_style")

        # stage 1
        renderer, recon_style_fpath = self.brushstroke_imitation(renderer)
        # stage 2
        self.synthesis_with_style_supervision(text_prompt,
                                              negative_prompt,
                                              renderer,
                                              style_prompt,
                                              style_fpath)

        # save the painting process as a video
        if self.make_video:
            self.print("\n making video...")
            video_path = self.result_path / "rendering.mp4"
            frame_log_dir = self.frame_log_dir / "iter%d.png"
            create_video(video_path, frame_log_dir, self.args.framerate)

        self.close(msg="painterly rendering complete.")

    def brushstroke_imitation(self, renderer: Painter) -> Tuple[Painter, Path]:
        # load optimizer
        optimizer = SketchPainterOptimizer(renderer,
                                           self.imit_cfg.lr,
                                           self.imit_cfg.color_lr,
                                           self.imit_cfg.width_lr,
                                           self.x_cfg.optim_opacity,
                                           self.x_cfg.optim_rgba,
                                           self.x_cfg.optim_width)
        optimizer.init_optimizers()

        self.print(f"-> Stoke Imitation Stage ...")
        self.print(f"-> Painter point params: {len(renderer.get_point_parameters())}")
        self.print(f"-> Painter width params: {len(renderer.get_width_parameters())}")
        self.print(f"-> Painter color params: {len(renderer.get_color_parameters())}")

        total_iter = self.imit_cfg.num_iter
        self.print(f"total optimization steps: {total_iter}")
        with tqdm(initial=self.step, total=total_iter, disable=not self.accelerator.is_main_process) as pbar:
            while self.step < total_iter:
                raster_sketch = renderer.get_image()
                loss = F.mse_loss(renderer.style_img, raster_sketch)

                # optimization
                optimizer.zero_grad_()
                loss.backward()
                optimizer.step_()

                # update lr
                if self.imit_cfg.lr_scheduler:
                    optimizer.update_lr(self.step, self.imit_cfg.decay_steps)

                # records
                pbar.set_description(
                    f"lr: {optimizer.get_lr():.2f}, "
                    f"l_total: {loss.item():.4f}"
                )

                # log raster and svg
                if self.step % self.args.save_step == 0 and self.accelerator.is_main_process:
                    plot_couple(renderer.style_img,
                                raster_sketch,
                                self.step,
                                output_dir=self.imit_png_logs_dir.as_posix(),
                                fname=f"iter{self.step}")
                    renderer.save_svg(self.imit_svg_logs_dir.as_posix(), fname=f"svg_iter{self.step}")

                self.step += 1
                pbar.update(1)

        # save style result
        renderer.save_svg(self.result_path.as_posix(), "style_result")
        style_result = renderer.get_image()
        recon_style_fpath = self.result_path / 'style_result.png'
        plot_img(style_result, self.result_path, fname='style_result')

        return renderer, recon_style_fpath

    def decode_and_save_latent(self, zT, ldm_pipe, fname='decode_zT'):
        zT = zT / ldm_pipe.vae.config.scaling_factor
        zT = zT.unsqueeze(0).to(ldm_pipe.vae.device, dtype=ldm_pipe.vae.dtype).detach().clone()

        with torch.no_grad():
            decoded = ldm_pipe.vae.decode(zT, return_dict=False)[0]

        decoded = (decoded.cpu() / 2 + 0.5).clamp(0, 1)
        plot_img(decoded.float(), self.sd_sample_dir, fname=fname)

    def captioning(self, image):
        blip2_processor = Blip2Processor.from_pretrained(
            "Salesforce/blip2-opt-6.7b",
            local_files_only=not self.args.model_download
        )
        blip2_model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-6.7b",
            load_in_8bit=True,
            device_map={"": 0},
            torch_dtype=torch.float16,
            local_files_only=not self.args.model_download
        )  # doctest: +IGNORE_RESULT
        inputs = blip2_processor(images=image, return_tensors="pt").to(device=self.device, dtype=torch.float16)
        generated_ids = blip2_model.generate(**inputs)
        caption = blip2_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        self.print(f"blip style prompt: {caption}")

        del blip2_processor, blip2_model
        torch.cuda.empty_cache()
        return caption

    def style_inversion(self, prompt, negative_prompt, style_prompt, init_fpath) -> Image:
        init_img = Image.open(init_fpath).convert("RGB").resize((1024, 1024))
        style_prompt = style_prompt if style_prompt is not None else self.captioning(init_img)

        # load pretrained diffusion model
        ldm_pipe = init_sdxl_pipeline(
            scheduler='ddim',
            device=self.device,
            torch_dtype=torch.float16,
            variant="fp16",
            local_files_only=not self.args.model_download,
            force_download=self.args.force_download,
            torch_compile=self.x_cfg.torch_compile,
            scaled_dot_product_attention=self.x_cfg.SDPA,
            enable_xformers=self.x_cfg.enable_xformers,
            gradient_checkpoint=self.x_cfg.gradient_checkpoint,
        )

        # ddim inversion
        x0 = copy.deepcopy(init_img)
        guidance_scale = 2
        zts = inversion.ddim_inversion(ldm_pipe, x0, style_prompt, self.x_cfg.num_inference_steps, guidance_scale)
        # zts: [ddim_steps+1, 4, w, h]
        zT, inversion_callback = inversion.make_inversion_callback(zts, offset=5)
        self.decode_and_save_latent(zT, ldm_pipe, fname="decode_zT")

        # instant style
        scale = {
            "up": {"block_0": [0.0, 1.0, 0.0]},
        }
        ldm_pipe.load_ip_adapter("h94/IP-Adapter",
                                 subfolder="sdxl_models",
                                 weight_name="ip-adapter_sdxl.bin",
                                 local_files_only=not self.args.model_download)
        ldm_pipe.set_ip_adapter_scale(scale)

        prompts = [style_prompt, prompt, prompt]
        latents = torch.randn(len(prompts), 4, 128, 128,
                              device=self.device,
                              generator=self.g_device,
                              dtype=ldm_pipe.unet.dtype)
        latents[0] = zT
        latents[1] = zT.clone()
        if isinstance(negative_prompt, str):
            negative_prompt = [negative_prompt] * len(prompts)

        outputs = ldm_pipe(
            prompt=prompts,
            negative_prompt=negative_prompt,
            height=1024,
            width=1024,
            ip_adapter_image=init_img,
            num_inference_steps=self.x_cfg.num_inference_steps,
            guidance_scale=self.x_cfg.guidance_scale,
            generator=self.g_device,
            latents=latents,
            add_watermarker=False,
            callback_on_step_end=inversion_callback,
            output_type='pt',
            return_dict=False
        )[0]
        self.print(outputs.shape)

        gen_file = self.sd_sample_dir / 'samples.png'
        save_image(outputs, fp=gen_file)
        target_file = self.sd_sample_dir / 'target.png'
        plot_img(outputs[-1], self.sd_sample_dir, fname='target')

        del ldm_pipe
        torch.cuda.empty_cache()

        target = Image.open(target_file)
        return target

    def synthesis_with_style_supervision(self, prompt, negative_prompt, renderer: Painter,
                                         style_prompt, recon_style_fpath: Path):
        # inversion
        target = self.style_inversion(prompt, negative_prompt, style_prompt, recon_style_fpath)
        inputs = self.img_to_tensor(target)
        inputs = inputs.detach()  # inputs as GT

        # log params
        init_relative_pos = get_relative_pos(renderer.get_point_parameters()).detach()  # init stroke position as GT
        init_curves = copy.deepcopy(renderer.get_point_parameters())

        # init optimizer
        optimizer = SketchPainterOptimizer(renderer,
                                           self.synt_cfg.lr,
                                           self.synt_cfg.color_lr,
                                           self.synt_cfg.width_lr,
                                           self.x_cfg.optim_opacity,
                                           self.x_cfg.optim_rgba,
                                           self.x_cfg.optim_width)
        optimizer.init_optimizers()

        self.print(f"\n-> Synthesis with Style Supervision ...")
        self.print(f"-> Painter points Params: {len(renderer.get_point_parameters())}")
        self.print(f"-> Painter width Params: {len(renderer.get_width_parameters())}")
        self.print(f"-> Painter color Params: {len(renderer.get_color_parameters())}")

        # init structure loss
        if self.x_cfg.struct_loss_weight > 0:
            if self.x_cfg.struct_loss == 'ssim':
                from vectorpainter.painter import SSIM
                l_struct_fn = SSIM()
            elif self.x_cfg.struct_loss == 'msssim':
                from vectorpainter.painter import MSSSIM
                l_struct_fn = MSSSIM()
            else:
                l_struct_fn = lambda x, y: torch.tensor(0.)  # zero loss

        # init shape loss
        sinkhorn_loss_fn = SinkhornLoss(device=self.device)

        self.step = 0
        total_iter = self.synt_cfg.num_iter
        self.print(f"total optimization steps: {total_iter}")
        with tqdm(initial=self.step, total=total_iter, disable=not self.accelerator.is_main_process) as pbar:
            while self.step < total_iter:
                raster_sketch = renderer.get_image()

                if self.make_video and (self.step % self.args.framefreq == 0 or self.step == total_iter - 1):
                    plot_img(raster_sketch, self.frame_log_dir, fname=f"iter{self.frame_idx}")
                    self.frame_idx += 1

                # recon loss
                l_recon = torch.tensor(0.)
                if self.x_cfg.l2_loss > 0:
                    l_recon = F.mse_loss(raster_sketch, inputs) * self.x_cfg.l2_loss

                # struct Loss
                l_struct = torch.tensor(0.)
                if self.x_cfg.struct_loss_weight > 0:
                    if self.x_cfg.struct_loss in ['ssim', 'msssim']:
                        l_struct = 1. - l_struct_fn(raster_sketch, inputs)
                    else:
                        l_struct = l_struct_fn(raster_sketch, inputs)

                # stroke loss
                l_rel_pos = torch.tensor(0.)
                if self.x_cfg.pos_loss_weight > 0:
                    if self.x_cfg.pos_type == 'pos':
                        l_rel_pos = F.mse_loss(get_relative_pos(renderer.get_point_parameters()),
                                               init_relative_pos) * self.x_cfg.pos_loss_weight
                    elif self.x_cfg.pos_type == 'bez':
                        l_rel_pos = bezier_curve_loss(renderer.get_point_parameters(),
                                                      init_curves) * self.x_cfg.pos_loss_weight
                    elif self.x_cfg.pos_type == 'sinkhorn':
                        l_rel_pos = sinkhorn_loss_fn(raster_sketch, renderer.style_img) * self.x_cfg.pos_loss_weight

                # total loss
                loss = l_recon + l_struct + l_rel_pos

                # optimization
                optimizer.zero_grad_()
                loss.backward()
                optimizer.step_()

                # update lr
                if self.synt_cfg.lr_scheduler:
                    optimizer.update_lr(self.step, self.synt_cfg.decay_steps)

                # records
                pbar.set_description(
                    f"lr: {optimizer.get_lr():.2f}, "
                    f"l_total: {loss.item():.4f}, "
                    f"l_recon: {l_recon.item():.4f}, "
                    f"l_struct: {l_struct.item():.4f}, "
                    f"l_pos: {l_rel_pos.item():.4f}"
                )

                # log raster and svg
                if self.step % self.args.save_step == 0 and self.accelerator.is_main_process:
                    # log png
                    plot_couple(inputs,
                                raster_sketch,
                                self.step,
                                output_dir=self.png_logs_dir.as_posix(),
                                fname=f"iter{self.step}",
                                prompt=prompt)
                    # log svg
                    renderer.save_svg(self.svg_logs_dir.as_posix(), fname=f"svg_iter{self.step}")

                self.step += 1
                pbar.update(1)

        # saving final result
        renderer.save_svg(self.result_path.as_posix(), "final_svg")
        final_raster_sketch = renderer.get_image().to(self.device)
        plot_img(final_raster_sketch, self.result_path, fname='final_render')

    def img_to_tensor(self, img) -> torch.Tensor:
        _transforms = [
            transforms.Resize(size=(self.canvas_width, self.canvas_height)),
            transforms.ToTensor(),
            transforms.Lambda(lambda t: t.unsqueeze(0)),
        ]
        if self.canvas_height == self.canvas_width:
            _transforms.append(transforms.CenterCrop(self.canvas_height))

        transform_pipe = transforms.Compose(_transforms)
        img_tensor = transform_pipe(img).to(self.device)
        return img_tensor

    def load_img_to_tensor(self, file_path: Union[str, Path]):
        assert Path(file_path).exists(), f"{file_path} is not exist!"
        pil_img = Image.open(file_path).convert("RGB")
        img_tensor = self.img_to_tensor(pil_img)
        return img_tensor

    def load_render(self, style_img):
        renderer = Painter(
            self.x_cfg,
            self.args.diffvg,
            style_img=style_img,
            style_dir=self.style_dir,
            num_strokes=self.x_cfg.num_paths,
            num_segments=self.x_cfg.num_segments,
            canvas_size=(self.canvas_width, self.canvas_height),
            device=self.device
        )
        return renderer

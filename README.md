# VectorPainter

### 🔥Quickstart

- style: `starry.jpg`

```shell
# sydney opera house
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A photo of Sydney opera house'" style="./assets/starry.jpg" "style_prompt='Van Gogh, Starry Sky, oil painting'" canvas_w=1024 canvas_h=1024 result_path='./workspace/Starry/sydney_starry_wo_ddim' seed=666
# mountain and cloud
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke "prompt='A mountain, with clouds in the sky'" style="./assets/starry.jpg" "style_prompt='Van Gogh, Starry Sky, oil painting'" canvas_w=1024 canvas_h=1024 result_path='./workspace/Starry/mountain' seed=666
```

- style: `brushstroke_azure_painting.jpg`

```shell
# mountain and cloud
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke "prompt='A mountain, with clouds in the sky.'" style="./assets/brushstroke_azure_painting.jpg" "style_prompt=''" canvas_w=1024 canvas_h=1024 result_path='./workspace/brushstroke_azure_painting/brush_mountain' seed=666
# test case, low recon step in stage 1
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py x=stroke "prompt='A painting of a watermelon. brushstoke style'" style="./assets/brushstroke_azure_painting.jpg" canvas_w=1024 canvas_h=1024 result_path='./workspace/brushstroke_azure_painting/brush_watermelon'
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke "prompt='A bouquet of blue roses.'" style="./assets/brushstroke_azure_painting.jpg" canvas_w=1024 canvas_h=1024 result_path='./workspace/brushstroke_azure_painting/brush_rose'
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke "prompt='sea waves. brushstoke style'" style="./assets/brushstroke_azure_painting.jpg" canvas_w=1024 canvas_h=768 result_path='./workspace/brushstroke_azure_painting/brush_wave'
```

- style: `oil_bouquet_of_flowers.jpg`

```shell
# mountain and cloud
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase.'" style="./assets/oil_bouquet_of_flowers.jpg" "style_prompt='flowers, oil painting'" canvas_w=1024 canvas_h=1024 result_path='./workspace/oil_bouquet_of_flowers/roses' seed=666
```

- style: `oil_full_field.jpg`
```shell
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py x=stroke "prompt='Field full of sunflowers'" style="./assets/oil_full_field.jpg" "style_prompt='flowers, oil painting'" canvas_w=1024 canvas_h=1024 result_path='./workspace/oil_full_field/sunflowers' seed=666
```

### Starry

```shell
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py x=stroke prompt='A horse is drinking water by the lake. van Gogh style.' style="./assets/starry.jpg" result_path='./workspace/Starry/horse_starry' seed=100
CUDA_VISIBLE_DEVICES=6 python vectorpainter.py "prompt='A photo of Sydney opera house.'" x=stroke style="./assets/starry.jpg" result_path='./workspace/Starry/sydney_starry' seed=8019
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke prompt='A painting of a cat.' style="./assets/starry.jpg" result_path='./workspace/Starry/cat_starry' seed=100
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py x=stroke "prompt='A mountain, with clouds in the sky.'" style="./assets/starry.jpg"  "style_prompt='starry night by van Gogh'" result_path='./workspace/Starry/mountain_starry'
CUDA_VISIBLE_DEVICES=5 python vectorpainter.py x=stroke "prompt='A dragon-cat hybrid.'" style="./assets/starry.jpg" result_path='./workspace/Starry/dragon_cat_starry'
```

### Sunflowers

```shell 
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase.'" style="./assets/sunflowers.jpg" result_path='./workspace/sunflowers/roses_sunflowers' seed=101
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py x=stroke "prompt='A fire-breathing dragon.'" style="./assets/sunflowers.jpg" result_path='./workspace/sunflowers/dragon_sunflowers' seed=100
CUDA_VISIBLE_DEVICES=4 python vectorpainter.py "prompt='A photo of Sydney opera house.'" x=stroke style="./assets/sunflowers.jpg" result_path='./workspace/sunflowers/sydney_sunflowers'
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py x=stroke "prompt='A bouquet of roses in a vase.'" style="./assets/sunflowers.jpg" x.pos_type='bez' x.pos_loss_weight=0.5 result_path='./workspace/sunflowers/roses_sunflowers_bez0.5' seed=100
```

### Field

```shell
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py "prompt='A brightly colored mushroom growing on a log. van Gogh style.'" x=stroke style="./assets/oil_field.jpg" result_path='./workspace/Field/mushroom_Field'
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py "prompt='A snail on a leaf. van Gogh style.'" x=stroke style="./assets/oil_field.jpg" result_path='./workspace/Field/snail_Field'
CUDA_VISIBLE_DEVICES=6 python vectorpainter.py "prompt='A photo of Sydney opera house on the sea.'" x=stroke style="./assets/oil_field.jpg" result_path='./workspace/Field/sydney_Field' seed=102
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py "prompt='A bamboo ladder propped up against an oak tree.'" x=stroke style="./assets/oil_field.jpg" "style_prompt='Van Gogh, Field, oil painting'" result_path='./workspace/Field/bamboo_Field' seed=100
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py "prompt='A rabbit cutting grass with a lawnmower.'" x=stroke style="./assets/oil_field.jpg" "style_prompt='Van Gogh, Field, oil painting'" result_path='./workspace/Field/rabbit_Field' seed=100
```

### Impression

```shell
CUDA_VISIBLE_DEVICES=5 python vectorpainter.py "prompt='A Torii Gate.'" x=stroke style="./assets/Impression.jpg" result_path='./workspace/impression/torii_impression'
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py "prompt='A beach with a cruise ship passing by.'" x=stroke style="./assets/Impression.jpg" result_path='./workspace/impression/beach_impression' seed=101
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py "prompt='A panda rowing a boat in a pond.'" x=stroke style="./assets/Impression.jpg" result_path='./workspace/impression/panda_impression' seed=106
CUDA_VISIBLE_DEVICES=3 python vectorpainter.py "prompt='An underwater submarine.'" x=stroke style="./assets/Impression.jpg" result_path='./workspace/impression/submarine_impression'
CUDA_VISIBLE_DEVICES=3 python vectorpainter.py "prompt='A boat on the lake.'" x=stroke style="./assets/Impression.jpg" result_path='./workspace/impression/boat_impression'
```

### Scream

```shell
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py "prompt='fire in the mountain.'" x=stroke style="./assets/scream.jpg" result_path='./workspace/scream/fire_scream'
CUDA_VISIBLE_DEVICES=2 python vectorpainter.py "prompt='The Great Wall.'" x=stroke style="./assets/scream.jpg" result_path='./workspace/scream/wall_scream'
CUDA_VISIBLE_DEVICES=1 python vectorpainter.py "prompt='The Great Pyramid.'" x=stroke style="./assets/scream.jpg" result_path='./workspace/scream/pyramid_scream'
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py "prompt='A Torii Gate.'" x=stroke style="./assets/scream.jpg" result_path='./workspace/scream/torii_scream'
```

### anxiety

```shell
CUDA_VISIBLE_DEVICES=3 python vectorpainter.py "prompt='fire in the mountain.'" x=stroke style="./assets/anxiety.jpg" result_path='./workspace/anxiety/fire_anxiety'
CUDA_VISIBLE_DEVICES=4 python vectorpainter.py "prompt='The winding Great Wall, with light sky. The anxiety of Edvard Munch style.'" x=stroke style="./assets/anxiety.jpg" result_path='./workspace/anxiety/wall_anxiety' seed=100
```

### Antimonocromatismo

```shell
CUDA_VISIBLE_DEVICES=4 python vectorpainter.py "prompt='A panda rowing a boat in a pond.'" x=stroke style="./assets/data_vis/sty/antimonocromatismo.png" result_path='./workspace/antimonocromatismo/panda_antimonocromatismo'
```

### Majeur

```shell
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py "prompt='The Great Pyramid.'" x=stroke style="./assets/majeur.jpg" result_path='./workspace/majeur/pyramid_majeur'
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py "prompt='A Torii Gate.'" x=stroke style="./assets/majeur.jpg" result_path='./workspace/majeur/torii_majeur'
CUDA_VISIBLE_DEVICES=7 python vectorpainter.py "prompt='The Great Wall.'" x=stroke style="./assets/majeur.jpg" result_path='./workspace/majeur/wall_majeur'
CUDA_VISIBLE_DEVICES=0 python vectorpainter.py "prompt='The Eiffel Tower.'" x=stroke style="./assets/majeur.jpg" result_path='./workspace/majeur/eiffel_majeur' seed=100
```

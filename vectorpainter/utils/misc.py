# -*- coding: utf-8 -*-
# Author: ximing
# Description: misc
# Copyright (c) 2023, XiMing Xing.
# License: MPL-2.0 License

import os
from datetime import datetime
import random
import pathlib
from typing import Any, List, Dict, Union
from subprocess import call

import omegaconf

"""Any Type"""
AnyPath = Union[str, pathlib.Path, os.PathLike]
AnyList = Union[omegaconf.ListConfig, List]
AnyDict = Union[omegaconf.DictConfig, Dict]


def render_batch_wrap(cfg: omegaconf.DictConfig,
                      seed_range: List,
                      pipeline: Any,
                      **pipe_args):
    start_time = datetime.now()
    for idx, seed in enumerate(seed_range):
        cfg.seed = seed  # update seed
        print(f"\n-> [{idx}/{len(seed_range)}], "
              f"current seed: {seed}, "
              f"current time: {datetime.now() - start_time}\n")
        pipe = pipeline(cfg)
        pipe.painterly_rendering(**pipe_args)


def get_seed_range(srange: AnyList):
    # random sampling without specifying a range
    start_, end_ = 1, 1000000
    if srange is not None:  # specify range sequential sampling
        seed_range_ = list(srange)
        assert len(seed_range_) == 2 and int(seed_range_[1]) > int(seed_range_[0])
        start_, end_ = int(seed_range_[0]), int(seed_range_[1])
        seed_range = [i for i in range(start_, end_)]
    else:
        # a list of lengths 1000 sampled from the range start_ to end_ (e.g.: [1, 1000000])
        numbers = list(range(start_, end_))
        seed_range = random.sample(numbers, k=1000)
    return seed_range


def mkdirs(dirs: List[pathlib.Path]):
    for _dir in dirs:
        _dir.mkdir(parents=True, exist_ok=True)


def create_video(video_path: pathlib.Path, frame_log_dir: AnyPath, framerate: int):
    # save .mp4
    call(["ffmpeg", "-framerate", str(framerate), "-i", frame_log_dir, "-vb", "20M", video_path])

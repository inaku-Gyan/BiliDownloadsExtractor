# coding=utf-8

import os
from json import loads
from copy import deepcopy
import ffmpeg
from typing import Callable


class Media:
    """
    存储一个视频对象，并记录其标题等信息
    """
    def __init__(self, path: str):
        self._path: str = path
        self._video: str = os.path.join(path, "16\\video.m4s")
        self._audio: str = os.path.join(path, "16\\audio.m4s")
        with open(os.path.join(path, "entry.json"), 'r', encoding='utf-8') as f:
            self._entry: dict = loads(f.read())

    @property
    def title(self) -> str:
        return self._entry['page_data']['part']

    @property
    def video(self) -> str:
        return self._video

    @property
    def audio(self) -> str:
        return self._audio

    @property
    def coll_name(self) -> str:
        return self._entry['title']

    @property
    def cover_url(self) -> str:
        return self._entry['cover']

    def is_in_any_coll(self) -> bool:
        return self.title != self.coll_name

    def show(self) -> str:
        return self.title


class Coll:
    """
    一个视频合集，类似于 `List[Media]` ，可以用 for-each 直接遍历其中的每一个 Media 对象
    """
    def __init__(self, path: str):
        self._path = path
        self._l: list[Media] = []
        for m in os.listdir(path):
            m_path = os.path.join(path, m)
            self._l.append(Media(m_path))
        self._name = self._l[0].coll_name

    def append(self, media: Media):
        self._l.append(media)

    @property
    def name(self) -> str:
        return self._name

    @property
    def content(self) -> list[Media]:
        return deepcopy(self._l)

    def __len__(self):
        return self._l.__len__()

    def video_titles(self) -> list[str]:
        r: list[str] = []
        for m in self._l:
            r.append(m.title)
        return r

    def show(self) -> str:
        return str(self.video_titles())

    def __iter__(self):
        return self._l.__iter__()


def scan(path: str) -> list[Media | Coll]:
    """
    扫描文件夹获得所有视频和合集
    这个文件夹必须是原始的，未经改动的
    :param path: 需要扫描的文件夹，应当为 ./tv.danmaku.bili/download
    :return: 包含所有视频和视频合集的列表
    """
    result: list[Media | Coll] = []
    for d in os.listdir(path):
        d_path = os.path.join(path, d)
        c = os.listdir(d_path)
        if len(c) == 1:
            result.append(Media(os.path.join(d_path, c[0])))
        else:
            result.append(Coll(d_path))
    return result


def default_get_name_func(media: Media) -> str:
    """
    直接用原视频标题作为导出后文件的标题
    """
    return media.title


def extract_video(media: Media, des_dir: str, fmt: str = 'mp4', copy: bool = False,
                  get_name_func: Callable[[Media], str] = default_get_name_func):
    """
    仅导出视频（无音频）文件，并转换为其他格式。（B站原始格式为 m4s）
    :param media: 需要导出的对象
    :param des_dir: 导出到的目标文件夹
    :param fmt: 导出文件的格式，即扩展名（不包括句点）
    :param copy: 是否启用 ffmpeg 的 `c=copy` 参数，启用后意味着文件不会重新编码，而是直接复制原始格式
    :param get_name_func: 一个函数，用于产生导出后的文件名（不包括扩展名）。这个函数输入目标 Media，输出一个字符串为目标文件名
    """
    name = get_name_func(media) + '.' + fmt
    des = os.path.join(des_dir, name)
    video_stream = ffmpeg.input(media.video)
    if copy:
        out = ffmpeg.output(video_stream, des, c='copy')
    else:
        out = ffmpeg.output(video_stream, des)
    ffmpeg.run(out, overwrite_output=True, quiet=True)


def extract_audio(media: Media, des_dir: str, fmt: str = 'mp3', copy: bool = False,
                  get_name_func: Callable[[Media], str] = default_get_name_func):
    """
    仅导出音频（无视频）文件，并转换为其他格式。（B站原始格式为 m4s）
    :param media: 需要导出的对象
    :param des_dir: 导出到的目标文件夹
    :param fmt: 导出文件的格式，即扩展名（不包括句点）
    :param copy: 是否启用 ffmpeg 的 `c=copy` 参数，启用后意味着文件不会重新编码，而是直接复制原始格式
    :param get_name_func: 一个函数，用于产生导出后的文件名（不包括扩展名）。这个函数输入目标 Media，输出一个字符串为目标文件名
    """
    name = get_name_func(media) + '.' + fmt
    des = os.path.join(des_dir, name)
    audio_stream = ffmpeg.input(media.audio)
    if copy:
        out = ffmpeg.output(audio_stream, des, c='copy')
    else:
        out = ffmpeg.output(audio_stream, des)
    ffmpeg.run(out, overwrite_output=True, quiet=True)


def extract_and_merge(media: Media, des_dir: str, fmt: str = 'mp4', copy: bool = False,
                  get_name_func: Callable[[Media], str] = default_get_name_func):
    """
    仅导出完整视频（同时有视频流和音频流）文件，并转换为某格式。
    Args:
        `media`: 需要导出的对象
        `des_dir`: 导出到的目标文件夹
        `fmt`: 导出文件的格式，即扩展名（不包括句点）
        `copy`: 是否启用 ffmpeg 的 `c=copy` 参数，启用后意味着文件不会重新编码，而是直接复制原始格式
        `get_name_func`: 一个函数，用于产生导出后的文件名（不包括扩展名）。这个函数输入目标 Media，输出一个字符串为目标文件名
    """
    name = get_name_func(media) + '.' + fmt
    des = os.path.join(des_dir, name)
    audio_stream = ffmpeg.input(media.audio)
    video_stream = ffmpeg.input(media.video)
    if copy:
        out = ffmpeg.output(audio_stream, video_stream, des, c='copy')
    else:
        out = ffmpeg.output(audio_stream, video_stream, des)
    ffmpeg.run(out, overwrite_output=True, quiet=True)












if __name__ == '__main__':
    ...


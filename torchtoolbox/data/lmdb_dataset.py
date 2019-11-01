# -*- coding: utf-8 -*-
# @Author  : DevinYang(pistonyang@gmail.com)
__all__ = ['ImageLMDB']

import os
import pyarrow
import lmdb
import six
from ..tools.convert_lmdb import get_key, load_pyarrow
from PIL import Image
from torch.utils.data import Dataset


class ImageLMDB(Dataset):
    """
    LMDB format for image folder.
    """

    def __init__(self, db_path, transform=None, target_transform=None):
        self.env = lmdb.open(db_path, subdir=os.path.isdir(db_path),
                             readonly=True, lock=False,
                             readahead=False, meminit=False)
        with self.env.begin() as txn:
            self.length = load_pyarrow(txn.get(b'__len__'))

        self.map_list = [get_key(i) for i in range(self.length)]
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        with self.env.begin() as txn:
            byteflow = txn.get(self.map_list[item])
        unpacked = load_pyarrow(byteflow)
        imgbuf, target = unpacked
        buf = six.BytesIO(imgbuf)
        img = Image.open(buf).convert('RGB')

        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target
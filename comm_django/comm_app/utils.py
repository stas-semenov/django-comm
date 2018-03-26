# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def check_int_positive(val):
    if val is not None:
        try:
            return int(val)
        except ValueError:
            pass
    return -1

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.


class Comment(MPTTModel):
    user_id = models.IntegerField(db_index=True)
    entity_id = models.IntegerField(db_index=True, null=True, blank=True)
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    text = models.TextField(default='')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['date']

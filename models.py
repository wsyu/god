#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：models.py
date ： 2022/11/22
time ： 19:54
Author ： wsy
desc ：
"""

from tortoise import fields
from tortoise.models import Model

class Stock(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")
    is_del = fields.IntField(default=0, description="删除标记")

    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=6)
    name = fields.CharField(max_length=20)
    day = fields.DateField(description="交易日期")
    first_price = fields.DecimalField(decimal_places=2, max_digits=6)
    last_price = fields.DecimalField(default=0, decimal_places=2, max_digits=6)
    close_price = fields.DecimalField(default=0, decimal_places=2, max_digits=6, description="收盘价")
    volume_ratio = fields.DecimalField(decimal_places=2, max_digits=6,description="量比")
    outer_disc = fields.IntField(default=0, description="外盘")
    inter_disc = fields.IntField(default=0, description="内盘")
    turnover_rate = fields.DecimalField(default=0, decimal_places=2, max_digits=6, description="换手率")
    last_day_turnover_rate = fields.DecimalField(default=0, decimal_places=2, max_digits=6, description="上一个交易日换手率")
    circulation_market_value = fields.DecimalField(default=0, decimal_places=2, max_digits=6, description="流通市值")
    add_num = fields.IntField(default=1)
    TTM = fields.DecimalField(default=0, decimal_places=2, max_digits=6, description="ttm市盈率")
    is_push = fields.IntField(default=0)

    class Meta:
        table = "tb_stock"
        unique_together = ('code', 'day')
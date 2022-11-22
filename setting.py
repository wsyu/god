#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：setting.py
date ： 2022/11/22
time ： 19:48
Author ： wsy
desc ：
"""
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""
数据库连接可以配置多个，表示可以同时连接多个数据库，配置如下
"""
HOST = "192.168.68.187"
PORT = 3306
USER = 'root'
PASSWORD = '123456'
DATABASE = 'fastapidemo'


# -----------------------定时任务配置----------------------------
INTERVAL_TASK = {
    # 配置存储器
    "jobstores": {
        'default': SQLAlchemyJobStore(url=f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8")
    },
    # 配置执行器
    "executors": {
        # 'default': ThreadPoolExecutor(20),
        # 使用进行池进行调试，最大进程数是5个
        # 'processpool': ProcessPoolExecutor(5),
        'async': AsyncIOExecutor()
    },
    # 创建jobs默认参数
    "job_defaults": {
        'coalesce': False, # 是否合并执行
        "max_instances": 9 # 最大实例数
    },
    "timezone": "Asia/Shanghai"  # 解决linux系统环境timezone不对称报错
}

# scheduler = AsyncIOScheduler(**INTERVAL_TASK)
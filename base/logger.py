# -*- coding: utf-8 -*-
"""
@Time ： 2026/10/12 14:18
@Author ：Peter Peng
@File ：logger.py
@Desc ：
"""
# 导入日志库
import logging
# 导入路径操作库
import os
# 导入配置类
from config import Config

import os.path
import logging
from base.config import config


def setup_logger(logger_name='EduRAG', logger_file=config.LOG_FILE):
    # 1. 确保日志目录存在，不存在创建
    # logger_file 是日志的文件名，所以我们先取到它所在的目录 os.path.pathj
    dirname = os.path.dirname(logger_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    # 2. 创建日志记录器: Logger
    # 2.1 获取Logger对象
    logger = logging.getLogger(logger_name)
    # 2.2 设置日志级别为所有控制器最低的(设置全局的日志级别)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # 3. 创建控制台控制器：StreamHandler
        # 3.1 创建控制台处理器对象
        stream_handler = logging.StreamHandler()
        # 3.2 设置日志级别为INFO
        stream_handler.setLevel(logging.INFO)
        # 4. 创建文件处理器:FileHandler，并指定目录
        # 4.1 创建文件处理对象
        file_handler = logging.FileHandler(logger_file, mode='a')
        # 4.2 设置日志级别为DEBUG
        file_handler.setLevel(logging.DEBUG)
        # 5. 定义并设置日志格式：
        # 5.1 定义日志格式：logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(pathname)s - %(funcName)s - %(module)s - %(lineno)d - %(message)s')
        # 5.2 设置处理器日志格式
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # 6. 把处理器添加到logger中
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger('EduRAG')

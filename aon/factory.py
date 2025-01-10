import atexit
import logging
import logging.config
import platform
import yaml
import os
from flask import Flask

from aon.core import JSONEncoder, db, scheduler
from aon.api.router import router
from aon.exception import *
from aon.response import ResMsg
from aon.code import ResponseCode


def create_app(config_name, config_path=None):
    app = Flask(__name__)
    # 读取配置文件
    if not config_path:
        pwd = os.getcwd()
        config_path = os.path.join(pwd, 'config/config.yaml')
    if not config_name:
        config_name = 'PRODUCTION'

    # 读取配置文件
    conf = read_yaml(config_name, config_path)
    app.config.update(conf)

    # 注册接口
    register_api(app=app, routers=router)

    # 返回json格式转换
    app.json_encoder = JSONEncoder

    # 注册数据库连接
    db.app = app
    db.init_app(app)

    #@app.errorhandler(Exception)
    #def handle_expired_error(e):
    #    return ResMsg(code=ResponseCode.SystemError).data, 500

    # 启动定时任务
    if app.config.get("SCHEDULER_OPEN"):
        scheduler_init(app)

    # 日志文件目录
    if not os.path.exists(app.config['LOGGING_PATH']):
        os.mkdir(app.config['LOGGING_PATH'])

    # 日志设置
    with open(app.config['LOGGING_CONFIG_PATH'], 'r', encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f.read())
    logging.config.dictConfig(dict_conf)

    # 读取msg配置
    with open(app.config['RESPONSE_MESSAGE'], 'r', encoding='utf-8') as f:
        msg = yaml.safe_load(f.read())
        app.config.update(msg)

    return app


def read_yaml(config_name, config_path):
    """
    config_name:需要读取的配置内容
    config_path:配置文件路径
    """
    if config_name and config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')


def register_api(app, routers):
    for router_api in routers:
        app.register_blueprint(router_api)


def scheduler_init(app):
    """
    保证系统只启动一次定时任务
    :param app:
    :return:
    """
    if platform.system() != 'Windows':
        fcntl = __import__("fcntl")
        f = open('scheduler.lock', 'wb')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.info('Scheduler Started,---------------')
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)
    else:
        msvcrt = __import__('msvcrt')
        f = open('scheduler.lock', 'wb')
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.debug('Scheduler Started,----------------')
        except:
            pass

        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass

        atexit.register(_unlock_file)
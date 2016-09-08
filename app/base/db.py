import pymysql
from flask import g
from config import config


def dbcnn():
    if not hasattr(g, 'cnn'):
        g.cnn = pymysql.connect(**config.db1)

import os

MODE = "default"

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '123aAA2334qqSwqDfg'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.igenwo.com'
    MAIL_PORT = 25
    # MAIL_USE_TLS = True
    MAIL_USERNAME = 'king@igenwo.com'
    MAIL_PASSWORD = 'a41030122Q'
    FLASKY_MAIL_SUBJECT_PREFIX = 'igenwo'
    FLASKY_MAIL_SENDER = 'king@igenwo.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 1200
    host_url = 'http://121.40.30.193'
    php_api_url = 'http://120.40.30.193:82/wanka/productselect'
    php_token = 'kwk4wco8g8cc0k00gkc8c8s4oo8cwko44go480g8'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    db1 = {'host': 'localhost', 'user': 'root', 'password': 'LiuHang!123',
           'port': 3306, 'database': 'igenwo', 'charset': 'utf8'}
    upload_path = basedir
    static_folder = os.path.join(basedir, 'app', 'static')
    redis = {'host': 'localhost', 'port': 6379}
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://' + db1['user'] + ':' + db1['password'] +
        '@' + db1['host'] + ':' + str(db1['port']) +
        '/' + db1['database'] + '?charset=utf8')


class TestingConfig(Config):
    # TESTING = True
    DEBUG = True
    db1 = {'host': 'localhost', 'user': 'root',
           'password': 'joyzone', 'port': 3306,
           'database': 'igenwo', 'charset': 'utf8'}
    upload_path = basedir
    static_folder = os.path.join(basedir, 'app', 'static')
    redis = {'host': 'localhost', 'port': 6379}
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://' + db1['user'] + ':' + db1['password'] +
        '@' + db1['host'] + ':' + str(db1['port']) +
        '/' + db1['database'] + '?charset=utf8')


class ProductionConfig(Config):
    db1 = {'host': 'localhost', 'user': 'root', 'password': 'LiuHang!123',
           'port': 3306, 'database': 'igenwo', 'charset': 'utf8'}
    upload_path = basedir
    static_folder = os.path.join(basedir, 'app', 'static')
    redis = {'host': 'localhost', 'port': 6379}
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://' + db1['user'] + ':' + db1['password'] +
        '@' + db1['host'] + ':' + str(db1['port']) +
        '/' + db1['database'] + '?charset=utf8')


conf = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

config = conf[MODE]

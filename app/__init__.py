from werkzeug.contrib.cache import RedisCache
from config import config

cache = RedisCache(**config.redis)

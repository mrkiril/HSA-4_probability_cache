import logging
import logging.config
import os
import sys


def load_from_file(filename, exception_text, mute=False):
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception:
        if not mute:
            logging.warning(exception_text)


class Config:
    def __init__(self, test=False):
        self.test = test
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.templates_folder = "templates"

        self.env = os.environ.get("ENV_NAME", 'local')
        self.log_level = os.environ.get("LOG_LEVEL", "ERROR")

        self.app_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.app_port = int(os.environ.get("APP_PORT", "3800"))
        self.MAX_BODY_SIZE = os.environ.get("MAX_BODY_SIZE", 100 * 1024 * 1024)
        self.use_probabilistic_cache = os.environ.get("USE_PROBABILISTIC_CACHE", "false") == 'true'

        self.db_name = os.environ.get("POSTGRES_DB", "db-reface-auth-new")
        self.db_user = os.environ.get("POSTGRES_USER", "master")
        self.db_host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
        self.db_port = os.environ.get("POSTGRES_PORT", "5432")
        self.db_pass = os.environ.get("POSTGRES_PASSWORD", "mysecretpassword")
        self.postgres_max_connections = int(os.environ.get("POSTGRES_MAX_CONNECTIONS", "50"))

        self.redis_host = os.environ.get("REDIS_HOST")
        self.redis_port = os.environ.get("REDIS_PORT")

        self.redis_replica_host = os.environ.get("REDIS_REPLICA_HOST")
        self.redis_replica_port = os.environ.get("REDIS_REPLICA_PORT")



        self.log_handlers = ["console"]
        self.log_format = "%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s"

        self.DEFAULT_LOGGING = {
            "version": 1,
            'disable_existing_loggers': False,
            "formatters": {
                "standard": {
                    "format": self.log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "simple": {
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": "DEBUG",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "": {
                    "level": self.log_level,
                    # 'handlers': ['console', 'file'],
                    "handlers": self.log_handlers,
                    "propagate": False,
                },
                "migrations": {
                    "level": "DEBUG",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "google": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "cachecontrol": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "peewee.async": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "peewee": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "urllib3": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
                "aiohttp": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": self.log_handlers,
                },
            },
        }

    def is_test_env(self):
        return self.test


conf = Config()

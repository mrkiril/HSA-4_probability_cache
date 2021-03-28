import linecache
import tracemalloc
import asyncio
import logging
import os
import sys

import aiohttp_jinja2
import jinja2
import uvloop
from aiohttp import log, web
from aiomisc import ThreadPoolExecutor
from peewee import Proxy
from peewee_asyncext import PooledPostgresqlExtDatabase

from app.api.routes import routes
from app.models import db_proxy, ExtendedDBManager, Article
from settings import Config


logger = logging.getLogger(__name__)


def init_db(conf: Config) -> Proxy:
    db_conf = PooledPostgresqlExtDatabase(
        conf.db_name,
        user=conf.db_user,
        host=conf.db_host,
        port=conf.db_port,
        password=conf.db_pass,
        register_hstore=False,
        autorollback=True,
        max_connections=conf.postgres_max_connections
    )

    db_proxy.initialize(db_conf)
    return db_proxy


async def on_startup(app):
    conf: Config = app["conf"]

    # setup templates renderer
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(conf.templates_folder))

    logging.basicConfig(level=logging.DEBUG)
    logging.config.dictConfig(conf.DEFAULT_LOGGING)
    app["db"] = ExtendedDBManager(init_db(conf))
    app["db"].database.create_tables([Article], safe=True)


async def on_cleanup(app):
    app["db"].database.drop_tables([Article])
    await app["db"].close()
    app["executor"].shutdown(wait=False)


async def on_shutdown(app):
    pass


def setup_app(conf):
    app = web.Application(
        client_max_size=conf.MAX_BODY_SIZE,
        logger=log.access_logger,
        middlewares=[]
    )
    app["conf"] = conf

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_shutdown)

    app.router.add_routes(routes)  # setup views and routes

    loop = asyncio.get_event_loop()

    executor = ThreadPoolExecutor(max_workers=10)
    app["executor"] = executor

    loop.set_default_executor(executor)

    return app


if __name__ == "__main__":
    argv = sys.argv[1:]
    uvloop.install()
    conf = Config()
    app = setup_app(conf)
    web.run_app(app, host=conf.app_host, port=conf.app_port)

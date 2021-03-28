import asyncio
import json
import logging
import os
import random
import string
import uuid
from functools import partial


import aiohttp_jinja2

import psycopg2
from aiohttp import web

from app.models import ExtendedDBManager, Article
from app.serializers import ArticlesSerializer
from settings import conf


logger = logging.getLogger(__name__)


def get_random_string(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(n))


class ArticleHandler:
    def __init__(self, db):
        self.db = db

    async def get(self, article_id) -> ArticlesSerializer:
        query = (
            Article.select().where(Article.article_id == article_id)
        )
        article = await self.db.get_or_none_async(query)
        return ArticlesSerializer.from_orm(article)



class HealthzCheck(web.View):
    async def get(self):
        # Everything is ok
        return web.HTTPOk()


class ArticleView(web.View):
    @aiohttp_jinja2.template("main_page.jinja2")
    async def get(self):
        db: ExtendedDBManager = self.request.app["db"]
        article_id = self.request.match_info["article_id"]

        # query = (
        #     Article.select().where(Article.article_id == article_id)
        # )
        # article = await db.get_or_none_async(query)
        art_handler = ArticleHandler(db=db)
        article: ArticlesSerializer = await art_handler.get(article_id=article_id)
        return web.json_response(text=article.json())

    async def post(self):
        db: ExtendedDBManager = self.request.app["db"]
        new_article = Article(
            article_id=str(uuid.uuid4()),
            status=0,
            name=get_random_string(15),
            body=get_random_string(100),
        )
        await db.create(new_article)


class ArticlesView(web.View):
    async def get(self):
        db: ExtendedDBManager = self.request.app["db"]
        query = (
            Article.select().limit(100)
        )
        articles = await db.execute(query)
        return web.json_response([art.serialize() for art in articles])


class Favicon(web.View):
    async def get(self):
        root_path = self.request.app['conf'].root_path
        return web.FileResponse(path=os.path.join(root_path, 'templates/favicon.ico'))

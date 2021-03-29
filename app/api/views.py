import asyncio
import json
import logging
import os
import random
import string
import uuid
from functools import partial
from typing import Optional

import aiohttp_jinja2

import psycopg2
from aiohttp import web
from peewee import DoesNotExist

from app.models import ExtendedDBManager, Article
from app.serializers import ArticlesSerializer, ArticlesListSerializer
from settings import conf


logger = logging.getLogger(__name__)


def get_random_string(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(n))


class ArticleHandler:
    def __init__(self, db, redis_cli, use_probabilistic_cache):
        self.db = db
        self.redis_cli = redis_cli
        self.use_probabilistic_cache = use_probabilistic_cache

    def __get_from_cache(self, article_id):
        if self.use_probabilistic_cache:
            print("lalala")
        cache_article_str = self.redis_cli.get(f"article_{article_id}")
        if cache_article_str:
            return json.loads(cache_article_str)

    def __set_art_to_cache(self, obj: ArticlesSerializer):
        self.redis_cli.set(f"article_{obj.article_id}", str(obj.json()), ex=120)  # 10s

    async def get(self, article_id) -> Optional[ArticlesSerializer]:
        cache_article_obj: Optional[dict] = self.__get_from_cache(article_id)
        if cache_article_obj:
            return ArticlesSerializer(**cache_article_obj)

        query = Article.select().where(Article.article_id == article_id)
        article = await self.db.get_or_none_async(query)
        if article:
            art = ArticlesSerializer.from_orm(article)
            self.__set_art_to_cache(art)
            return art

    async def create(self, db):
        new_article = await db.create(
            Article,
            status=0,
            name=get_random_string(15),
            body=get_random_string(100),
        )
        return new_article


class ArticleView(web.View):
    async def get(self):
        db: ExtendedDBManager = self.request.app["db"]
        redis_cli = self.request.app["redis_cli"]
        use_probabilistic_cache: bool = self.request.app["conf"].use_probabilistic_cache
        article_id = self.request.match_info["article_id"]

        art_handler = ArticleHandler(
            db=db, redis_cli=redis_cli, use_probabilistic_cache=use_probabilistic_cache
        )
        await art_handler.create(db=db)
        article: ArticlesSerializer = await art_handler.get(article_id=article_id)
        if article:
            return web.json_response(text=article.json())
        raise web.HTTPNotFound()

    async def post(self):
        db: ExtendedDBManager = self.request.app["db"]
        art_handler = ArticleHandler(db=db)
        article: ArticlesSerializer = await art_handler.create(db=db)
        raise web.HTTPOk()


class ArticlesView(web.View):
    async def get(self):
        db: ExtendedDBManager = self.request.app["db"]
        query = (
            Article.select().limit(100)
        )
        try:
            articles = await db.execute(query)
        except (DoesNotExist, TypeError):
            articles = None
        if articles is None:
            raise web.HTTPNotFound()

        return web.json_response(text=ArticlesListSerializer(articles=[art for art in articles]).json())


class HealthzCheck(web.View):
    async def get(self):
        # Everything is ok
        return web.HTTPOk()


class Favicon(web.View):
    async def get(self):
        root_path = self.request.app['conf'].root_path
        return web.FileResponse(path=os.path.join(root_path, 'templates/favicon.ico'))

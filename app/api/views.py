import asyncio
import json
import logging
import os
import random
import string
import time
from datetime import datetime
from functools import partial
from typing import Optional

from aiohttp import web
from peewee import DoesNotExist

from app.models import ExtendedDBManager, Article
from app.serializers import ArticlesSerializer, ArticlesListSerializer


logger = logging.getLogger(__name__)


def get_random_string(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def pretty_dt(ts):
    return datetime.utcfromtimestamp(ts).strftime('%H:%M:%S')


class ArticleHandler:

    CACHE_BLUR_GAP = 60
    CACHE_TIMEOUT = 180

    def __init__(self, db, redis_cli, use_probabilistic_cache):
        self.db = db
        self.redis_cli = redis_cli
        self.use_probabilistic_cache = use_probabilistic_cache
        self.CACHE_BLUR_TIME_NEXT = None
        self.CACHE_BLUR_TIME_NEXT_NEXT = None

    def __is_probabilistic_period(self):
        current_time = time.time()
        if not self.CACHE_BLUR_TIME_NEXT:
            self.CACHE_BLUR_TIME_NEXT = current_time + self.CACHE_TIMEOUT - self.CACHE_BLUR_GAP
            self.CACHE_BLUR_TIME_NEXT_NEXT = current_time + 2 * self.CACHE_TIMEOUT - self.CACHE_BLUR_GAP
            print(f"Start cache next {pretty_dt(self.CACHE_BLUR_TIME_NEXT)}   next-next {pretty_dt(self.CACHE_BLUR_TIME_NEXT_NEXT)}")

        if (
            self.CACHE_BLUR_TIME_NEXT <= current_time <= self.CACHE_BLUR_TIME_NEXT + self.CACHE_BLUR_GAP
            and random.randint(0, 9) >= 8
        ):
            print(f"In cache next {pretty_dt(self.CACHE_BLUR_TIME_NEXT)}   next-next {pretty_dt(self.CACHE_BLUR_TIME_NEXT_NEXT)}")
            return True

        if (
            self.CACHE_BLUR_TIME_NEXT_NEXT <= current_time <= self.CACHE_BLUR_TIME_NEXT_NEXT + self.CACHE_BLUR_GAP
        ):
            self.CACHE_BLUR_TIME_NEXT += self.CACHE_TIMEOUT
            self.CACHE_BLUR_TIME_NEXT_NEXT += self.CACHE_TIMEOUT
            return True

        return False

    async def __get_from_cache(self, article_id):
        if self.use_probabilistic_cache:
            is_pp = self.__is_probabilistic_period()
            if is_pp:
                return

        loop = asyncio.get_event_loop()
        cache_article_str = await loop.run_in_executor(None, partial(self.redis_cli.get, f"article_{article_id}"))

        if cache_article_str:
            return json.loads(cache_article_str)

    def __set_art_to_cache(self, obj: ArticlesSerializer):
        self.redis_cli.set(f"article_{obj.article_id}", str(obj.json()), ex=self.CACHE_TIMEOUT)  # 10s

    async def get(self, article_id) -> Optional[ArticlesSerializer]:
        cache_article_obj: Optional[dict] = await self.__get_from_cache(article_id)
        if cache_article_obj:
            return ArticlesSerializer(**cache_article_obj)

        query = Article.select().where(Article.article_id == article_id)
        article = await self.db.get_or_none_async(query)
        if article:
            art = ArticlesSerializer.from_orm(article)
            self.__set_art_to_cache(art)
            return art

    async def create(self, db):
        body = """
        MINNEAPOLIS — For nearly a year, the country’s understanding of George Floyd’s death has come mostly from a gruesome video of a white Minneapolis police officer kneeling on Mr. Floyd’s neck for more than nine minutes. It has become, for many, a painful encapsulation of racism in policing.
        But as the murder trial of the officer, Derek Chauvin, opened on Monday, his lawyer attempted to convince jurors that there was more to know about Mr. Floyd’s death than the stark video.
        The case was about Mr. Floyd’s drug use, the lawyer, Eric J. Nelson, argued. It was about Mr. Floyd’s size, his resistance of police officers and his weakened heart, the lawyer said. It was about an increasingly agitated crowd that gathered at an intersection in South Minneapolis, which he said diverted Mr. Chauvin’s attention from Mr. Floyd, who was Black. This, Mr. Nelson asserted, was, in part, an overdose, not a police murder.
        Prosecutors, however, said that the case was exactly what it seemed to be — and exactly what the video, with its graphic, indelible moments, had revealed.
        """
        new_article = await db.create(
            Article,
            status=0,
            name=f"Title - {get_random_string(15)}",
            body=body + get_random_string(100),
        )
        return new_article


class ArticleView(web.View):
    async def get(self):
        db: ExtendedDBManager = self.request.app["db"]
        art_handler = self.request.app["art_handler"]
        # redis_cli = self.request.app["redis_cli"]
        # use_probabilistic_cache: bool = self.request.app["conf"].use_probabilistic_cache
        article_id = self.request.match_info["article_id"]


        if int(article_id) % 2 == 0:
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

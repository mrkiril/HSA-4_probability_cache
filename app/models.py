import logging
from datetime import datetime

import peewee_async
from peewee import (
    Model, Proxy, SmallIntegerField, CharField, TextField,
    DateTimeField, DoesNotExist, ProgrammingError
)

db_proxy = Proxy()


class ExtendedDBManager(peewee_async.Manager):

    async def execute(self, query):
        try:
            query = await super().execute(query)
            return query

        except ProgrammingError as e:
            logging.error(
                f"Model does not exists. Request has been silently ignored. "
                f"Please migrate you database. {e}",
                exc_info=True,
            )

    async def get_or_none_async(self, model, *query, **kwargs):
        try:
            return await self.get(model, *query, **kwargs)
        except (DoesNotExist, TypeError):
            return None


class BaseModel(Model):
    @classmethod
    def table_name(cls):
        return cls._meta.table_name

    def serialize(self):
        """JSON serializer for objects not serializable by default json code"""
        return self.__dict__["__data__"]

    class Meta:
        database = db_proxy


class Article(BaseModel):
    article_id = CharField(null=False, unique=True, primary_key=True)
    status = SmallIntegerField(null=False, index=True)
    name = TextField(null=False)
    body = TextField(null=False)
    created_date = DateTimeField(index=True, default=datetime.utcnow)
    modified_date = DateTimeField(null=True, index=True)
    deleted_date = DateTimeField(null=True, index=True)

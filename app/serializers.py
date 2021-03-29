import uuid
from datetime import datetime
from typing import Union, Optional, no_type_check, List

from pydantic import BaseModel, Field, constr


class PydBaseModel(BaseModel):
    @classmethod
    @no_type_check
    def _get_value(cls, *args, **kwargs):
        v = super()._get_value(*args, **kwargs)

        if isinstance(v, uuid.UUID):
            return str(v)
        else:
            return v


class ArticlesSerializer(PydBaseModel):
    class Config:
        orm_mode = True

    article_id: int  # required field
    status: int
    name: constr(min_length=5)
    body: constr(min_length=10)
    created_date: datetime
    modified_date: Optional[datetime]
    deleted_date: Optional[datetime]


class ArticlesListSerializer(PydBaseModel):
    articles: List[ArticlesSerializer]

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import lazyload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.database import Base, SessionType

T_Model = TypeVar("T_Model", bound=Base)


class PaginationFilters(BaseModel):
    page: int = Query(default=1)
    per_page: int = Query(default=50)


@dataclass
class Pagination(Generic[T_Model]):
    page: int
    per_page: int
    total: int
    items: list[T_Model]

    first: int = field(init=False)
    last: int = field(init=False)
    pages: int = field(init=False)

    has_prev: bool = field(init=False)
    has_next: bool = field(init=False)
    prev_num: Optional[int] = field(init=False)
    next_num: Optional[int] = field(init=False)

    def __post_init__(self):
        """Workaround for the FastAPI response serialisation because PyDantic ignores the properties"""
        self.first = (self.page - 1) * self.per_page + 1
        self.last = max(self.first, self.first + len(self.items) - 1)
        self.pages = 0 if self.total == 0 else ceil(self.total / self.per_page)
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None


def human_name(class_name: str) -> str:
    return "".join([c if c.islower() else f" {c}" for c in class_name]).strip()


class BaseDao(Generic[T_Model]):
    class Meta:
        model: T_Model = NotImplemented
        order_options: Optional[Dict[Any, Any]]
        default_order_by: Optional[List[Any]]

    def __init__(self, session: SessionType | None = None):
        self.session = session

    def create(self, *args, **kwargs) -> T_Model:
        raise NotImplementedError

    def update(self, *args, **kwargs) -> Optional[T_Model]:
        raise NotImplementedError

    def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def query(self, *args, **kwargs):
        return select(self.Meta.model)

    def bulk_update(self, where: dict, fields: dict):
        query = self.query(**where)
        query.update(fields)
        self.session.flush()

    def list_query(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def build_list_query(self, *args, order_by: Optional[List[Any]] = None, **kwargs):
        query = self.list_query(*args, **kwargs)
        return self.apply_ordering(query, order_by=order_by)

    def apply_ordering(self, query, order_by: Optional[List[Any]] = None):
        if order_by and hasattr(self.Meta, "order_options"):
            order_expressions = []
            for _order_by in order_by:
                exp = self.Meta.order_options[_order_by]
                if isinstance(exp, Iterable):
                    order_expressions.extend(exp)
                else:
                    order_expressions.append(exp)
        elif hasattr(self.Meta, "default_order_by"):
            # TODO default order_by should be a key used in the order_by map
            order_expressions = self.Meta.default_order_by
        else:
            order_expressions = [self.Meta.model.id.asc()]

        return query.order_by(*order_expressions)

    def list(self, *args, **kwargs) -> list[T_Model]:
        return self.session.scalars(self.build_list_query(*args, **kwargs)).all()

    def perform_get(self, query, raise_exc: bool = True) -> Optional[T_Model]:
        try:
            return self.session.scalars(query).one()
        except (NoResultFound, MultipleResultsFound) as e:
            if raise_exc:
                raise e.__class__(f"{human_name(self.Meta.model.__name__)} not found")

        return None

    def get_query(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def get(self, *args, raise_exc: bool = True, **kwargs) -> Optional[T_Model]:
        return self.perform_get(self.get_query(*args, **kwargs), raise_exc=raise_exc)

    def paginate(self, *args, pagination: PaginationFilters, **kwargs) -> Pagination:
        query = self.build_list_query(*args, **kwargs)
        items = self.session.scalars(
            query.limit(pagination.per_page).offset(
                (pagination.page - 1) * pagination.per_page
            )
        ).all()
        total = query.options(lazyload("*")).order_by(None).count()

        return Pagination(
            page=pagination.page,
            per_page=pagination.per_page,
            items=items,
            total=total,
        )

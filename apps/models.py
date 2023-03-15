import typing as t
from datetime import datetime

from sqlalchemy import (Boolean, DateTime, Integer,
                        String, func)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Users(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255))

    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.current_timestamp())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

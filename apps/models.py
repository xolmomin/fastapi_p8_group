import enum
import typing as t
from datetime import datetime

from sqlalchemy import (Boolean, DateTime, Enum, ForeignKey, Integer, String,
                        Text, func)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class CreateDateBase:
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 onupdate=func.current_timestamp(),
                                                 nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __str__(self):
        return str(self.id)


class Users(Base, CreateDateBase):
    class Status(enum.Enum):
        CLIENT = "client"
        VIP_CLIENT = "vip_client"
        ADMIN = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    image: Mapped[str] = mapped_column(String(200), nullable=True)
    password: Mapped[str] = mapped_column(String(200))

    status: Mapped[str] = mapped_column(Enum(Status), server_default=Status.CLIENT.name)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    posts: Mapped[list['Post']] = relationship(back_populates='author', lazy='selectin')


class Post(Base, CreateDateBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text())
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    author: Mapped['Users'] = relationship(back_populates='posts')
    image: Mapped[str] = mapped_column(String(255), nullable=True)

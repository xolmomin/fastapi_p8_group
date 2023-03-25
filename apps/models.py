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
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Users(Base):
    class Type(enum.Enum):
        ADMIN = 'admin'
        CLIENT = 'client'
        VIP_CLIENT = 'vip_client'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(Enum(Type), server_default=Type.CLIENT.name)  # TODO change lowercase
    email: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    posts: Mapped[list['Post']] = relationship(back_populates='author', lazy='selectin')
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.current_timestamp())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Post(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text())
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    author: Mapped['Users'] = relationship(back_populates='posts')
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.current_timestamp())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

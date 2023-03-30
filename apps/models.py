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


class BaseCreateDate:
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.current_timestamp())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Users(Base, BaseCreateDate):
    class Type(enum.Enum):
        ADMIN = 'ADMIN'
        CLIENT = 'CLIENT'
        VIP_CLIENT = 'VIP_CLIENT'

    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(Enum(Type), server_default=Type.CLIENT.name)  # TODO change lowercase
    email: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    is_verified_phone: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(255))
    posts: Mapped[list['Post']] = relationship(back_populates='author', lazy='selectin')
    verification: Mapped[list['Verification']] = relationship(back_populates='user', lazy='selectin')


class Post(Base, BaseCreateDate):
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text())
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    author: Mapped['Users'] = relationship(back_populates='posts')
    image: Mapped[str] = mapped_column(String(255), nullable=True)


class Verification(Base):
    class VerifyType(enum.Enum):
        EMAIL = 'EMAIL'
        PHONE = 'PHONE'

    type: Mapped[str] = mapped_column(Enum(VerifyType), server_default=VerifyType.EMAIL.name)
    code: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['Users'] = relationship(back_populates='verification')

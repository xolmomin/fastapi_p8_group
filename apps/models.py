import enum
import typing as t
from datetime import datetime

from sqlalchemy import (Boolean, DateTime, Enum, ForeignKey, Integer, String,
                        Text, func, Column)
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
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100))
    email: str = Column(String(50), unique=True)
    is_active: str = Column(Boolean, default=False)
    password: str = Column(String(255))
    image = Column(String(255))
    updated_at: datetime = Column(DateTime, onupdate=datetime.now)
    created_at: datetime = Column(DateTime, server_default=func.now())

# class Post(Base):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     title: Mapped[str] = mapped_column(String(255))
#     description: Mapped[str] = mapped_column(Text())
#     is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
#     author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
#     author: Mapped['Users'] = relationship(back_populates='posts')
#     image: Mapped[str] = mapped_column(String(255), nullable=True)
#     updated_at: Mapped[datetime] = mapped_column(DateTime,
#                                                  server_default=func.now(),
#                                                  onupdate=func.current_timestamp())
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

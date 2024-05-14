import asyncio

from sqlalchemy import Table, Column, Integer, String, MetaData, text, ForeignKey, Index, DDL, event, PickleType, URL, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data.orm.engine import Base, str_256, str_256_pk
import enum
import datetime
from typing import Optional, Annotated
import pickle
from pydantic import BaseModel, SecretStr


metadata_obj = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, )]
str_512 = Annotated[str, 512]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                        onupdate=datetime.datetime.utcnow,
                                                        )]


class TransactionStatus(enum.Enum):
    COMPLETE = "COMPLETE"
    IN_PROCESS = "IN_PROCESS"
    NOT_STARTED = "NOT_STARTED"

class SteamListings(Base):
    __tablename__ = "listings"

    ts_long = 50
    name: Mapped[str] = mapped_column(primary_key=True, index=True)
    main_gun: Mapped[str_256]
    ref: Mapped[str_512]
    image_small = Column(String(512))
    image_big = Column(String(512))
    time_series_pckl = Column(PickleType)
    ml_weights = Column(LargeBinary)
    time_series_new_val = Column(Integer, index=True)


class SkinId(Base):
    __tablename__ = "skins"

    id: Mapped[intpk]
    owner: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    name_fk: Mapped[str] = mapped_column(ForeignKey("listings.name"))


class Transactions(Base):
    __tablename__ = "transactions"

    self_id: Mapped[intpk]
    gun_id: Mapped[int] = mapped_column(ForeignKey("skins.id", ondelete="CASCADE"))
    owner_to: Mapped[int]
    status: Mapped[TransactionStatus]


class UserPd(BaseModel):
    user_id: int
    password_hash: SecretStr
    mail: str

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[intpk]
    password_hash: Mapped[str_256]
    mail: Mapped[str_256]

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    #loop.run_until_complete()
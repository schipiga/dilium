from collections import namedtuple

from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        Text,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

Base = declarative_base()


class Node(Base):

    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    host_name = Column(String(64), unique=True, nullable=False)
    browsers_config = Column(Text, nullable=False)


class Blocker(Base):

    __tablename__ = 'blockers'

    id = Column(Integer, primary_key=True)
    host_name = Column(String(64), nullable=False)
    browser_name = Column(String(64), nullable=False)
    client_uuid = Column(String(64), nullable=False)
    time_limit = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint('host_name', 'client_uuid'),)


ENGINE = create_engine('sqlite:///' + config.DATABASE,
                       echo=True if config.DEBUG else False)
Base.metadata.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)

TmpBlocker = namedtuple('TmpBlocker', ('host_name',
                                       'browser_name',
                                       'client_uuid',
                                       'time_limit'))
TMP_BLOCKERS = {}

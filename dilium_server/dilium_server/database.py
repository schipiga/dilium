"""
---------------
Dilium database
---------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.from collections import namedtuple

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

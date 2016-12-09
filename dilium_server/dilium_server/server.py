import json
import time
from tornado import web
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Text, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from threading import RLock
from collections import namedtuple

request_lock = RLock()

Base = declarative_base()

DEFAULT = object()


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

engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


tmp_blockers = {}
TmpBlocker = namedtuple(
    'TmpBlocker', ('host_name', 'browser_name', 'client_uuid', 'time_limit'))


def get_client_uuid(headers):
    for key, value in headers.items():
        if key.lower() == 'client-uuid':
            return value


class Main(web.RequestHandler):

    def get(self):
        self.write("Distributed selenium")


class UploadConfig(web.RequestHandler):

    def post(self):
        """Upload config with info about hosts and browser capabilitites to db.

        Args:
            - config: json
        """
        config = json.loads(self.request.body)
        session = Session()
        for host, config in config.items():
            for capability in config['capabilities']:
                capability['maxInstances'] = 1
            node = Node(host_name=host, browsers_config=json.dumps(config))
            session.add(node)
        session.commit()


class RequestHost(web.RequestHandler):

    def get(self):
        desired_capabilities = json.loads(self.request.body)
        client_uuid = get_client_uuid(self.request.headers)
        session = Session()

        with request_lock:

            for key, blocker in tmp_blockers.items():
                if blocker.time_limit < time.time():
                    del tmp_blockers[key]

            for blocker in session.query(Blocker).all():
                if blocker.time_limit < time.time():
                    session.query(Blocker).filter_by(id=blocker.id).delete()
            session.commit()

            available_nodes = []
            for node in session.query(Node).all():
                capabilities = json.loads(node.browsers_config)['capabilities']

                for capability in capabilities:
                    for key, value in desired_capabilities.items():

                        if capability.get(key, DEFAULT) != value:
                            break
                    else:
                        browser_name = capability['browserName']

                        blockers_count = session.query(Blocker).filter_by(
                            host_name=node.host_name,
                            browser_name=browser_name).count()

                        blockers_count += len(
                            [blocker for blocker in tmp_blockers.values()
                             if blocker.host_name == node.host_name
                             and blocker.browser_name == browser_name])

                        max_count = capability['maxInstances']

                        if blockers_count < max_count:
                            available_nodes.append(
                                {'node': node,
                                 'browser_name': browser_name,
                                 'free_count': max_count - blockers_count})

            if not available_nodes:
                self.write_error(500, exc_info='All browsers are busy')
            else:
                available_nodes.sort(
                    key=lambda item: item['free_count'])
                node = available_nodes[0]['node']
                browser_name = available_nodes[0]['browser_name']

                tmp_blockers[node.host_name + client_uuid] = TmpBlocker(
                    host_name=node.host_name,
                    client_uuid=client_uuid,
                    browser_name=browser_name,
                    time_limit=time.time() + 10)

                self.write(node.host_name)


class AcquireHost(web.RequestHandler):

    def post(self):
        client_uuid = get_client_uuid(self.request.headers)
        data = json.loads(self.request.body)
        host_name = data['host']
        duration = int(data['duration'])
        tmp_blocker = tmp_blockers[host_name + client_uuid]

        if tmp_blocker.time_limit < time.time():
            self.write_error(
                500, exc_info="Time to acquire request host is outdated!")
        else:
            session = Session()
            blocker = Blocker(host_name=host_name,
                              client_uuid=client_uuid,
                              browser_name=tmp_blocker.browser_name,
                              time_limit=time.time() + duration)
            session.add(blocker)
            session.commit()
            del tmp_blockers[host_name + client_uuid]


class ReleaseHost(web.RequestHandler):

    def post(self):
        client_uuid = get_client_uuid(self.request.headers)
        data = json.loads(self.request.body)
        host_name = data['host']
        session = Session()
        blocker = session.query(Blocker).filter_by(
            host_name=host_name, client_uuid=client_uuid)
        if blocker.count():
            blocker.delete()
        else:
            self.write_error(500, exc_info='No hosts to release')
        session.commit()


def server():
    return web.Application([
        (r"/", Main),
        (r"/upload-config/", UploadConfig),
        (r"/request-host/", RequestHost),
        (r"/acquire-host/", AcquireHost),
        (r"/release-host/", ReleaseHost),
    ])

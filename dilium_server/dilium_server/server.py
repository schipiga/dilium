import json
from tornado import web
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Text
from sqlalchemy.orm import sessionmaker

tmp_blockers = {}

Base = declarative_base()


class Node(Base):

    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    host = Column(String(64), unique=True, nullable=False)
    capabilities = Column(Text, nullable=False)


class Blocker(Base):

    __tablename__ = 'blockers'

    id = Column(Integer, primary_key=True)
    host = Column(String(64), nullable=False)
    uuid = Column(String(64), nullable=False)
    count = Column(Integer, default=0)

engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class Main(web.RequestHandler):

    def get(self):
        self.write("Distributed selenium")


class UploadConfig(web.RequestHandler):

    def post(self):
        config = json.loads(self.request.body)
        session = Session()
        for host, capabilities in config.items():
            node = Node(host=host, capabilities=json.dumps(capabilities))
            session.add(node)
        session.commit()


class RequestHost(web.RequestHandler):

    def get(self):
        session = Session()
        nodes = session.query(Node).all()
        desired = json.loads(self.request.body)
        for node in nodes:
            cap = json.loads(node.capabilities)
            for key, val in desired.items():
                if cap.get(key, None) != val:
                    break
            else:
                tmp_blockers[node.host] = cap['browserName']
                self.write(node.host)


class AcquireHost(web.RequestHandler):

    def post(self):
        host = self.request.body
        uuid = tmp_blockers.pop(host)
        session = Session()
        blocker = session.query(Blocker).filter_by(host=host, uuid=uuid).first()
        if blocker:
            blocker.count += 1
        else:
            blocker = Blocker(host=host, uuid=uuid, count=1)
            session.add(blocker)
        session.commit()


class ReleaseHost(web.RequestHandler):

    def post(self):
        host, uuid = self.request.body
        session = Session()
        blocker = session.query(Blocker).get(host=host, uuid=uuid)
        blocker.count -= 1
        session.commit()


def server():
    return web.Application([
        (r"/", Main),
        (r"/upload-config/", UploadConfig),
        (r"/request-host/", RequestHost),
        (r"/acquire-host/", AcquireHost),
        (r"/release-host/", ReleaseHost),
    ])

"""
-------------
Dilium server
-------------
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
# under the License.

import json
import threading
import time

from tornado import web

from . import config, database

REQUEST_LOCK = threading.RLock()


def get_client_uuid(headers):
    """Get client UUID from request headers."""
    for key, value in headers.items():
        if key.lower() == config.CLIENT_UUID:
            return value


def cleanup_blockers():
    """Cleanup records about blocked hosts, if their time is expired."""
    for key, blocker in database.TMP_BLOCKERS.items():
        if blocker.time_limit < time.time():
            del database.TMP_BLOCKERS[key]

    session = database.Session()

    for blocker in session.query(database.Blocker).all():
        if blocker.time_limit < time.time():
            session.query(database.Blocker).filter_by(id=blocker.id).delete()

    session.commit()


class Main(web.RequestHandler):

    def get(self):
        self.write("Distributed selenium")


class UploadConfig(web.RequestHandler):

    def post(self):
        """Upload config with info about hosts and browser capabilitites to db.
        """
        hosts_config = json.loads(self.request.body)
        session = database.Session()

        for host, browsers_config in hosts_config.items():

            for capability in browsers_config[config.CAPABILITIES]:
                capability[config.MAX_INSTANCES] = 1

            node = database.Node(host_name=host,
                                 browsers_config=json.dumps(browsers_config))
            session.add(node)

        session.commit()


class RequestHost(web.RequestHandler):

    def get(self):
        """POST-request to request available host."""
        desired_capabilities = json.loads(self.request.body)
        client_uuid = get_client_uuid(self.request.headers)

        with REQUEST_LOCK:
            cleanup_blockers()

            session = database.Session()
            available_nodes = []

            for node in session.query(database.Node).all():
                capabilities = json.loads(
                    node.browsers_config)[config.CAPABILITIES]

                for capability in capabilities:
                    for key, value in desired_capabilities.items():

                        if capability.get(key, config.DEFAULT) != value:
                            break
                    else:
                        browser_name = capability[config.BROWSER_NAME]

                        blockers_count = session.query(
                            database.Blocker).filter_by(
                            host_name=node.host_name,
                            browser_name=browser_name).count()

                        blockers_count += len(
                            [blocker for blocker
                             in database.TMP_BLOCKERS.values()
                             if blocker.host_name == node.host_name
                             and blocker.browser_name == browser_name])

                        max_count = capability[config.MAX_INSTANCES]

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

                database.TMP_BLOCKERS[node.host_name + client_uuid] = \
                    database.TmpBlocker(
                        host_name=node.host_name,
                        client_uuid=client_uuid,
                        browser_name=browser_name,
                        time_limit=time.time() + 10)

                self.write(json.dumps({'host': node.host_name}))


class AcquireHost(web.RequestHandler):

    def post(self):
        """POST-request to acquire requested host."""
        client_uuid = get_client_uuid(self.request.headers)
        host_data = json.loads(self.request.body)

        host_name = host_data['host']
        block_duration = int(host_data['duration'])

        tmp_blocker = database.TMP_BLOCKERS[host_name + client_uuid]
        if tmp_blocker.time_limit < time.time():
            self.write_error(
                500, exc_info="Time to acquire request host is outdated!")

        else:
            session = database.Session()
            blocker = database.Blocker(host_name=host_name,
                                       client_uuid=client_uuid,
                                       browser_name=tmp_blocker.browser_name,
                                       time_limit=time.time() + block_duration)
            session.add(blocker)
            session.commit()
            del database.TMP_BLOCKERS[host_name + client_uuid]
            self.write(json.dumps({'browser': tmp_blocker.browser_name}))


class ReleaseHost(web.RequestHandler):

    def post(self):
        """POST-request to release acquired host."""
        client_uuid = get_client_uuid(self.request.headers)
        data = json.loads(self.request.body)
        host_name = data['host']

        session = database.Session()

        blocker = session.query(database.Blocker).filter_by(
            host_name=host_name, client_uuid=client_uuid)

        if blocker.count():
            blocker.delete()
        else:
            self.write_error(500, exc_info='No hosts to release')

        session.commit()


def server():
    """Create tornado web application.
    """
    return web.Application([
        (r"/", Main),
        (r"/upload-config/", UploadConfig),
        (r"/request-host/", RequestHost),
        (r"/acquire-host/", AcquireHost),
        (r"/release-host/", ReleaseHost),
    ])

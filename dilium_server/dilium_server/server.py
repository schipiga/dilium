from tornado import web


class Main(web.RequestHandler):

    def get(self):
        self.write("Distributed selenium")


class UploadConfig(web.RequestHandler):

    def post(self):
        pass


class RequestHost(web.RequestHandler):

    def get(self):
        pass


class AcquireHost(web.RequestHandler):

    def post(self):
        pass


class ReleaseHost(web.RequestHandler):

    def post(self):
        pass


def server():
    return web.Application([
        (r"/", Main),
        (r"/upload-config", UploadConfig),
        (r"/request-host", RequestHost),
        (r"/acquire-host", AcquireHost),
        (r"/release-host", ReleaseHost),
    ])

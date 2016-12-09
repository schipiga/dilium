import tornado.ioloop

from dilium_server.server import server

if __name__ == "__main__":
    app = server()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

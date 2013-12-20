import tornado.ioloop
import tornado.web
import tornado.gen

from vimeo import VimeoClient

class TestSyncHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Demonstrates synchronous use of VimeoClient

        Caller does not need to be wrapped in a decorator, result is returned synchronously
        """
        vimeo = VimeoClient("YOUR ACCESS TOKEN")
        res = vimeo.users.emmett9001()
        self.write(res)
        self.finish()


class TestCoroutineHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        """
        Demonstrates asynchronous use of VimeoClient via tornado.gen

        The caller must be decorated by tornado.gen.coroutine
        The call to an API function must include the async kwarg set to True
        The result must be yielded before assignment
        """
        vimeo = VimeoClient("YOUR ACCESS TOKEN")
        res = yield vimeo.users(query='cats', async=True)
        self.write(res)
        self.finish()


class TestCallbackHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        """
        Demonstrates asynchronous use of VimeoClient via callback function

        Caller must be wrapped in @tornado.web.asynchronous
        Call to API function must include the callback kwarg
        """
        vimeo = VimeoClient("YOUR ACCESS TOKEN")
        def callback(result):
            self.write(result)
            self.finish()
        vimeo.users.emmett9001(callback=callback)


def get_app():
    application = tornado.web.Application([
        (r"/test_sync", TestSyncHandler),
        (r"/test_coroutine", TestCoroutineHandler),
        (r"/test_callback", TestCallbackHandler),
    ])
    return application

if __name__ == "__main__":
    application = get_app()
    application.listen(5000)
    tornado.ioloop.IOLoop.instance().start()

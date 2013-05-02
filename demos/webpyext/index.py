# -*- coding: utf-8 -*-
"""
    test for webpyext
    ~~~~~~~~~~~~~~~~
    :copyright: 2012 by mental.we8log.com

>>> req = app.request('/ajax/userinfo', method='GET')
>>> req.status
'200 OK'
>>> req.data
"{'user': {'access_key': '', 'id': 1}}"
"""
import os
import logging

logger = logging.getLogger(__name__)

import web

from webpyext.utils import DataRow
from webpyext.webbase import WebBaseHandler, init_session, expose, get_identity
from webpyext import identity

web.config.debug = False

urls = (
        "/", "index",
        "/login", "login",
        "/logout", "logout",
        "/profile", "profile",
        "/ajax/userinfo", "userinfo",
        )

app = web.application(urls, locals())


class DBProvider(identity.IDProvider):
    def do_get_user(self, access_key):
        return DataRow(dict(id=1, access_key=access_key))

    def do_set_user(self, user, userinfo):
        pass

    def get_authuser(self):
        pass


def init_provider(session, fnauth=None):
    def wrapper(handler):
        try:
            return handler()
        except web.HTTPError:
            raise
        except:
            raise
        finally:
            pass
    return wrapper

    
session = init_session(app)
app.add_processor(init_provider(session))


class BaseHandler(WebBaseHandler):
    templates_path = os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/')
    url_base = ""


class index(BaseHandler):
    @expose("index")
    def GET(self):
        return {}


class login(BaseHandler):
    @expose("login")
    def GET(self):
        return {}

    def POST(self):
        web.seeother("/")


class logout(BaseHandler):
    def GET(self):
        web.seeother("/")


class profile(BaseHandler):
    @expose("profile")
    @identity.require_login()
    def GET(self):
        return dict(user=get_identity().user)


class userinfo(BaseHandler):
#    @expose(format="json")
    def GET(self):
        return dict(user=get_identity().user)


from webpyext.logger import initLogger

initLogger({}, 'web')

if __name__ == "__main__":
    import sys
    import doctest
    if sys.argv[-1] == '--test':
        doctest.testmod()
    else:
        app.run()

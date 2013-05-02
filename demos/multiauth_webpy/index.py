import web
from multiauth.auth import GoogleMixin
from multiauth.identity import Identity
from multiauth import auth_webpy

import json
import urllib
import datetime
import calendar
import email.utils

import functools
from sys import stderr
import traceback

web.config.debug = False

urls = (
        "/", "index",
        "/index", "index",
        "/profile", "profile",
        "/login", "login",
        "/logout", "logout"
        )

app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'user_info': None})

class SessProvider:
    def __init__(self, session):
        self.session = session

    def getUser(self):
        return (self.session.user_info != None) and json.loads(self.session.user_info) or None

    def setUser(self, user):
        self.session.user_info=json.dumps(user)

    def redirectLogin(self):
        return web.redirect('/login?redirect=%s' % auth_webpy.CurrentURL())

identity = Identity(SessProvider(session))

class GoogleAuth(auth_webpy.WebappAuth, GoogleMixin):
    pass

class BaseHandler:
    def __init__(self):
        self.render = web.template.render("templates")

class index(BaseHandler):
    def GET(self):
        user = identity.get_user()
        return self.render.index(user=user, current_url=web.ctx.home + web.ctx.fullpath)

class login(BaseHandler):
    def GET(self):
        google_auth = GoogleAuth(self)

        try:
            data = web.input()
            if "openid.mode" in data.keys():
                google_auth.get_authenticated_user(self._on_auth)
                return self.render.redirect(url='/')
            google_auth.authenticate_redirect()
        except auth_webpy.RequestRedirect, e:
            raise web.redirect(e.url)

    def _on_auth(self, user):
        if user:
            identity.set_user(user)

class logout(BaseHandler):
    def GET(self):
        identity.logout()
        raise web.redirect("/")

class profile(BaseHandler):
    @identity.require(identity.not_anonymous())
    def GET(self):
        user = identity.get_user()
        if user != None:
            return self.render.profile(user=user)
        else:
            raise web.redirect("/")

if __name__ == "__main__":
    app.run()


# -*- coding: utf-8 -*-
"""
    user identity for web server
    ~~~~~~~~~~~~~~~~
    :copyright: 2010-12 by mental.we8log.com
"""
import re
import web

from functools import partial

from common.common import DataRow, error_exc
from webcommon import WebUnauthorizedError, WebForbiddenError, WebBaseHandler

import logging

logger = logging.getLogger(__name__)


# requires provider functions:
# do_get_user(access_key), returns DataRow(user)
# do_set_user(cur_user, new_userinfo), returns access_key
# get_authuser(), return DataRow(user)
class IDProvider:
    cookie_expires = 30
    def __init__(self, session, fnauth=None):
        self.session = session
        self.fnauth  = fnauth
        self.user    = None

    def get_session(self, name, defvalue, reset_after_get=False):
        if self.session and name in dir(self.session):
            v = getattr(self.session, name)
            logger.debug("get_session(%s)=%s" % (name, v))
            if reset_after_get:
                setattr(self.session, name, defvalue)
            return v
        return defvalue

    def set_session(self, name, value):
        if self.session:
            setattr(self.session, name, value)

    def get_referer(self):
        r = self.get_session("login_referer", "", True)
        if r == "":
            r = web.ctx.env.get("HTTP_REFERER", "")
        logger.debug("referer_url %s" % r)
        return r

    def get_session_user(self):
        u = self.get_session("user", None)
        return (u!=None) and DataRow(u) or None

    def get_user(self):
        key = web.cookies().get("cookie_key", "")
        if key=="":
            if self.session:
                self.session.user = None
            user = None
        else:
            user = self.get_session_user()
            logger.debug("session user : %s" % user)
            if user==None or user.access_key!=key:
                try:
                    user = self.do_get_user(key)
                except:
                    logger.error("provider get_user fail! error: %s" % error_exc())
                    user = None
                if self.session:
                    self.session.user = user
                key = (user!=None) and user.access_key or ""
                web.setcookie("cookie_key", key, self.cookie_expires*24*3600)
                logger.debug("get_user() set cookie_key %s" % key)
        self.user = user
        return user

    def set_user(self, userinfo):
        user = self.get_session_user()
        user = web.ctx.provider.do_set_user(user, userinfo)
        logger.debug("do_set_user returns: %s" % user)
        if self.session:
            self.session.user = user
        self.user = user
        key = (user!=None) and user.access_key or ""
        web.setcookie("cookie_key", key, self.cookie_expires*24*3600)
        logger.debug("set_user() set cookie_key %s" % key)
        return key

#Auth2.0
#    def get_authuser(self):
#        user = None
#        token = self.fnauth()
#        if token != "":
            # read from db
            #user = web.ctx.provider.get_apiuser(token)
#        return user


#def login(username, userpass):
#    set_user(dict(username=username, userpass=userpass))


def logout():
    set_user(None)


def get_user():
    return web.ctx.provider.get_user()


def set_user(userinfo):
    return web.ctx.provider.set_user(userinfo)


def get_auth_basic():
    try:
        auth_str = web.ctx.env.get('HTTP_AUTHORIZATION', '')
        if auth_str[:6] == 'Basic ':
            return auth_str[6:].decode('base64')
        else:
            return ''
    except:
        return '' 


def get_auth_oauth1():
    pass


def get_auth_oauth2():
    return web.input().get("oauth_token", "")


def get_auth_openid():
    pass


def get_apiuser():
    return web.ctx.provider.get_authuser()


def redirect_login():
    web.ctx.provider.session.login_referer = WebBaseHandler.current_url()
    raise web.seeother(WebBaseHandler.url_base + WebBaseHandler.url_login)


def redirect_error(msg):
    web.ctx.provider.session.last_error = msg
    raise web.seeother(WebBaseHandler.url_base + WebBaseHandler.url_error)


def raise_error(err):
    raise err


def require(fncheck):
    def req_wrapper(fn):
        def wrapper(*args, **kwargs):
            fncheck(fn, *args, **kwargs)
            return fn(*args, **kwargs)
        return wrapper
    return req_wrapper


def has_permission(fn_get_user, fn_not_login, fn_error, fnperm):
    def wrapper(fn, *args, **kwargs):
        arglist = {}
        arglen = len(fn.__code__.co_varnames)
        for index, arg in enumerate(args):
            if index < arglen:
                arglist[fn.__code__.co_varnames[index]] = arg
        arglist.update(kwargs)
        obj = arglist.pop('self')
        user = fn_get_user()
        if user==None:  # no user, no permission, redirect login
            fn_not_login()
        checked = fnperm(user, obj.__class__.__name__, fn.__name__, arglist)
        if not checked:
            fn_error()
        return checked
    return wrapper


def not_anonymous(fn_get_user, fn_not_login, fn_checker=None):
    def wrapper(fn, *args, **kwargs):
        checked = (fn_get_user()!=None) and ((fn_checker==None) or (fn_checker(fn_get_user())))
        if not checked:
            if fn_get_user()!=None:
                logout()
            fn_not_login()
        return checked
    return wrapper


def require_login(fn_checker=None):
    return require(not_anonymous(get_user, redirect_login, fn_checker))


def requre_perm(fnperm):
    return require(has_permission(get_user, redirect_login, partial(redirect_error, "Permission deny!"), fnperm))


def api_auth(fn_checker=None):
    return require(not_anonymous(get_apiuser, partial(raise_error, WebUnauthorizedError), fn_checker))


def api_perm(fnperm):
    return require(has_permission(get_apiuser, partial(raise_error, WebUnauthorizedError), partial(raise_error, WebForbiddenError), fnperm))


def and_(*fnperms):
    def wrapper(user, cname, fname, arglist):
        r = True
        for fn in fnperms:
            r = r and fn(user, cname, fname, arglist)
        return r
    return wrapper


def or_(*fnperms):
    def wrapper(user, cname, fname, arglist):
        r = False
        for fn in fnperms:
            r = r or fn(user, cname, fname, arglist)
        return r
    return wrapper

# -*- coding: utf-8 -*-
"""
    webma.auth_webpy
    ~~~~~~~~~~~~~~~~

    HTTP client, RequestAdapter, RequestRedirect, WebappAuth.

    :copyright: 2010 by raptor.zh@gmail.com.
    :license: Apache License Version 2.0. See LICENSE.txt for more details.
"""
import web
import httpclient

try:
    import json
except ImportError:
    import simplejson as json
import urllib
import datetime
import calendar
import email.utils
import functools


class RequestAdapter(object):
    def __init__(self, request):
        self.arguments = {}
        args = dict(web.input())
        for k in args.keys():
            self.arguments.setdefault(k, []).append(args[k])

        self.full_url = lambda: web.ctx.home + web.ctx.fullpath
        self.host     = web.ctx.host
        self.path     = web.ctx.homepath + web.ctx.path
        self.home     = web.ctx.home


class RequestRedirect(Exception):
    def __init__(self, url):
        Exception.__init__(self)
        self.url = url


class WebappAuth(object):
    def __init__(self, handler, **kwargs):
        self.request = RequestAdapter(web.ctx)
        self.settings = kwargs
        self._request = web.input()

    def getHTTPClient(self):
        return httpclient.HTTPClient()

    def require_setting(name, feature='this feature'):
        if not self.settings.get(name):
            raise Exception('You must define the "%s" setting in your '
                'application to use %s' % (name, feature))

    def async_callback(self, callback, *args, **kwargs):
        if callback is None:
            return None

        if args or kwargs:
            callback = functools.partial(callback, *args, **kwargs)

        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except Exception, e:
                # for debug
                import traceback
                traceback.print_exc()

        return wrapper

    def redirect(self, url):
        raise RequestRedirect(url)

    _ARG_DEFAULT = []
    def get_argument(self, name, default=_ARG_DEFAULT, strip=True):
        if name in self._request.keys():
            value = self._request[name]
        else:
            value = default
        if value is self._ARG_DEFAULT:
            raise HttpException('Missing request argument %s' % name)

        if strip:
            value = value.strip()

        return value

    def get_cookie(self, name, default=None):
        cookie = web.cookies().get(name)
        if cookie is None:
            return default
        return str(base64.b64decode(cookie))

    def set_cookie(self, name, value, domain=None, expires=None, path='/',
                   expires_days=None):
        if expires_days is not None and not expires:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                days=expires_days)

        cookie = str(base64.b64encode(value))

        if expires:
            timestamp = calendar.timegm(expires.utctimetuple())
            expires = email.utils.formatdate(timestamp, localtime=False,
                usegmt=True)

        web.setcookie(name, cookie, expires, domain)

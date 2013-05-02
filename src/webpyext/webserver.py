# -*- coding: utf-8 -*-
"""
    web base for web.py
    ~~~~~~~~~~~~~~~~
    :copyright: 2010-12 by mental.we8log.com
"""
import re
import copy
import urllib
import web
from web.contrib.template import render_mako

from common.common import DataRow
from webcommon import WebBasehandler

import logging

logger = logging.getLogger(__name__)


def init_session(appmain, dburi=""):
    def _parse_db_args(dburi):
        patDbUrl = re.compile('([^:]*)://([^/]*)/(.+)')
        patDbDbn = re.compile('([^\+]+)\+?(.*)')
        listDbns = {'postgresql': 'postgres'}
        patDbLogin = re.compile('([^:@]+):([^@]+)@([^:]+):?([0-9]*)')

        d = {'host': '', 'port': '', 'db': '', 'user': '', 'pw': '', 'dbn': ''}
        s = ""
        m = patDbUrl.findall(dburi)
        args = {}
        if len(m) == 1:
            dbn, s, d['db'] = m[0]
        if dbn != "":
            m = patDbDbn.findall(dbn)
            if len(m) == 1:
                dbn, drv = m[0]
                args['dbn'] = listDbns.get(dbn, dbn)
        if s != "":
            m = patDbLogin.findall(s)
            if len(m) == 1:
                d['user'], d['pw'], d['host'], d['port'] = m[0]
        [args.__setitem__(k,v) for k,v in d.iteritems() if v != '']
        return args

    default_session_data = {'login_referer': "", 'login_referer': "", 'user': None, 'error_msg': ""}

    if dburi == "":
        store = web.session.DiskStore('sessions')
    else:
        args = _parse_db_args(dburi)
        db = web.database(**args)
        store = web.session.DBStore(db, 'sessions')
    return web.session.Session(appmain, store, initializer=default_session_data)


class PageNavigator(DataRow):
    def __init__(self, index, count, url, args={}):
        DataRow.__init__(self, indict=dict(index=index, count=count, url=url, args=args))

    def page_url(self, p=None):
        args = copy.copy(self.args)
        if p!=None:
            args["p"] = str(p)
        return "%s?%s" % (self.url, urllib.urlencode(args))


class HtmlBaseHandler(WebBaseHandler):
    templates_path = 'templates'
    url_base  = '/'

    def __init__(self):
        self.mako_render = render_mako(
            directories=[self.templates_path, ],
            input_encoding='utf-8',
            output_encoding='utf-8'
        )
        self.kw = web.input()  # remove for test

    def html_render(self, page, data):
        web.header('Content-Type', 'text/html;charset=utf-8')
        return getattr(self.mako_render, page)(**data)

    # user, last_error, extra_data
    def get_identity(self):
        if "session" in dir(web.ctx.provider):
            extra_data = None
            if "extra_data" in dir(web.ctx.provider):
                extra_data = web.ctx.provider.extra_data
            return DataRow(dict(
                user=web.ctx.provider.get_user(),
                last_error=web.ctx.provider.get_session("last_error", "", True),
                extra_data=extra_data,
            ))
        else:
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import unittest

    class TestWebBase(unittest.TestCase):
        def ntestPageNavigator(self):
            pn = PageNavigator(1, 5, "http://localhost/", dict(k1="v1", k2="v2"))
            print pn.page_url(3)

    unittest.main()

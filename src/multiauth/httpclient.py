# -*- coding: utf-8 -*-
"""
    webma.httpclient
    ~~~~~~~~~~~~~~~~

    HTTP client use urllib.urlopen.

    :copyright: 2010 by raptor.zh@gmail.com.
    :license: Apache License Version 2.0. See LICENSE.txt for more details.
"""
import urllib2
import logging

logger = logging.getLogger(__name__)

class HttpResponseError(object):
    """A dummy response used when urlfetch raises an exception."""
    code = 404
    body = '404 Not Found'
    error = 'Error 404'

class FetchResult:
    pass

class HTTPClient(object):
    def fetch(self, url, callback, **kwargs):
        result = FetchResult()
#        logger.debug(url)
        try:
            f = urllib2.urlopen(url)
            result.status_code = 200
            result.content = f.read()
            f.close()
        except urllib2.HTTPError, e:
            result.status_code = 500
            result.content = ""
        try:
            code = result.status_code
            result.body = result.content
            if code < 200 or code >=300:
                result.error = "Error %" % code
            else:
                result.error = None
        except urlfetch.DownloadError, e:
            result = HttpResponseError()
        try:
            args = (result,)
            return callback(*args)
        except Exception, e:
            logger.error("Exception during callback")

#if __name__ == "__main__":
#    def wrapper(*args):
#        print args[0].status_code, args[0].body
#    http = HTTPClient()
#    http.fetch("http://www.baidu.com", wrapper)


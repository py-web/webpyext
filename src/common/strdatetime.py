#coding=utf-8
'''
    string datetime utilities
    ~~~~~~~~~~~~~~~~

    :copyright: 2010-12 by mental.we8log.com
'''

from datetime import datetime, timedelta
#import time
#from feedparser import _parse_date

__fmtDateTime = "%Y%m%d%H%M%S"


def dt2str(dt):
    return (dt != None) and dt.strftime(__fmtDateTime) or ""

def str2dt(s):
    if (s != None) and (len(s) > 15 or len(s) in [8,10,12,14]):
        return datetime.strptime(s, __fmtDateTime[:len(s)-2])
    else:
        return None

def nowstr():
    return dt2str(datetime.now())

def time2dt(t):
    return (t != None) and datetime(*(t[0:6])) or datetime.now()

#def time2str(t):
#    return (t != None) and time.strftime(__fmtDateTime, t) or None

#def strtime2str(s, tz=8):
#    return (s != None and s != '') and dt2str(datetime(*(_parse_date(s)[:6]))+timedelta(seconds=tz*3600)) or ""

#def datetime2float(self, dt):
#    tm=None
#    if dt:
#        tm=time.mktime(dt.timetuple())
#    return tm

#def float2datetime(self, fl):
#    return time2datetime(time.localtime(fl))


if __name__ == "__main__":
    import unittest

    class TestUtils(unittest.TestCase):
        def testDt2str(self):
            self.assertEqual(dt2str(None), "")
            self.assertEqual(dt2str(datetime(2012, 5, 12, 14, 28)), "20120512142800")

        def testStr2dt(self):
            self.assertEqual(str2dt(""), None)
            self.assertEqual(str2dt("2012"), None)
            self.assertEqual(str2dt("20120512"), datetime(2012, 5, 12))
            self.assertEqual(str2dt("201205121"), None)
            self.assertEqual(str2dt("201205121428"), datetime(2012, 5, 12, 14, 28))
            #self.assertRaises(ValueError, str2dt("abcdefgh"))


    unittest.main()

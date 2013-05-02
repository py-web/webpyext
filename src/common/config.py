#coding=utf-8
'''
这里定义机器人需要用到的工具类和函数
@author: 令狐虫
@date: 20080410

Init logger from config
@author: raptor
@date: 2010-2013
'''
import logging

def initLogger(conf, appname=""):
    logconf = {}
    try:
        logconf['filename'] = conf[appname+'.logger.file']
        logconf['filemode'] = conf.get(appname+'.logger.mode', 'w')
    except KeyError:
        pass
    try:
        logconf['format'] = conf[appname+'.logger.format']
    except KeyError:
        logconf['format'] = '%(asctime)s %(name)s %(levelname)s %(message)s'
    LEVELS = {  'debug'   : logging.DEBUG,
                'info'    : logging.INFO,
                'warning' : logging.WARNING,
                'error'   : logging.ERROR,
                'critical': logging.CRITICAL}
    try:
        logconf['level'] = LEVELS[conf[appname+'.logger.level']]
    except KeyError:
        logconf['level'] = logging.NOTSET
    logging.basicConfig(**logconf)

class EBadConfigureLine:
    '''
    错误的配置行异常类
    '''
    def __init__(self, line):
        self.line = line

    def __str__(self):
        return "EBadConfigureLine: %s" % line

class Configure(dict):
    """
    简单的配置文件解析类。将一个配置文件转换成字典
    仅支持单行注释，不支持代码混合注释
    """
    COMMENT_STARTER = '#'

    def __init__(self, filename):
        '''
        构造函数
        @param filename: 配置文件名
        '''
        dict.__init__(self)
        self.filename = filename
        self._parse()

    def _isComment(self, line):
        '''
        判断某行是否注释
        @param line: 需要判断的行
        @return: 如果是注释返回True，否则返回False
        '''
        return (len(line.strip()) == 0) or (line.strip().startswith(Configure.COMMENT_STARTER))

    def _getKeyValue(self, line):
        '''
        对于不是注释的行，返回key,value对
        @param line: 需要处理的行
        @return: key, value对
        @raise EBadConfigureLine: 解析配置失败
        '''
        line = line.strip()
        index = line.find('=')
        #-1表示没有找到，0表示没有key
        if index == -1 or index == 0:
            raise EBadConfigureLine(line)

        key = line[:index].strip()
        value = line[index+1:].strip()
        return key, value

    def _parse(self):
        """
        解析配置文件，将内容存放到内部的一个dict中
        """
        for line in open(self.filename):
            if not self._isComment(line):
                key, value = self._getKeyValue(line)
                self.__setitem__(key, value)


conf = None

if __name__ == "__main__":
    import unittest

    class TestConfigure(unittest.TestCase):
        def setUp(self):
            self.config = Configure('test.conf')

        def tearDown(self):
            del self.config

        def testIsComment(self):
            self.assertEqual(self.config._isComment('#This is a comment'), True)
            self.assertEqual(self.config._isComment('This is not a comment'), False)
            self.assertEqual(self.config._isComment(''), False)

        def testGetKeyValue(self):
            key, value = self.config._getKeyValue("aaa=bbb")
            self.assertEqual((key,value), ("aaa", "bbb"))

            key, value = self.config._getKeyValue("aaa=bbb=ccc")
            self.assertEqual((key,value), ("aaa", "bbb=ccc"))

            key, value = self.config._getKeyValue(" aaa =    bbb ")
            self.assertEqual((key,value), ("aaa", "bbb"))

            key, value = self.config._getKeyValue("aaa =")
            self.assertEqual((key,value), ("aaa", ""))

            key, value = self.config._getKeyValue("aaa =      ")
            self.assertEqual((key,value), ("aaa", ""))

            self.assertRaises(EBadConfigureLine, self.config._getKeyValue, "abc")
            self.assertRaises(EBadConfigureLine, self.config._getKeyValue, "=abc")
            self.assertRaises(EBadConfigureLine, self.config._getKeyValue, "=")
            self.assertRaises(EBadConfigureLine, self.config._getKeyValue, "")
        def testGetItem(self):
            self.assertEqual(self.config['sqlalchemy.url'], "mysql://g4p:g4prpwt@localhost/g4p?use_unicode=0&charset=utf8")
            self.assertEqual(self.config['sqlalchemy.encoding'], "'utf-8'")
            self.assertEqual(self.config['sqlalchemy.convert_unicode'], "True")

            try:
                dummy = self.config['not existed']
            except KeyError:
                pass
            else:
                raise self.failureException('KeyValue exception should be raised')

    unittest.main()


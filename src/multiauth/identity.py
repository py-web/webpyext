# -*- coding: utf-8 -*-
"""
    webma.identity
    ~~~~~~~~~~~~~~~~

    user identity.

    :copyright: 2010 by raptor.zh@gmail.com.
"""
class Identity:
    def __init__(self, provider):
        self.provider = provider

    def logout(self):
        self.provider.setUser(None)

    def get_user(self):
        return self.provider.getUser()

    def set_user(self, user):
        self.provider.setUser(user)

    def require(self, cond):
        def req_wrapper(fn):
            def wrapper(*args, **kwargs):
                if cond():
                    return fn(*args, **kwargs)
                else:
                    raise self.provider.redirectLogin()
            return wrapper
        return req_wrapper

    def not_anonymous(self):
        return lambda : self.provider.getUser() != None

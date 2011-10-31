#!/usr/bin/env python
#-*- coding: utf-8 -*-



##
## backend.py - analyze_dossier
## copyright (c) 2009-2010 Koninklijke Bibliotheek - National library of the Netherlands.
##
## this program is free software: you can redistribute it and/or modify
## it under the terms of the gnu general public license as published by
## the free software foundation, either version 3 of the license, or
## (at your option) any later version.
##
## this program is distributed in the hope that it will be useful,
## but without any warranty; without even the implied warranty of
## merchantability or fitness for a particular purpose. see the
## gnu general public license for more details.
##
## you should have received a copy of the gnu general public license
## along with this program. if not, see <http://www.gnu.org/licenses/>.
##



import os
import sys
import time
import logging
import urllib2
import tempfile
import simplejson

from pprint import pprint

def log(message, log_level = logging.CRITICAL):
    logging.log(log_level, message)
    pass


class Storage():
    data = {}
    def __init__(self):
        pass

    def get(self, key):
        log("Getting %s via backend : %s" % (key, self.__class__.__name__))
        if key in self.data:
            log("Got %s via backend : %s" % (key, self.__class__.__name__))
            return(self.data[key])
        else:
            log("No data for %s via backend : %s" % (key, self.__class__.__name__))
            return(False)
    
    def store(self, key, data=data):
        if not key in self.data:
            self.data[key] = data
            log("Storing %s via backend : %s" % (key, self.__class__.__name__))
        return(True)

class Files(Storage):
    def __init__(self):
        pass

class Pickle(Storage):
    def __init__(self):
        pass
    
class backend(object):
    prefered_backends = "pymongo", "couchdb", "sqlite3", "memcache", "pickle", "files"
    current_backend = False
    settings = { "tmp_path" : tempfile.gettempdir()+os.sep+"lod"+os.sep,
                 "hostname" : None,
                 "portname" : None }

    def __init__(self, func, *arg, **narg):
        self.func = func
        for backend in self.prefered_backends:
            try:
                module = __import__(backend)
                try:
                    if getattr(sys.modules[__name__], backend.title()):
                        setattr(sys.modules[__name__], backend, module)
                        self.current_backend = getattr(sys.modules[__name__], backend.title())()
                        log("Setting backend to %s" % backend)
                        break
                except AttributeError:
                    log("Backend %s not implemented yet" % backend)
            except ImportError:
                log("Module %s not found on this system" % backend)

        if self.current_backend == False:
            log("Falling back to native file backend")
            self.current_backend = getattr(sys.modules[__name__],  self.prefered_backends[-1].title())()
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)
        else:
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)

    def __repr__(self):
        return("Selected backend : %s " % self.current_backend)

    def __call__(self, *args, **nargs):
        data = self.get(*args)
        if not data:
            data = self.func(*args)
            self.store(*args, data=data)
            return(data)
        else:
            return(data)
    
@backend
def test(item):
    return("")

print test('appel')
print test('pruim')
print test('appel')

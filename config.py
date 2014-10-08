#!/usr/bin/env python
# -*- coding:Utf-8 -*-

"""
Footprint dynamic configuration.
"""

#: No automatic export
__all__ = []

import logging
logger = logging.getLogger('footprints.config')

from . import dump, reporting, util


# Module interface

def get(**kw):
    """Return actual setup object matching description."""
    return FootprintSetup(**kw)

def add2proxies(c, **kw):
    """
    Add to default or specified setup object (according to ``kw`` and its ``tag`` value)
    the current collector ``c`` as a reference to existing proxies.
    """
    setup = FootprintSetup(**kw)
    for p in setup.proxies:
        setattr(p, c.tag, c.load)
        setattr(p, c.tag + 's', c)


# Base class

class FootprintSetup(util.GetByTag):
    """Defines some defaults and external tools."""

    def __init__(self, docstrings=True, extended=True, fastmode=False, fatal=True, shortnames=False,
                 fastkeys=('kind',), callback=None, defaults=None, proxies=None,
                 report=True, nullreport=reporting.NullReport()):
        """Initialisation of a simple footprint setup driver."""
        self._extended  = bool(extended)
        self.docstrings = bool(docstrings)
        self.shortnames = bool(shortnames)
        self.fatal      = bool(fatal)
        self.report     = bool(report)
        self.nullreport = nullreport
        self.fastmode   = bool(fastmode)
        self.fastkeys   = tuple(fastkeys)
        self.callback   = callback
        if proxies is None:
            self.proxies = set()
        else:
            self.proxies = set(proxies)
        self._defaults  = util.LowerCaseDict()
        if defaults is not None:
            self._defaults.update(defaults)
            logger.warning('New FootprintSetup')
            print 'DEBUG', kw

    def __call__(self, **kw):
        if kw:
            initvalues = self.as_dict()
            initvalues.update(kw)
            thesetup = self.__class__(**initvalues)
        else:
            thesetup = self
        thesetup.info()
        return thesetup

    def as_dict(self):
        """Return a standalone dictionary or current setup attributes."""
        return dict([ (k.lstrip('_'), v) for k, v in self.__dict__.items() ])

    def info(self):
        """Summuray of actual settings."""
        for k, v in sorted(self.as_dict().items()):
            print k.ljust(12), ':', v

    def add_proxy(self, obj, clear=False):
        """
        Populate an ``obj`` with references to active collectors and load methods
        so that it could behave like a static proxy.
        """
        if isinstance(obj, object):
            from . import collectors
            self.proxies.add(obj)
            for k, v in collectors.items():
                if clear or not hasattr(obj, k):
                    setattr(obj, k, v.load)
                if clear or not hasattr(obj, k+'s'):
                    setattr(obj, k + 's', v)
        else:
            logger.error('Could not populate a non-module or non-instance object: %s', obj)
            raise ValueError('Not a module nor an object instance: %s', obj)

    def _get_defaults(self):
        """Property getter for footprints defaults."""
        return self._defaults

    def _set_defaults(self, *args, **kw):
        """Property setter for current defaults environnement of the footprint resolution."""
        self._defaults = util.LowerCaseDict()
        self._defaults.update(*args, **kw)

    defaults = property(_get_defaults, _set_defaults)

    def _get_extended(self):
        """Property getter to ``extended`` switch."""
        return self._extended

    def _set_extended(self, switch):
        """Property setter to ``extended`` mode for footprint defaults."""
        if switch is not None:
            self._extended = bool(switch)

    extended = property(_get_extended, _set_extended)

    def extras(self):
        if self.callback:
            cb = self.callback
            return cb()
        else:
            return dict()

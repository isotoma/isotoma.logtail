
from twisted.python import log

import inotify
import stat
import os

logheader = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
    <title>{{ pageTitle }}</title>
    <link rel="stylesheet" href="/default.css" type="text/css" />
  </head>
  <body class='log'>
  <pre>
"""


class TailService(object):

    def __init__(self, request, filename, delay=1):
        self.request = request
        self.filename = filename
        self.delay = delay
        self.fp = None
        self.stat = None
        self.finished = False
        self.inotify = False

    def start(self):
        log.msg("Starting tail of '%s'" % self.filename)
        self.request.write(logheader)
        self._open()
        self._tail()

        if inotify:
            self.inotify = inotify.INotify()
            self.inotify.startReading()
            self.inotify.watch(filepath.FilePath(self.filename), callbacks=[self._inotify_cb])

    def stop(self):
        log.msg("Stopping tail of '%s'" % self.filename)
        self.finished = True

        if self.inotify:
            self.inotify.stopReading()
            self.inotify = None

    def _stat(self):
        s = os.stat(self.filename)
        return (s[stat.ST_DEV], s[stat.ST_INO])

    def _open(self):
        self.fp = open(self.filename)
        self.stat = self._stat()

    def _inotify_cb(self, ignored, filepath, mask):
        self._tail()

    def _tail(self):
        data = self.fp.read()
        if data:
            self.dataReceived(data)

        if self.stat != self._stat():
            log.msg("Repopening '%s'" % self.filename)
            self._open()

        if not inotify and not self.finished:
            reactor.callLater(self.delay, self._tail)

    def dataReceived(self, data):
        if not self.finished:
            self.request.write(data)

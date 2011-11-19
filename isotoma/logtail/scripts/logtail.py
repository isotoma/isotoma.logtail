
from twisted.scripts.twistd import run as twistd_run
from twisted.python.util import sibpath
import sys
import os
import yay

def usage():
    print >>sys.stderr, "Usage: logtail stop | start"

def run(config_filename):
    if len(sys.argv) != 2:
        usage()
        return 255
    config = yay.load(open(config_filename).read())
    pidfile = config['pidfile']
    logfile = config['logfile']
    command = sys.argv[1]
    if command == "start":
        # we pass arguments through to the tac file using the environment
        # because there is no other option
        os.environ["LOGTAIL_CONFIG_FILENAME"] = config_filename
        sys.argv[1:] = [
            '-y', sibpath(__file__, "logtail.tac"),
            '--pidfile', pidfile,
            '--logfile', logfile,
        ]
        twistd_run()
    elif command == "stop":
        try:
            pid = int(open(pidfile).read())
        except IOError:
            print "Logtail is not running"
            return 255
        os.kill(pid, 15)
    else:
        usage()
        return 255


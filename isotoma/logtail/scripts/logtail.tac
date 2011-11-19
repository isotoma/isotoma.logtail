from twisted.application import service, internet
from nevow import appserver

from isotoma.logtail import web, config

import os
import yay

config_filename = os.environ["LOGTAIL_CONFIG_FILENAME"]

# module level global used for all config
config.config = yay.load(open(config_filename).read())

application = service.Application("logtail")
site = appserver.NevowSite(web.Root())
web_server = internet.TCPServer(int(config.config['port']), site)
web_server.setServiceParent(application)

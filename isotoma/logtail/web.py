
from twisted.python.util import sibpath
from nevow import rend
from nevow import loaders

import os

from isotoma.logtail import config

templates = sibpath(__file__, "templates")

template = lambda x: loaders.xmlfile(os.path.join(templates, x))

class Root(rend.Page):
    addSlash = True
    docFactory = template("index.html")


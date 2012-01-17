
from zope.interface import implements
from twisted.python.util import sibpath
from nevow import rend, loaders, guard, inevow, tags
from twisted.cred import checkers, portal, credentials
from twisted.web.server import NOT_DONE_YET

import crypt
import os

from isotoma.logtail import config
from isotoma.logtail.tailer import TailService

templates = sibpath(__file__, "templates")

template = lambda x: loaders.xmlfile(os.path.join(templates, x))


class TailResource(rend.Page):

    contentType = "text/plain"

    def __init__(self, logfile):
        rend.Page.__init__(self)
        self.logfile = logfile

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        if not os.path.exists(self.logfile):
            return "Path '%s' does not exist" % self.logfile

        tail = TailService(request, self.logfile)
        tail.start()

        request.notifyFinish().addErrback(self._response_failed, tail)
        return NOT_DONE_YET

    def _response_failed(self, err, tail):
        tail.stop()

class AnonymousRoot(rend.Page):
    addSlash = True
    docFactory = loaders.stan(
    tags.html[
        tags.head[tags.title["Not Logged In"]],
        tags.body[
            tags.form(action=guard.LOGIN_AVATAR, method='post')[
                tags.table[
                    tags.tr[
                        tags.td[ "Username:" ],
                        tags.td[ tags.input(type='text',name='username') ],
                    ],
                    tags.tr[
                        tags.td[ "Password:" ],
                        tags.td[ tags.input(type='password',name='password') ],
                    ]
                ],
                tags.input(type='submit'),
                tags.p,
            ]
        ]
    ])

def no_logout():
    return None

class MyRealm:
    """ A simple realm, that returns the appropriate root resource """

    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is inevow.IResource:
                # do web stuff
                if avatarId is checkers.ANONYMOUS:
                    resc = AnonymousRoot()
                    resc.realm = self
                    return (inevow.IResource, resc, no_logout)
                else:
                    resc = Root()
                    resc.realm = self
                    return (inevow.IResource, resc, resc.logout)

        raise NotImplementedError("Can't support that interface.")

class File(rend.Page):

    def childFactory(self, ctx, segment):
        f = config.config['tail'].get(segment, None)
        if f is None:
            return 404
        return TailResource(f['path'])

class Root(rend.Page):
    addSlash = True
    docFactory = template("index.html")
    child_file = File()

    def data_files(self, ctx, data):
        for k, v in config.config['tail'].items():
            name = v.get('name', k)
            yield {
                'id': k,
                'name': name,
                'path': v['path'],
                }

    def render_file(self, ctx, data):
        return ctx.tag[tags.a(href='/file/%s' % data['id'])[data['name']]]

    def logout(self):
        return


def create_resource():
    realm = MyRealm()
    p = portal.Portal(realm)
    p.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
    p.registerChecker(checkers.FilePasswordDB(
        config.config['htpasswd'],
        hash=lambda u, passwd, stored: crypt.crypt(passwd, stored[:2])
    ))
    res = guard.SessionWrapper(p)
    return res




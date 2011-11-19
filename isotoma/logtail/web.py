
from zope.interface import implements
from twisted.python.util import sibpath
from nevow import rend, loaders, guard, inevow, tags
from twisted.cred import checkers, portal, credentials

import crypt
import os

from isotoma.logtail import config

templates = sibpath(__file__, "templates")

template = lambda x: loaders.xmlfile(os.path.join(templates, x))

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
                    return (inevow.IResource, resc, no_l1ogout)
                else:
                    resc = Root()
                    resc.realm = self
                    return (inevow.IResource, resc, resc.logout)

        raise NotImplementedError("Can't support that interface.")


class Root(rend.Page):
    addSlash = True
    docFactory = template("index.html")

    def __init__(self):
        rend.Page.__init__(self)

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




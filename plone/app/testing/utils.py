# -*- coding: utf-8 -*-
from persistent.list import PersistentList
from Products.MailHost.MailHost import _mungeHeaders
from Products.MailHost.MailHost import MailBase


class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.
    """

    def __init__(self, id):
        self.reset()

    def reset(self):
        self.messages = PersistentList()

    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """
        self.messages.append(messageText)

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self.messages.append(messageText)

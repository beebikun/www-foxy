class BgException(Exception):
    def __init__(self, msg=None, reason=None):
        self.reason = reason
        if reason:
            msg = '%s: \n %s' % (msg, reason)
        super(Exception, self).__init__(msg)


class LoginException(BgException):
    def __init__(self, reason=None):
        msg = 'Failed to login into bg'
        self.reason = reason
        super(BgException, self).__init__(msg, reason)

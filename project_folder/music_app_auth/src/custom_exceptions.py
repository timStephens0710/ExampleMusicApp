class EmailNotFound(Exception):
    """ Raises an error when the email the user has entered is incorrect. """
    def __init__(self, user=None, message = "We couldn't find this email address. Please double check and try again."):
        self.user = user
        self.message = message
        super().__init__(self.message)


class UnverifiedEmail(Exception):
    """ Raises an error when the email has not been verified by the user. """
    def __init__(self, user, message = "Please verify your email address before tyring to login."):
        self.user = user
        self.message = message
        super().__init__(self.message)


class IncorrectPassword(Exception):
    """ Raises an error when the password entered is incorrect. """
    def __init__(self, user, message = "The password you have entered is incorrect. Please try again.."):
        self.user = user
        self.message = message
        super().__init__(self.message)

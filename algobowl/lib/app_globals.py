"""The application's Globals object"""

import tg
from cryptography.fernet import Fernet

__all__ = ["Globals"]


class Globals:
    """
    Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the ``app_globals`` variable.
    """

    def __init__(self):
        self.fernet = Fernet(tg.config["fernet.key"])

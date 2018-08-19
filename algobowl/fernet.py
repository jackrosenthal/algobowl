from cryptography.fernet import Fernet
__all__ = ('fernet', )


class FernetProxy:
    def __init__(self):
        self._fernet = None

    def init_app(self, app):
        key = app.config.get('FERNET_KEY')
        if not key:
            key = Fernet.generate_key()
        self._fernet = Fernet(key)

    def __getattr__(self, name):
        return getattr(self._fernet, name)


fernet = FernetProxy()

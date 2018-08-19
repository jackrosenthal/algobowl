class DefaultConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///devdata.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTH_TYPE = 'MPAPI'
    MPAPI_URL = 'https://mastergo.mines.edu/mpapi'

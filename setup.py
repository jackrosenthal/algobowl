import sys
from setuptools import setup

if sys.version_info < (3, 4):
    print('AlgoBOWL requires at least Python 3.4', file=sys.stderr)
    sys.exit(1)

setup(
    name='algobowl',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    packages=['algobowl'],
    install_requires=[
        "TurboGears2 >= 2.3.12",
        "Beaker >= 1.8.0",
        "Kajiki >= 0.6.3",
        "zope.sqlalchemy >= 0.4",
        "sqlalchemy",
        "alembic",
        "repoze.who",
        "WebHelpers2"],
    python_requires='>=3.4,<4',
    include_package_data=True,
    package_data={'algobowl': [
        'templates/*/*',
        'public/*/*'
    ]},
    entry_points={
        'paste.app_factory': [
            'main = algobowl.config.middleware:make_app'
        ],
        'gearbox.plugins': [
            'turbogears-devtools = tg.devtools'
        ]
    }
)

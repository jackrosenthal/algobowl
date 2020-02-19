import sys
from setuptools import setup

if sys.version_info < (3, 5):
    print('AlgoBOWL requires at least Python 3.5', file=sys.stderr)
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
        "tgext.admin",
        "decorator",
        "tw2.forms",
        "Beaker >= 1.8.0",
        "Kajiki >= 0.6.3",
        "filedepot >= 0.6.0",
        "zope.sqlalchemy >= 1.2",
        "sqlalchemy",
        "alembic",
        "repoze.who",
        "WebHelpers2",
        "recordclass"],
    python_requires='>=3.5,<4',
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

import setuptools

setuptools.setup(
    name='algobowl',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    packages=setuptools.find_packages(),
    install_requires=[
        "TurboGears2 >= 2.3.12",
        "tgext.admin",
        "decorator",
        "google-api-python-client",
        "google-auth-oauthlib",
        "tw2.forms",
        "Beaker >= 1.8.0",
        "Kajiki >= 0.6.3",
        "filedepot >= 0.6.0",
        "zope.sqlalchemy >= 1.2",
        "sqlalchemy>=1.3,<1.4",
        "alembic",
        "repoze.who",
        "WebHelpers2",
        "recordclass",
        "cryptography",
        "requests",
    ],
    python_requires='>=3.7,<4',
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

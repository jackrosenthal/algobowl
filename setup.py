from pathlib import Path

import setuptools

HERE = Path(__file__).resolve().parent

BASE_DEPENDS = [
    "click>=8.0",
    "pytest>=4.6",
    "pytest-cov>=4.1.0",
    "requests>=2.0",
    "tabulate>=0.8",
    "toml>=0.10",
]

WEB_DEPENDS = [
    "TurboGears2 >= 2.3.12",
    "tgext.admin-jmr",
    "decorator",
    "google-api-python-client",
    "google-auth-oauthlib",
    "tw2.forms",
    "Beaker >= 1.8.0",
    "Kajiki >= 0.6.3",
    "filedepot >= 0.6.0",
    "zope.sqlalchemy >= 1.2",
    "sqlalchemy>=1.3,<1.4",
    "alembic>=0.8.8",
    "repoze.who",
    "WebHelpers2",
    "recordclass",
    "cryptography",
    "requests",
]

DEV_DEPENDS = [
    "tg.devtools",
]

setuptools.setup(
    name="algobowl",
    version=(HERE / "VERSION").read_text(encoding="ascii").strip(),
    description="Competition-based group project for Algorithms courses",
    long_description=(HERE / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Jack Rosenthal",
    author_email="jack@rosenth.al",
    url="https://github.com/jackrosenthal/algobowl",
    packages=setuptools.find_packages(),
    python_requires=">=3.8,<4",
    install_requires=BASE_DEPENDS,
    extras_require={
        "web": WEB_DEPENDS,
        "dev": WEB_DEPENDS + DEV_DEPENDS,
    },
    include_package_data=True,
    package_data={"algobowl": ["templates/*/*", "public/*/*"]},
    entry_points={
        "console_scripts": [
            "algobowl = algobowl.cli.__main__:main",
        ],
        "paste.app_factory": ["main = algobowl.config.middleware:make_app"],
        "gearbox.plugins": ["turbogears-devtools = tg.devtools"],
    },
)

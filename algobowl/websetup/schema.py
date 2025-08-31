"""Setup the algobowl application"""

import transaction
from tg import config


def setup_schema(command, conf, vars):
    """Place any commands to setup algobowl here"""
    # Load the models

    # <websetup.websetup.schema.before.model.import>
    from algobowl import model  # noqa: PLC0415

    # <websetup.websetup.schema.after.model.import>
    # <websetup.websetup.schema.before.metadata.create_all>
    print("Creating tables")
    model.metadata.create_all(bind=config["tg.app_globals"].sa_engine)
    # <websetup.websetup.schema.after.metadata.create_all>
    transaction.commit()
    print("Initializing Migrations")
    import alembic.config  # noqa: PLC0415

    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option("script_location", "migration")
    alembic_cfg.set_main_option("sqlalchemy.url", config["sqlalchemy.url"])
    import alembic.command  # noqa: PLC0415

    alembic.command.stamp(alembic_cfg, "head")

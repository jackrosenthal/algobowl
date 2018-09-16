"""Setup the algobowl application"""
from algobowl.config.environment import load_environment
from .schema import setup_schema
from .bootstrap import bootstrap


def setup_app(command, conf, vars):
    load_environment(conf.global_conf, conf.local_conf)
    setup_schema(command, conf, vars)
    bootstrap(command, conf, vars)


__all__ = ['setup_app']

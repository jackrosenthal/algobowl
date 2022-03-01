import json

import click
import tabulate
import toml


def cmd(text):
    return click.style(text, fg="cyan", bold=True)


def err(text):
    err_prefix = click.style("ERROR:", fg="red", bold=True)
    click.echo(f"{err_prefix} {text}", err=True)


def filter_table(table, keys):
    table = [{k: row[k] for k in keys} for row in table]
    return table


class JsonFormatter:
    def dump_table(self, table, headers="keys", filter_keys=None):
        if filter_keys:
            table = filter_table(table, filter_keys)
        self.dump_json(table)

    def dump_config(self, config):
        self.dump_json(config)

    def dump_json(self, data):
        click.echo(json.dumps(data, sort_keys=True, indent=4))


class TableFormatter(JsonFormatter):
    def dump_table(self, table, headers="keys", filter_keys=None):
        if filter_keys:
            table = filter_table(table, filter_keys)
        click.echo(tabulate.tabulate(table, headers=headers))

    def dump_config(self, config):
        click.echo(toml.dumps(config), nl=False)

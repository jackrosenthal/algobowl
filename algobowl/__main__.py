import flask.cli
import argparse
import inspect
from . import create_minimal_app, db
from .auth import login_manager


def show_config(app):
    for k, v in app.config.items():
        print("{}: {!r}".format(k, v))


def init_db(app):
    """
    Initialize the database with default seed values.
    """
    db.create_all(app=app)
    db.session.commit()


def init_user(app, *users):
    """
    Create accounts for the provided usernames if they
    do not exist.
    """
    for user in users:
        u = login_manager.user_from_id(user)
        db.session.add(u)
        print("Added user {!r}".format(u))
    db.session.commit()


def promote_admin(app, *users):
    """
    Promote the provided user to admin.
    """
    for user in users:
        u = login_manager.user_from_id(user)
        u.admin = True
        db.session.add(u)
        print("Promoted user {!r}".format(u))
    db.session.commit()


subcommands = [init_db, show_config, init_user, promote_admin]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sa-debug',
        action='store_true',
        help='Print SQL statements to console')
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    for f in subcommands:
        p = subparsers.add_parser(
            f.__name__.replace('_', '-'),
            help=f.__doc__)
        p.set_defaults(func=f)
        sig = inspect.signature(f)
        for parm in sig.parameters.values():
            if parm.name == 'app':
                continue

            ap_lst = []
            ap_dict = {}

            if (parm.default is not parm.empty
                    or parm.kind is parm.KEYWORD_ONLY):
                ap_lst.append('--' + parm.name.replace('_', '-'))
            else:
                ap_lst.append(parm.name.replace('_', '-'))

            if parm.default is not parm.empty:
                ap_dict['default'] = parm.default

            if parm.annotation is not parm.empty:
                ap_dict['type'] = parm.annotation

            if parm.kind is parm.VAR_POSITIONAL:
                ap_dict['nargs'] = '*'

            p.add_argument(*ap_lst, **ap_dict)

    args = parser.parse_args()

    config_dict = {
        'SQLALCHEMY_ECHO': args.sa_debug,
    }

    flask.cli.load_dotenv()
    app = create_minimal_app(config_dict=config_dict)
    app.app_context().push()

    call_args = []
    call_kw = {}
    sig = inspect.signature(args.func)
    for parm in sig.parameters.values():
        if parm.name == 'app':
            continue
        elif parm.kind is parm.VAR_POSITIONAL:
            call_args.extend(getattr(args, parm.name))
        else:
            call_kw[parm.name] = getattr(args, parm.name)

    args.func(app, *call_args, **call_kw)


if __name__ == '__main__':
    main()

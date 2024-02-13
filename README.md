# AlgoBOWL

AlgoBOWL is a group project for algorithms courses.  Students compete to create
heuristics to an NP-hard problem.  For more information, see the paper in
[ITiCSE 2019](https://doi.org/10.1145/3304221.3319761).

This is the AlgoBOWL web application, as well as associated tools (e.g., command
line interface).

## Getting Started

The rest of this `README` assumes you're interested in hacking on the AlgoBOWL
code, and want to install the web app locally.  For other topics of interest,
check out the `docs/` directory.

You'll need a system running Linux and Python 3.8+.

Create and activate a virtual environment to install in:

```shellsession
$ python3 -m venv venv
$ . venv/bin/activate
```

Next, install the app in editable mode::

```shellsession
$ pip install -e ".[dev]"
```

Next, copy the sample development config and setup the application::

```shellsession
$ cp development.ini.sample development.ini
$ gearbox setup-app
```

Finally, you can serve the app::

```shellsession
$ gearbox serve --reload --debug
```

Have fun!

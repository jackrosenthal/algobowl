# AlgoBOWL CLI

The AlgoBOWL CLI provides convenient access to interact with AlgoBOWL from your
command line and from scripts.

**The CLI is still very much in beta state, and not complete yet.**
Improvements are welcome (send patches!)

## System Requirements

The only requirement is Python 3.9 or newer.  The CLI is best-supported on
Linux, however, it may work on Windows and Mac as well.  Patches are welcome
if it doesn't work on Windows or Mac.

## Installation

Download [`cli_launcher.py`](../cli_launcher.py) and mark it executable.  It's
recommended to name this file `algobowl` and put it somewhere on your `PATH`.
Alternatively, you could download it into your group's Git repository and use it
as `./algobowl` from there.

``` shellsession
$ curl https://raw.githubusercontent.com/jackrosenthal/algobowl/main/cli_launcher.py -o algobowl && chmod +x algobowl
```

The CLI launcher will download the CLI and dependencies, and keep them up to
date as required.  If you prefer to manage your own installation, or plan on
hacking on the CLI source code, you can install an "editable copy" of this
repository using `pip` instead:

``` shellsession
$ pip install -e .
```

## Usage

Detailed usage can be found by running `algobowl --help`.

### Authenticating to an AlgoBOWL server

Run `algobowl auth login` and follow the instructions.  You can then verify
you've successfully logged in by running `algobowl auth whoami`.

The default server is `https://mines.algobowl.org`.  You can choose another
server by running `algobowl config set-default-server ...`.

### Group Commands

You can perform actions on behalf of your group using `algobowl group` commands.
By default, if you're only a member of one active group, it'll be selected for
group commands.  If you're a member of multiple groups, or you're a site
administrator and want to act on behalf of another group, you can pass
`--group-id` to specify your group ID.  Here are some commands which may be of
interest:

#### Input Upload

* `algobowl group input upload FILENAME`: Upload your group's input.
* `algobowl group input download OUTPUT_FILE`: Download your group's input.
* `algobowl group set-team-name TEAM_NAME`: Set your team name.

#### Output Upload

* `algobowl group output --to-group-id GROUP_ID upload FILENAME`: Upload an
   output.
* `algobowl group output --to-group-id GROUP_ID download OUTPUT_FILE`: Download
   one of your submitted outputs.
* `algobowl group output list`: List output files you'll need to provide.

Note: if you use filenames containing the group ID, (e.g.,
`output_group123.txt`), the CLI can infer the group ID from the filename, and
passing `--to-group-id` is not required.  When multiple IDs appear in the
filename (e.g., `output_from_group120_to_group123.txt`), the second ID
is used.

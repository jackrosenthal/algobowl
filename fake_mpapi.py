#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["flask"]
# ///
"""
Fake MPAPI server for local testing.

Usage:
    uv run fake_mpapi.py [--port 8081]

Then set auth.mpapi.url = http://localhost:8081 in your development.ini.
"""

import argparse
import hashlib
import uuid
from urllib.parse import urlencode

from flask import Flask, jsonify, redirect, request

app = Flask(__name__)

# In-memory ticket store: {ticket: username}
tickets: dict[str, str] = {}


def fake_uid(username: str) -> int:
    """Generate a stable fake uidNumber from the username."""
    return int(hashlib.md5(username.encode()).hexdigest()[:8], 16)


def user_attributes(username: str) -> dict:
    return {
        "uidNumber": fake_uid(username),
        "first": username.capitalize(),
        "sn": "Testuser",
        "mail": f"{username}@mines.edu",
    }


@app.get("/sso")
def sso_form():
    return_url = request.args.get("return", "/")
    return f"""
<!doctype html>
<html>
<head><title>Fake MPAPI Login</title>
<style>
  body {{ font-family: sans-serif; max-width: 400px; margin: 4rem auto; }}
  input, button {{ display: block; width: 100%; padding: 0.5rem; margin: 0.5rem 0; font-size: 1rem; box-sizing: border-box; }}
  .notice {{ background: #fff3cd; border: 1px solid #ffc107; padding: 0.75rem; margin-bottom: 1rem; border-radius: 4px; }}
</style>
</head>
<body>
  <h2>Fake MPAPI Login</h2>
  <div class="notice">
    This is a fake MPAPI server for local testing only.
    Try a username ending in <code>_sw</code> to test the student worker block.
  </div>
  <form method="post" action="/sso">
    <input type="hidden" name="return" value="{return_url}" />
    <label>Username</label>
    <input type="text" name="username" autofocus placeholder="e.g. jdoe or jdoe_sw" />
    <button type="submit">Sign In</button>
  </form>
</body>
</html>
"""


@app.post("/sso")
def sso_submit():
    username = request.form.get("username", "").strip()
    return_url = request.form.get("return", "/")

    if not username:
        return redirect(f"/sso?{urlencode({'return': return_url})}")

    ticket = str(uuid.uuid4())
    tickets[ticket] = username
    separator = "&" if "?" in return_url else "?"
    return redirect(f"{return_url}{separator}tkt={ticket}")


@app.post("/fetch")
def fetch():
    tkt = request.form.get("tkt")
    username = tickets.pop(tkt, None)
    if username is None:
        return jsonify({"result": "failure", "reason": "unknown ticket"})
    return jsonify(
        {
            "result": "success",
            "uid": username,
            "attributes": user_attributes(username),
        }
    )


@app.get("/uid/<username>")
def uid_lookup(username: str):
    return jsonify(
        {
            "result": "success",
            "uid": username,
            "attributes": user_attributes(username),
        }
    )


@app.get("/slo")
def slo():
    return """
<!doctype html>
<html>
<head><title>Signed Out</title>
<style>body {{ font-family: sans-serif; max-width: 400px; margin: 4rem auto; }}</style>
</head>
<body>
  <h2>Signed out (fake MPAPI)</h2>
  <p>You have been signed out of the fake MPAPI server.</p>
</body>
</html>
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    print(f"Fake MPAPI running at http://localhost:{args.port}")
    print(f"Set auth.mpapi.url = http://localhost:{args.port} in development.ini")
    app.run(port=args.port, debug=True)

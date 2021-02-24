#!/bin/bash

set -x -e

HERE="$(dirname "$0")"

for f in "${HERE}"/sampdata/*.sql; do
    CFG="$(mktemp /tmp/migration_test_XXXXXXXX.ini)"
    DB="$(mktemp /tmp/migration_test_XXXXXXXX.db)"
    sqlite3 "${DB}" <"${f}"
    sed -e 's#%(here)s/devdata\.db#'"${DB}"'#g' \
        "${HERE}/development.ini.sample" >"${CFG}"
    gearbox migrate -c "${CFG}" -l "${HERE}/migration" upgrade
    rm "${CFG}"
    rm "${DB}"
done

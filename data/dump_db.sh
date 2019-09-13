#!/usr/bin/env bash
sqlite3 -header -csv dsds.db  "select * from objects;" > objects.csv
sqlite3 -header -csv dsds.db  "select * from checksums;" > checksums.csv
sqlite3 -header -csv dsds.db  "select * from contents;" > contents.csv
sqlite3 -header -csv dsds.db  "select * from access_methods;" > access_methods.csv
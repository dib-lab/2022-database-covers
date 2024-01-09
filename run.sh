#! /bin/bash
set -e
set -x

/usr/bin/time -v ./make-db-cover.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-reps.k21.zip \
    /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip \
    -o gtdb-rs214.k21.cover.zip --scaled=1000 -k 21

mkdir -p gtdb-rs214.k21.scaled=1000.cover.d
cd gtdb-rs214.k21.scaled=1000.cover.d && sourmash sig split ../gtdb-rs214.k21.cover.zip -E .sig.gz && cd ..

find $(pwd)/gtdb-rs214.k21.scaled=1000.cover.d -type f > list.gtdb-rs214.k21.cover.txt

#! /bin/bash

/usr/bin/time -v ./make-db-cover.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-reps.k21.zip \
    /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip \
    -o gtdb-rs214.k21.cover.d/ --scaled=10000 -k 21
#! /bin/bash
#/usr/bin/time -v ./make-pangenome-sketches.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214-lineages.sqldb -o gtdb-rs214-pangenomes.k21.species.zip -k 21
/usr/bin/time -v ./make-pangenome-sketches.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214-lineages.sqldb -o gtdb-rs214-pangenomes.k21.genus.zip -k 21 -r genus


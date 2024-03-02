# A Pangenome Guide

This is a walkthrough on how to use the 2022-database-covers repo for building pangenome databases!

Make sure to fork all the branches from [ctb/2022-database-covers](https://github.com/ctb/2022-database-covers) and create a tmux session that will be for this specific project!

## Clone the repo by a specific branch

The command `git clone` only clones the top-level branch (e.g. `main`, `master`, or `latest`).

To clone a specific branch in a repo, use:
```
git clone -b pangenome git@github.com:ccbaumler/2022-database-covers.git
```

Use the `git branch` command to see the branch you are currently using.
```
git branch
```

Output:
```
* pangenome
```

If you have already cloned a repo and would like to add a remote branch to your local repository, you can do that as well!
Simply use `git checkout` like so:
```
git checkout -b latest origin/latest
```

This `git checkout` command will add the `latest` branch to the local repo. What command will show you what branches you have in your local repo?

Output:
```
latest
* pangenome
```

## Set up the databases

Next we need to set up the repo with the correct databases (or at least identify the `pwd` path for each define in the script).

Use `cat` to see the bash script Titus used to run the python script:
```
cat make-pangenome.sh
```

The `cat` command's output is one way of seeing how to use the script as the author intended. Understanding the author's intentions is a critical step in using any software application, because we do not have a detailed documentation for using this simple script, we need to do some detective work.

Output:
```
#! /bin/bash
#/usr/bin/time -v ./make-pangenome-sketches.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214-lineages.sqldb -o gtdb-rs214-pangenomes.k21.species.zip -k 21
/usr/bin/time -v ./make-pangenome-sketches.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214-lineages.sqldb -o gtdb-rs214-pangenomes.k21.genus.zip -k 21 -r genus
```

> - `#! /bin/bash` is the script identity. This is a bash script.
> - `/usr/bin/time -v` is a benchmarking software on the farm that outputs some standard metrics. This is typically used to see how the script performance changes with alterations.
> - `./make-pangenome-sketches.py` is a command to run the a script that is executable (i.e. `chmod +x`).
> - `/group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214-lineages.sqldb -o gtdb-rs214-pangenomes.k21.genus.zip -k 21 -r genus` are the arguments of the executing script.

Looking through this command line operation, I can see two databases we will need before we run the command and three arguments that define the output.

We will need one of [sourmashes prepared databases](https://sourmash.readthedocs.io/en/latest/databases.html#gtdb-r08-rs214-dna-databases) and a lineage spreadsheet. Typically, this type of step would require the use of a command that downloads files through the web. Think `curl`, `rsync`, `wget`. However, these files are stored on the farm and made available from the farm. This means the files are already in the farm. We only need to find and link the files to our repository to use them!

Linking is a simple way of not using move disk space than needed. By linking a file, we are creating a named file pointer to the location of the actual file.

```
ln -s /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip $(pwd)/gtdb-rs214-k21.zip
ln -s /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214.lineages.csv ./gtdb-rs214.lineages.csv
```

> - I have changed the output file path in the lineages line to highlight the proper usage of `ln -s`
> - `ln -s` is the symbolic link creation command
> - `/group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip` is the absolute path location of the file
> - `$(pwd)/gtdb-rs214-k21.zip` is the absolute path location to the symbolic link we will use

The `ln -s` command creates a symbolic link with the purpose of pointing to the files we defined in the `ln -s` command previously. It is similar to simply typing in the absolute path like Titus did in the bash script.

For added linux fun!, let's try to create the sqldb to fully copy Titus' bash command. If we look at the [sourmash documentation](https://sourmash.readthedocs.io/en/latest/databases-advanced.html#storing-taxonomies), we can narrow in on the command to do this! Running `sourmash tax prepare -h` will give us guidance to running this sub-command as well.

Using the linked lineage file...
```
sourmash tax prepare --taxonomy-csv ./gtdb-rs214.lineages.csv -F sql -o gtdb-rs214.lineages.sqldb
```

Doesn't work!!!
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

loading taxonomies...
ERROR while loading taxonomies!
cannot read taxonomy assignments from 'gtdb-rs214.lineages.csv': 'gtdb-rs214.lineages.csv' does not exist
```

Well, that's okay because we know the absolute path to the file anyway.

```
sourmash tax prepare --taxonomy-csv /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214.lineages.csv -F sql -o gtdb-rs214.lineages.sqldb
```

Yay, we get the correct output:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

loading taxonomies...
...loaded 402709 entries.
saving to 'gtdb-rs214.lineages.sqldb', format sql...
done!
```

But, why didn't our symbolic link work? 

Hint: Think in absolute paths!

## How to run the script

After reading the previous sections breakdown of the bash script that runs the python script, you should have a rough idea of how to run this script, but there are two more ways of investigating the script further.

1. Using the `-h, --help` command

Try it out with:
```
./make-pangenome-sketches.py -h
```

Reading the output should give further details on how to run this script
```
usage: make-pangenome-sketches.py [-h] -t FILE [FILE ...] [--scaled SCALED] [-k KSIZE] -o OUTPUT [-r RANK] sketches [sketches ...]

positional arguments:
  sketches              sketches to combine

options:
  -h, --help            show this help message and exit
  -t FILE [FILE ...], --taxonomy-file FILE [FILE ...], --taxonomy FILE [FILE ...]
                        database lineages file
  --scaled SCALED
  -k KSIZE, --ksize KSIZE
  -o OUTPUT, --output OUTPUT
  -r RANK, --rank RANK
```

2. Read the script itself

Open the script file in a text editor of your choice.
```
vi make-pangenome-sketches.py
```

Look for the section of the script that defines the arguments. For this particular script, we are looking for `argparse` package commands.
```
    p = argparse.ArgumentParser()
    p.add_argument(
        '-t', '--taxonomy-file', '--taxonomy', metavar='FILE',
        action="extend", nargs='+', required=True,
        help='database lineages file'
    )
    p.add_argument(
        'sketches', nargs='+',
        help='sketches to combine'
    )
    p.add_argument('--scaled', default=1000, type=int)
    p.add_argument('-k', '--ksize', default=31, type=int)
    p.add_argument('-o', '--output', required=True)
    p.add_argument('-r', '--rank', default='species')
    args = p.parse_args()
```

To exit a text editor
click```esc``` and type```:qw```

Titus' command:
```
./make-pangenome-sketches.py /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip -t gtdb-rs214.lineages.sqldb -o gtdb-rs214-pangenomes.k21.genus.zip -k 21 -r genus
```

Our command
```
./make-pangenome-sketches.py gtdb-rs214-k21.zip -t gtdb-rs214.lineages.sqldb -o gtdb-rs214-k21.pangenomes.genus.zip -k 21 -r genus
```

Output:
```
loading taxonomies from ['gtdb-rs214.lineages.sqldb']
found 402709 identifiers in taxdb.
loading file /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-k21.zip as index => manifest
...1000 - loading
...2000 - loading
...3000 - loading

.
.
.

...18000 - saving
...19000 - saving
...20000 - saving
```

Now run the command to produce a species and family pangenome database.

## Understanding how the databases have changed

Let's do a very important step to any bioinformatics. Visualize the data!

```
sourmash sig summarize <each_database>
```

This command will inform us how the script has changed our databases. With this information, we can begin asking informed questions about the scripts operations and final products.

Orignal Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from 'gtdb-rs214-k21.zip'
path filetype: ZipFileLinearIndex
location: /home/baumlerc/2022-database-covers/gtdb-rs214-k21.zip
is database? yes
has manifest? yes
num signatures: 402709
** examining manifest...
total hashes: 1485439346
summary of sketches:
   402709 sketches with DNA, k=21, scaled=1000        1485439346 total hashes
```

Species Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from 'gtdb-rs214-k21.pangenomes.species.zip'
path filetype: ZipFileLinearIndex
location: /home/baumlerc/2022-database-covers/gtdb-rs214-k21.pangenomes.species.zip
is database? yes
has manifest? yes
num signatures: 85205
** examining manifest...
total hashes: 326393008
summary of sketches:
   85205 sketches with DNA, k=21, scaled=1000         326393008 total hashes
```

Genus Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from 'gtdb-rs214-k21.pangenomes.genus.zip'
path filetype: ZipFileLinearIndex
location: /home/baumlerc/2022-database-covers/gtdb-rs214-k21.pangenomes.genus.zip
is database? yes
has manifest? yes
num signatures: 20739
** examining manifest...
total hashes: 274333012
summary of sketches:
   20739 sketches with DNA, k=21, scaled=1000         274333012 total hashes
```

Family Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from 'gtdb-rs214-k21.pangenomes.family.zip'
path filetype: ZipFileLinearIndex
location: /home/baumlerc/2022-database-covers/gtdb-rs214-k21.pangenomes.family.zip
is database? yes
has manifest? yes
num signatures: 4814
** examining manifest...
total hashes: 262393736
summary of sketches:
   4814 sketches with DNA, k=21, scaled=1000          262393736 total hashes
```

We can see that the number of sketches in each of our ranked pangenome databases corresponds with the taxonomic lineage database with:
```
sourmash tax summarize gtdb-rs214.lineages.sqldb 
```

Output:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

loading taxonomies...
...loaded 402709 entries.
number of distinct taxonomic lineages: 402709
rank superkingdom:        2 distinct taxonomic lineages
rank phylum:              202 distinct taxonomic lineages
rank class:               553 distinct taxonomic lineages
rank order:               1802 distinct taxonomic lineages
rank family:              4814 distinct taxonomic lineages
rank genus:               20739 distinct taxonomic lineages
rank species:             85205 distinct taxonomic lineages
```

Comparing species level pangenome with representative genomes of GTDB

Representative Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from '/group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-reps.k21.zip'
path filetype: ZipFileLinearIndex
location: /group/ctbrowngrp/sourmash-db/gtdb-rs214/gtdb-rs214-reps.k21.zip
is database? yes
has manifest? yes
num signatures: 85205
** examining manifest...
total hashes: 270637876
summary of sketches:
   85205 sketches with DNA, k=21, scaled=1000         270637876 total hashes
```

Species Database:
```
== This is sourmash version 4.8.5. ==
== Please cite Brown and Irber (2016), doi:10.21105/joss.00027. ==

** loading from 'gtdb-rs214-k21.pangenomes.species.zip'
path filetype: ZipFileLinearIndex
location: /home/baumlerc/2022-database-covers/gtdb-rs214-k21.pangenomes.species.zip
is database? yes
has manifest? yes
num signatures: 85205
** examining manifest...
total hashes: 326393008
summary of sketches:
   85205 sketches with DNA, k=21, scaled=1000         326393008 total hashes
```

## Explore the impact of database on `sourmash gather`

Download the metadata at [this SRA Run Selector link](https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRR1976948%2CSRR5650070%2CSRR606249%2CSRR12324253&o=acc_s%3Aa)

I renamed my SraRunTable.txt to mock.txt.

For Farm HPC users:

1. Check if signature files already exist on the Farm.
```
for i in $(awk -F',' 'NR >= 2 {print $1}' mock.txt | uniq); do echo [ -e "/group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/$i.sig" ] && echo "File $i.sig exists in wort" || echo "File $i.sig does not exist in wort" ; done
```

2. Link those files into the `sigs` directory for ease and minimal disk space use.
```
for i in $(awk -F',' 'NR > 1 {print $1}' mock.txt); do ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/$i.sig $(pwd)/sigs/$i.sig ; done
```

> - Note that each of these bash conditionals were written with `echo` after `do` in the for loop. This output shows the action the for loop will execute before I unleash it on the computer cluster.
> This:
> ```
> for i in $(awk -F',' 'NR > 1 {print $1}' mock.txt); do echo ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/$i.sig $(pwd)/sigs/$i.sig ; done
> ```
> Outputs:
> ```
> ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/SRR606249.sig /home/baumlerc/2022-database-covers/sigs/SRR606249.sig
> ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/SRR5650070.sig /home/baumlerc/2022-database-covers/sigs/SRR5650070.sig
> ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/SRR1976948.sig /home/baumlerc/2022-database-covers/sigs/SRR1976948.sig
> ln -s /group/ctbrowngrp/irber/data/wort-data/wort-sra/sigs/SRR12324253.sig /home/baumlerc/2022-database-covers/sigs/SRR12324253.sig
> ```

Running `sourmash prefetch` on mock metagenome signatures
```
sourmash prefetch --threshold-bp 3000 -o prefetch/SRR12324253-prefetch.csv -k 21 sigs/SRR12324253.sig gtdb-rs214-k21.pangenomes.species.zip
```
[Should threshold be set to 3x scaled as a minimum](https://sourmash.readthedocs.io/en/latest/faq.html#id8)

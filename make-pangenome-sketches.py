#! /usr/bin/env python

import argparse
import sys
from collections import Counter, defaultdict
import csv
import os
import sourmash
from sourmash import sourmash_args
from sourmash.tax import tax_utils

def main():
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
    p.add_argument('-o', '--output', required=True,
                    help='Define a filename for the pangenome signatures (.zip preferred).')
    p.add_argument('--csv', help='A CSV file generated to contain the lineage rank, genome name, hash count, and genome count.')
    p.add_argument('-r', '--rank', default='species')
    p.add_argument('-a', '--abund', action='store_true', help='Enable abundance tracking of hashes across rank selection.')
    args = p.parse_args()

    print(f"loading taxonomies from {args.taxonomy_file}")
    taxdb = sourmash.tax.tax_utils.MultiLineageDB.load(args.taxonomy_file)
    print(f"found {len(taxdb)} identifiers in taxdb.")

    ident_d = {}
    revtax_d = {}
    accum = defaultdict(dict)
    if args.abund:
        counts = {}
    if args.csv:
        csv_file = check_csv(args.csv)

    # Load the database
    for filename in args.sketches:
        print(f"loading file {filename} as index => manifest")
        db = sourmash_args.load_file_as_index(filename)
        db = db.select(ksize=args.ksize)
        mf = db.manifest
        assert mf, "no matching sketches for given ksize!?"

        if args.csv: chunk = []

        # Work on a single signature at a time across the database
        for n, ss in enumerate(db.signatures()):
            if n and n % 1000 == 0:
                print(f'...{n} - loading')

            name = ss.name
            ident = tax_utils.get_ident(name)

            # grab relevant lineage name
            lineage_tup = taxdb[ident]
            lineage_tup = tax_utils.RankLineageInfo(lineage=lineage_tup)
            lineage_pair = lineage_tup.lineage_at_rank(args.rank)
            lineage_name = lineage_pair[-1].name

            ident_d[lineage_name] = ident # pick an ident to represent this set of pangenome sketches

            # Accumulate the count within lineage names if `--abund` in cli
            if args.abund:
                c = Counter(ss.minhash.hashes)
                if lineage_name in counts:
                    counts[lineage_name].update(c)
                else:
                    counts[lineage_name] = c

            # track merged sketches
            mh = revtax_d.get(lineage_name)

            if mh is None:
                mh = ss.minhash.to_mutable()
                revtax_d[lineage_name] = mh
            else:
                mh += ss.minhash

            ## Add {name, hash_count} to a lineage key then
            ## create a simpler dict for writing the csv
            if args.csv:
                # Accumulated counts of hashes in lineage by genome
                hash_count = len(mh.hashes)

                accum[lineage_name][name] = accum[lineage_name].get(name, 0) + hash_count
                chunk.append({'lineage': lineage_name, 'sig_name': name, 'hash_count': hash_count, 'genome_count': n})

            if args.csv and len(chunk) >= 1000: #args.chunk_size?
                write_chunk(chunk, csv_file) #args.outputfilenameforcsv?
                accum = defaultdict(dict)
                chunk = []

        # Write remaining data
        if args.csv and len(chunk) > 0:
            write_chunk(chunk, csv_file)
            accum = defaultdict(dict)
            chunk = []

   # save!
    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sigs:
        for n, (lineage_name, ident) in enumerate(ident_d.items()):
            if n and n % 1000 == 0:
                print(f'...{n} - saving')

            sig_name = f'{ident} {lineage_name}'

            # retrieve merged MinHash
            mh = revtax_d[lineage_name]

            # Add abundance to signature if `--abund` in cli
            if args.abund:
                abund_d = dict(counts[lineage_name])

                abund_mh = mh.copy_and_clear()
                abund_mh.track_abundance = True
                abund_mh.set_abundances(abund_d)

            # Create a signature with abundance only if `abund` in cli. Otherwise, create a 'flat' sig
            ss = sourmash.SourmashSignature(abund_mh, name=sig_name) if args.abund else sourmash.SourmashSignature(mh, name=sig_name)

            save_sigs.add(ss)

# Chunk function to limit the memory used by the hash_count dict and list
def write_chunk(chunk, output_file):
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['lineage', 'sig_name', 'hash_count', 'genome_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(chunk)

def check_csv(csv_file):
    if csv_file is None:
        return

    if os.path.exists(count_csv):
        raise argparse.ArgumentTypeError("\n%s already exists" % count_csv)

    count_csv = os.path.splitext(csv_file)[0] + ".csv"
    return count_csv

if __name__ == '__main__':
    sys.exit(main())

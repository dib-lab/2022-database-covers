#! /usr/bin/env python
import argparse
import sys

from collections import defaultdict
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
    p.add_argument('-o', '--output', required=True)
    p.add_argument('-r', '--rank', default='species')
    args = p.parse_args()

    print(f"loading taxonomies from {args.taxonomy_file}")
    taxdb = sourmash.tax.tax_utils.MultiLineageDB.load(args.taxonomy_file)

    revtax_d = {}
    ident_d = {}

    for filename in args.sketches:
        print(f"loading file {filename} as index => manifest")
        db = sourmash_args.load_file_as_index(filename)
        db = db.select(ksize=args.ksize)
        mf = db.manifest
        assert mf, "no matching sketches for given ksize!?"

        for ss in db.signatures():
            name = ss.name
            md5sum = ss.md5sum()

            ident = tax_utils.get_ident(name)

            # grab relevant lineage name
            lineage_tup = taxdb[ident]
            lineage_tup = tax_utils.RankLineageInfo(lineage=lineage_tup)
            lineage_pair = lineage_tup.lineage_at_rank(args.rank)
            lineage_name = lineage_pair[-1].name

            # pick an ident to represent this set of pangenome sketches
            ident_d[lineage_name] = ident # ok if overwrite...

            # track
            mh = revtax_d.get(lineage_name)
            if mh is None:
                mh = ss.minhash.to_mutable()
                revtax_d[lineage_name] = mh
            else:
                mh += ss.minhash

            print('...', name)

    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sigs:
        for lineage_name, ident in ident_d.items():
            sig_name = f'{ident} {lineage_name}'
            mh = revtax_d[lineage_name]
            ss = sourmash.SourmashSignature(mh, name=sig_name)
            save_sigs.add(ss)

            print(f'saved: {sig_name}')


if __name__ == '__main__':
    sys.exit(main())

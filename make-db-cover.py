#! /usr/bin/env python
import sys
import sourmash
from sourmash import sourmash_args
import argparse


from sourmash.search import JaccardSearch, SearchType

class MyJaccardSearch(JaccardSearch):
    def __init__(self, query):
        JaccardSearch.__init__(self, SearchType.CONTAINMENT)
        self.query = query

    def collect(self, score, match):
        if self.query == match:
            return False
        return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('database')
    p.add_argument('--scaled', default=10000, type=int)
    p.add_argument('-o', '--output', required=True)
    args = p.parse_args()

    seen_hashes = set()

    idx = sourmash.load_file_as_index(args.database)

    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sigs:
        for n, ss in enumerate(idx.signatures()):
            print(n, len(seen_hashes))
            mh = ss.minhash.downsample(scaled=args.scaled)
            new_mh = mh.copy_and_clear()

            hashes = set(mh.hashes)
            remaining = hashes - seen_hashes
            new_mh.add_many(remaining)
            seen_hashes.update(remaining)

            ss.minhash = new_mh
            save_sigs.add(ss)


if __name__ == '__main__':
    sys.exit(main())

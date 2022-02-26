#! /usr/bin/env python
import sys
import sourmash
from sourmash import sourmash_args
import argparse
import os.path


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
    p.add_argument('databases', nargs='+')
    p.add_argument('--scaled', default=10000, type=int)
    p.add_argument('-o', '--output', required=True)
    args = p.parse_args()

    seen_hashes = set()

    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sigs:
        for filename in args.databases:
            idx = sourmash.load_file_as_index(filename)

            for n, ss in enumerate(idx.signatures()):
                print(f"examining {ss.name[:30]}... from {os.path.basename(filename)} - #{n}, {len(seen_hashes)} total hashes.")
                mh = ss.minhash.downsample(scaled=args.scaled)

                hashes = set(mh.hashes)
                remaining = hashes - seen_hashes
                seen_hashes.update(remaining)

                if len(hashes) == len(remaining):
                    print("saving unmodified signature.")
                    save_sigs.add(ss)
                elif len(remaining) == 0:
                    print("DISCARDING signature.")
                else:
                    new_mh = mh.copy_and_clear()

                    new_mh.add_many(remaining)
                    ss.minhash = new_mh
                    save_sigs.add(ss)
                    print(f'saving updated minhash ({len(hashes)} to {len(remaining)})')
                print('---')


if __name__ == '__main__':
    sys.exit(main())

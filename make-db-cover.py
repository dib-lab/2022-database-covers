#! /usr/bin/env python
import sys
import sourmash
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
    p.add_argument('--scaled', default=10000)
    args = p.parse_args()

    idx = sourmash.load_file_as_index(args.database)
    for ss in idx.signatures():
        ss.minhash = ss.minhash.downsample(scaled=args.scaled)
        search_obj = MyJaccardSearch(ss)

        results = list(idx.find(search_obj, ss))
        if results:
            print(ss.name)
            for n, sr in enumerate(results):
                print('   ', n, sr.signature.name, sr.score)
            print('---')
        else:
            print('XXX NO RESULTS:', ss.name)


if __name__ == '__main__':
    sys.exit(main())

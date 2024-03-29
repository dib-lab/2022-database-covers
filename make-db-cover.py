#! /usr/bin/env python
import sys
import sourmash
from sourmash import sourmash_args
import argparse
import os.path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('databases', nargs='+')
    p.add_argument('--scaled', default=10000, type=int)
    p.add_argument('-k', '--ksize', default=31, type=int)
    p.add_argument('-o', '--output', required=True)
    p.add_argument('--preload', help="load this cover first")
    args = p.parse_args()

    seen_hashes = set()

    if args.preload:
        print(f"preloading '{args.preload}'")
        pre = sourmash.load_file_as_index(args.preload)
        pre = pre.select(ksize=args.ksize)

        for n, ss in enumerate(pre.signatures()):
            if n % 10000 == 0:
                print(f'preload at {n}')
            mh = ss.minhash.downsample(scaled=args.scaled)
            hashes = set(mh.hashes)
            seen_hashes.update(hashes)

        print(f"preloaded {len(seen_hashes)} hashes.")

    with sourmash_args.SaveSignaturesToLocation(args.output) as save_sigs:
        print(f"opening '{args.output} to save.")
        for filename in args.databases:
            print(f"opening '{filename} for reading...")
            idx = sourmash.load_file_as_index(filename)
            idx = idx.select(ksize=args.ksize)

            for n, ss in enumerate(idx.signatures()):
                print(f"examining {ss.name[:30]}... from {os.path.basename(filename)} - #{n}, {len(seen_hashes)} total hashes.")
                mh = ss.minhash.downsample(scaled=args.scaled)

                hashes = set(mh.hashes)
                remaining = hashes - seen_hashes
                seen_hashes.update(remaining)

                ss = ss.to_mutable()

                if len(hashes) == len(remaining):
                    print("saving original (downsampled?) signature.")
                    ss.minhash = mh
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

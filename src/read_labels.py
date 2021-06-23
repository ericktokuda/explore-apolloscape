#!/usr/bin/env python3
"""Analyze labels from Apolloscape
"""

import argparse
import time, datetime
import os
from os.path import join as pjoin
import inspect

import sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import imageio
from labels_apollo import labels
from myutils import info, create_readme

##########################################################
def main(rootdir, outdir):
    """Main call"""
    info(inspect.stack()[0][3] + '()')
    names = {} # Load the apolloscape labels
    for l in labels:
        if l.clsId in names.keys(): continue
        names[l.clsId] = l.name
    ids = list(names.keys())
    nlabels = len(ids)

    roadid = 2
    recordid = 18
    camid = 5
    maskdir = pjoin(rootdir, 'road{:02d}_ins'.format(roadid), 'Label',
                    'Record{:03d}'.format(recordid),
                    'Camera {}'.format(camid))
    info('maskdir:{}'.format(maskdir))

    os.chdir(maskdir)
    allfiles = sorted(os.listdir(maskdir))
    files = []
    objs = np.zeros((len(allfiles), nlabels), dtype=int)
    i = 0
    for f in allfiles[:5]:
        if 'instanceIds' in f or '.json' in f: continue
        files.append(f.replace('_bin.png', ''))
        mask = imageio.imread(f)
        uvals, count = np.unique(mask, return_counts=True)
        for uval in uvals: objs[i, ids.index(uval)] = 1
        i += 1

    df = pd.DataFrame(objs[:i, :], columns=names.values())
    df['file'] = files
    df = df.reindex(columns=['file']+list(names.values()))
    outpath = pjoin(outdir, 'roa{:02d}_rec{:02d}_cam{}.csv'.format(
        roadid, recordid, camid))
    df.to_csv(outpath, index=False)

##########################################################
if __name__ == "__main__":
    info(datetime.date.today())
    t0 = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rootdir', required=True, help='ApolloScape root dir')
    parser.add_argument('--outdir', default='/tmp/out/', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    readmepath = create_readme(sys.argv, args.outdir)

    main(args.rootdir, args.outdir)

    info('Elapsed time:{:.02f}s'.format(time.time()-t0))
    info('Output generated in {}'.format(args.outdir))

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
from external.labels_apollo import labels as apollolabels
from myutils import info, create_readme

##########################################################
def main(rootdir, outdir):
    """Main call"""
    info(inspect.stack()[0][3] + '()')
    labels = {} # Load the apolloscape labels
    for l in apollolabels:
        if l.clsId in labels.keys(): continue
        labels[l.clsId] = l.name

    camera = 'Camera 5' # Just picking one of the cameras

    for r in sorted(os.listdir(rootdir)):
        roaddir = pjoin(rootdir, r)
        if (not r.endswith('_ins')) or (not os.path.isdir(roaddir)):
            continue
        roadidstr = r.replace('road', '').replace('_ins', '')
        labeldir = pjoin(roaddir, 'Label')
        for rec in sorted(os.listdir(labeldir)):
            recdir = pjoin(labeldir, rec)
            recidstr = rec.replace('Record', '')
            if (not rec.startswith('Record')) or (not os.path.isdir(recdir)):
                continue
            info('{}'.format(recdir))
            maskdir = pjoin(recdir, camera)
            outpath = pjoin(outdir, 'road{}_rec{}.csv'.format(
                roadidstr, recidstr))
            parse_masks(maskdir, labels, outpath)

##########################################################
def parse_masks(maskdir, labels, outpath):
    """Parse all masks in @maskdir and output a csv in @outdir"""
    # info(inspect.stack()[0][3] + '()')
    ids = list(labels.keys())
    nlabels = len(ids)
    os.chdir(maskdir)
    allfiles = sorted(os.listdir(maskdir))
    files = []
    objs = np.zeros((len(allfiles), nlabels), dtype=int)
    i = 0
    for f in allfiles:
        if 'instanceIds' in f or '.json' in f: continue
        files.append(f.replace('_bin', '').replace('.png', ''))
        mask = imageio.imread(f)
        uvals, counts = np.unique(mask, return_counts=True)
        for uval, count in zip(uvals, counts): objs[i, ids.index(uval)] = count
        i += 1

    df = pd.DataFrame(objs[:i, :], columns=labels.values())
    df['file'] = files
    df = df.reindex(columns=['file']+list(labels.values()))
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

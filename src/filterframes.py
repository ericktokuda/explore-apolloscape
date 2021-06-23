#!/usr/bin/env python3
"""Filter frames considering the objects they contain. Assume the existence of the csvs gerated by readlabels.py
"""

import argparse
import time, datetime
import os
from os.path import join as pjoin
import inspect

import sys, shutil, re
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import subprocess
from myutils import info, create_readme

##########################################################
def generate_video(frameids, ext, framedir, res, outpath):
    """Generate a video considering the given frames"""
    info(inspect.stack()[0][3] + '()')
    tmpdir = '/tmp/thisisatemporaryfolder/'
    if os.path.isdir(tmpdir): shutil.rmtree(tmpdir)
    os.makedirs(tmpdir, exist_ok=True)

    i = 0
    for fr in frameids:
        imgpath = pjoin(framedir, fr + ext)
        if not os.path.isfile(imgpath):
            info('File {} does not exist'.format(imgpath))
            continue
        img = Image.open(imgpath)
        img.thumbnail((res, res), Image.ANTIALIAS) # resizes 512x512 to 256x256
        img.save(pjoin(tmpdir, '{:04d}.png'.format(i)))
        i += 1
    cmd = '''ffmpeg -i {}/%04d.png {}'''.format(tmpdir, outpath)
    subprocess.check_output(cmd, shell=True)

##########################################################
def main(csvdir, datasetdir, outdir):
    """Short description"""
    info(inspect.stack()[0][3] + '()')
    classes = ['person', 'truck']
    camid = 5
    res = 640
    ext = '.jpg'
    for f in sorted(os.listdir(csvdir)):
        if not f.endswith('.csv'): continue
        info('{}'.format(f))
        csvpath = pjoin(csvdir, f)
        aux = re.match(r'road(\d+)_rec(\d+).csv', f)
        roadid, recordid = aux.group(1), aux.group(2)
        framedir = pjoin(datasetdir, 'road{}_ins'.format(roadid), 'ColorImage',
                         'Record{}'.format(recordid), 'Camera {}'.format(camid))
        df = pd.read_csv(csvpath)
        filename = '{}.gif'.format(f.replace('.csv', ''))
        outpath = pjoin(outdir, filename)
        generate_video(df.file.tolist(), ext, framedir, res, outpath)
        for _cls in classes:
            frameids = df.loc[df[_cls] == 1].file.tolist()
            outpath = outpath.replace('.gif', '_{}.gif'.format(_cls))
            generate_video(frameids, ext, framedir, res, outpath)

##########################################################
if __name__ == "__main__":
    info(datetime.date.today())
    t0 = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csvdir', required=True, help='Output from readlabels.py')
    parser.add_argument('--datasetdir', required=True, help='ApolloScape dataset root')
    parser.add_argument('--outdir', default='/tmp/out/', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    readmepath = create_readme(sys.argv, args.outdir)

    main(args.csvdir, args.datasetdir, args.outdir)

    info('Elapsed time:{:.02f}s'.format(time.time()-t0))
    info('Output generated in {}'.format(args.outdir))

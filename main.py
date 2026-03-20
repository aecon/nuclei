import os
import sys
import glob
import argparse

import numpy as np
import skimage.io

from nuclei import nuclei


# ----------------------------------------
# SETTINGS
# ----------------------------------------
basedir = '/media/user/SSD2/Simone/test'


# ----------------------------------------
# SOURCE CODE - DO NOT TOUCH
# ----------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--skip-existing', action='store_true', help='Skip images that already have labels')
args = parser.parse_args()

# check if input folder exists
if not os.path.exists(basedir):
    print("ERROR: basedir path is incorrect.")
    sys.exit()

files = sorted(glob.glob(basedir + '/**/*.tif', recursive=True))
files = [f for f in files if os.sep + 'labels' + os.sep not in f]

# always regenerate CSV files from scratch
csv_files = set()
for file in files:
    output_file = basedir + os.sep + "counts_" + os.path.dirname(file).split(basedir)[1].replace('/', '_').replace(' ', '') + ".csv"
    if output_file not in csv_files:
        csv_files.add(output_file)
        nuclei.write_header_static(output_file)

n = None  # lazy-init model only if needed
skipped = 0

Nfiles = len(files)
for i, file in enumerate(files):
    print("Processing image %d/%d:" % (i+1, Nfiles), file)

    output_file = basedir + os.sep + "counts_" + os.path.dirname(file).split(basedir)[1].replace('/', '_').replace(' ', '') + ".csv"
    output_folder = os.path.dirname(file) + os.sep + "labels"
    output_labels = output_folder + os.sep + os.path.basename(file) + "_labels.tif"

    # try to reuse existing labels from a previous run
    if args.skip_existing and os.path.exists(output_labels):
        try:
            labels = skimage.io.imread(output_labels, plugin='tifffile')
            Nnuclei = len(np.unique(labels)) - 1
            nuclei.write_data_static(output_file, file, Nnuclei)
            print("  Skipped (labels exist), nuclei:", Nnuclei)
            skipped += 1
            continue
        except Exception:
            print("  Corrupted labels file, re-processing...")

    # create output folder for labels
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # lazy-load model on first image that needs processing
    if n is None:
        n = nuclei()

    # read image
    try:
        img = skimage.io.imread(file, plugin='tifffile')
    except Exception as e:
        print("WARNING: Could not read file, skipping:", e)
        continue

    # process image
    Nnuclei, labels = n.process(img)

    # write counts in csv file
    n.write_data(output_file, file, Nnuclei)

    # export labels image
    skimage.io.imsave(output_labels, labels, plugin='tifffile', check_contrast=False)

print("Done! Processed %d/%d images. (%d skipped)" % (Nfiles - skipped, Nfiles, skipped))


import os
import sys
import glob

from nuclei import *


# ----------------------------------------
# MUST EDIT: GIVE PATH TO FOLDER CONTAINING ALL PLATES
# ----------------------------------------
basedir = '/media/user/SSD2/Simone/test'



# ----------------------------------------
# SOURCE CODE - DO NOT TOUCH
# ----------------------------------------

# check if input folder exists
if not os.path.exists(basedir):
    print("ERROR: basedir path is incorrect.")
    sys.exit()

files = sorted(glob.glob(basedir + '/**/*.tif', recursive=True))
files = [f for f in files if os.sep + 'labels' + os.sep not in f]

n = nuclei()

Nfiles = len(files)
for i,file in enumerate(files):
    print("Processing image %d/%d:" % (i+1, Nfiles), file)

    # 2025 04 01
    #base1 = os.path.basename( os.path.dirname( os.path.dirname(file)))
    #base2 = os.path.basename( os.path.dirname(file))
    #output_file   = os.path.dirname(file) + os.sep + "counts_%s.csv" % (base1+"_"+base2)

    # 2025 04 25 | 2025 05 05
    output_file = basedir + os.sep + "counts_" + os.path.dirname(file).split(basedir)[1].replace('/', '_').replace(' ', '') + ".csv"
    output_folder = os.path.dirname(file) + os.sep + "labels"
    output_labels = output_folder + os.sep + os.path.basename(file) + "_labels.tif"


    # create output file
    if not os.path.exists(output_file):
        n.write_header(output_file)

    # create output folder for labels
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

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

    # export labels image if there are nuclei
    if Nnuclei == 0:
        continue
    else:
        skimage.io.imsave(output_labels, labels, plugin='tifffile', check_contrast=False)
 

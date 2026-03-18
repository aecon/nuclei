import os
import sys
import glob
import argparse

import numpy as np
import skimage.io
import skimage.filters
import skimage.morphology
import tensorflow as tf

from stardist.models import StarDist2D
from csbdeep.utils import normalize


class nuclei():

    def __init__(self):
        # limit GPU usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # Load StarDist model
        self.model = StarDist2D.from_pretrained('2D_versatile_fluo')

        # Parameters
        # - pre process
        self.sigma_denoise = 2
        self.sigma_background = 50
        # - post process
        self.min_area = 300
        self.max_area = 15000


#    def pre_process(self, img):
#        """
#        Perform image normalization by dividing the 
#        denoised image with an estimate of the background
#        """
#        denoised   = skimage.filters.gaussian(img, sigma=self.sigma_denoise,    mode='nearest', preserve_range=True)
#        background = skimage.filters.gaussian(img, sigma=self.sigma_background, mode='nearest', preserve_range=True)
#        normalized = denoised / background
#        return normalized


    def post_process(self, labels, img):
        """
        Filter segmented nuclei based on area and brightness
        """
        # get number of detected objects and unique labels
        unique_labels, unique_counts = np.unique(labels, return_counts=True)
        Nlabels = np.shape(unique_labels)[0]

        # exclude very small and very large objects
        kept_labels = []
        avg_brightness = []
        for i in range(1,Nlabels):
            Vol = unique_counts[i]
            idx = (labels==unique_labels[i])
            # remove small objects
            if Vol<self.min_area:
                labels[idx] = 0
            # remove very large objects
            elif Vol>self.max_area:
                labels[idx] = 0
            else:
                kept_labels.append(unique_labels[i])
                avg_brightness.append(np.mean(img[idx]))
        avg_brightness = np.asarray(avg_brightness)

        # check if no nuclei were detected
        if len(avg_brightness) < 1:
            return 0, np.zeros_like(labels)

        # remove very dim and very bright objects
        bmax = np.percentile(avg_brightness, 98)
        bmin = np.percentile(avg_brightness, 2)
        for i, lbl in enumerate(kept_labels):
            idx = (labels==lbl)
            bavg = avg_brightness[i]
            if bavg<bmin:
                labels[idx] = 0
            if bavg>bmax:
                labels[idx] = 0

        # count number of cells after filters (exclude background label 0)
        Nnuclei = len(np.unique(labels)) - 1
        print("Number of nuclei:", Nnuclei)

        return Nnuclei, labels


    def process(self, img):
        #img = self.pre_process(img)
        labels, _ = self.model.predict_instances(normalize(img), predict_kwargs=dict(verbose=False))
        Nnuclei, labels = self.post_process(labels, img)
        return Nnuclei, labels


    def write_header(self, output_file):
        with open(output_file, 'w') as f:
            f.write("%s,%s\n" % ("Image", "NucleiCounts"))


    def write_data(self, output_file, file, Nnuclei):
        with open(output_file, 'a') as f:
            f.write("\"%s\",%d\n" % (os.path.basename(file), Nnuclei))



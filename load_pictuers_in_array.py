import cv2
import numpy as np
from os import listdir
import string


mypath_labels = './OID/Dataset/test/Human body_Duck/Label/'
mypath_img = './OID/Dataset/test/Human body_Duck/'

def load_images(wide, height, path):

    array = np.empty([0, wide, height, 3])

    names = [p for p in listdir(path)if p[-4:] == ".jpg"]

    for i in names:
        img = cv2.imread(path + i) / 255.
        img = cv2.resize(img, (wide, height), interpolation = cv2.INTER_AREA)
        img = np.expand_dims(img, 0)
        array = np.concatenate((array, img), axis=0)
        print(array.shape)
    return array
def load_labels(path):
    col_num = 0
    delimiter = " " 
    array_name = np.empty(0)
    names = [p for p in listdir(path)if p[-4:] == ".txt"]
    for name in names:
        file = open(path + name)
        data = file.readline().split(delimiter)[col_num] 
        array_name = np.append(array_name, data.strip('\n')) 
        print(path + name)
    return array_name

import matplotlib.pyplot as plt 
Y_train = load_labels(mypath_labels)
X_train = load_images(128, 128, mypath_img)
np.save('Y_test.npy', Y_train)
np.save('X_test.npy', X_train)

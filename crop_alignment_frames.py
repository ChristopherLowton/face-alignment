import math
from os.path import relpath
import os
import pandas as pd
import glob
from os import walk
import numpy as np
import re
from os.path import exists

video_frames = 29
video_length = 1.16

base_folder = "C:\\Users\\Chris\\Documents\\Lip Reading in the Wild Data\\lipread_mp4\\"

folders = [
    ""
]

files = []

for folder in folders:
    #Combine base folder path with folder names then convert to relative path for walk to process
    folder = relpath(base_folder + folder)

    #Find all files to process in folders
    for (dirpath, dirnames, filenames) in walk(folder):
        if (len(filenames) > 0):
            for file in filenames:
                if "_lips.txt" in file:
                    files.append(dirpath + "\\" + file)

def getDuration(path):
    f = open(path.split("_lips.txt")[0] + ".txt", "r")
    lines = f.readlines()
    
    duration = -1

    for line in lines:
        if "Duration" in line:
            duration = float(line.split(" ")[1])
    return duration

def get_related_files(path):
    related_files = []
    base_name = path.split("_lips.txt")[0]

    related_files.append(path)
    related_files.append(base_name + "_eye1.txt")
    related_files.append(base_name + "_eye2.txt")
    related_files.append(base_name + "_eyebrow1.txt")
    related_files.append(base_name + "_eyebrow2.txt")
    related_files.append(base_name + "_face.txt")
    related_files.append(base_name + "_lips-relative.txt")
    related_files.append(base_name + "_lips-vector.txt")
    related_files.append(base_name + "_nose.txt")
    related_files.append(base_name + "_nostril.txt")
    related_files.append(base_name + "_teeth.txt")

    return related_files

def format_line(line):
    line = line[1:]
    line = line[:-1]
    line = line.replace("\n ", ",")
    line = line.replace(".", "")
    line = line.replace(" ", ",")
    return line

def crop_coordinate_files(path, duration):
    related_files = get_related_files(path)

    min_frame = 0
    max_frame = video_frames

    if duration > 0:
        word_frames = (video_frames/video_length)*duration
        min_frame = math.floor((video_frames/2) - (word_frames/2))
        max_frame = math.ceil((video_frames/2) + (word_frames/2))

        for file in related_files:
            print(file)
            f = open(file, "r")
            coord_length = len(f.readline().replace("],[", "] [").replace("\n", "").split(" "))

            replacement = ""
            frame_index = 0
            f.seek(0)
            for line in f:
                if frame_index >= min_frame and frame_index <= max_frame:
                    replacement = replacement + line
                else:
                    replacement = replacement + format_line(str(np.zeros((coord_length, 2)))) + "\n"
                frame_index = frame_index + 1
            f.close()
            f_new = open(file.split(".txt")[0] + "_padding.txt", "w")
            f_new.write(replacement)
            f_new.close()



for file in files:
    duration = getDuration(file)
    crop_coordinate_files(file, duration)
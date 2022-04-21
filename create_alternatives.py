#This file processes a file containing 2D coordinates in order to convert the coordinate positions from absolute to relative and movement vectors

from os.path import relpath
import os
import pandas as pd
import glob
from os import walk
import numpy as np
import re
from os.path import exists

base_folder = "C:\\Users\\Chris\\Documents\\Lip Reading in the Wild Data\\lipread_mp4\\"

folders = [
    "HISTORY",
    "HOSPITAL",
    "INDUSTRY",
    "INFORMATION",
    "JAMES",
    "JUSTICE",
    "KILLED",
    "LEAST",
    "LEVELS",
    "LITTLE",
    "LIVING",
    "MAKES",
    "MATTER",
    "MEDIA",
    "NIGHT",
    "NORTH",
    "OFFICE",
    "OPERATION",
    "PARENTS",
    "PEOPLE",
    "PRICES",
    "PROCESS",
    "QUESTION",
    "RECENT",
    "RESULT",
    "SAYING",
    "SECURITY",
    "STRONG",
    "TALKING",
    "TEMPERATURES",
    "THEMSELVES",
    "UNDERSTAND",
    "WARNING",
    "WATCHING",
    "WHOLE",
    "YEARS",
    "YESTERDAY"
]

MAXFORWORD = 10000

delete_previous = False
validate_files = False

files = []

def read_face_alignment_data_file(path):
    data = []
    f = open(path, "r")
    for line in f:
        data_points = line.replace("],[", "] [").replace("\n", "").split(" ")
        for i, point in enumerate(data_points):
            point = re.sub(r",+", ",", point, 0, re.MULTILINE)
            data_points[i] = point.replace('[', '').replace(']','').split(',')
            splice_coords = []
            for coord_index, coord in enumerate(data_points[i]):
                #If empty coordinate splice from data as it will be a false value due to errors in the face alignment program
                if not coord or coord.isspace():
                    splice_coords.append(coord_index)
            #Remove invalid coordinates from data in reverse order so indexes aren't compromised
            for coord_index in sorted(splice_coords, reverse=True):
                data_points[i].pop(coord_index)
            data_points[i][0] = float(data_points[i][0])
            data_points[i][1] = float(data_points[i][1])
        data.append(data_points)
    #print(str(data))
    return data

def createVectorFile(path, data):
    print(path)
    vector_data = np.zeros((29, 12, 2))
    previousFrame = np.zeros((12, 2))
    for frame_idx, frame in enumerate(data):
        for coord_idx, coord in enumerate(frame):
            #Calculate a vector for each point from the previous frame to the current frame
            x = coord[0] - previousFrame[coord_idx][0]
            y = coord[1] - previousFrame[coord_idx][1]
            x = int(x)
            y = int(y)

            #If first frame replace with zeros as a starting point
            if frame_idx == 0:
                x = 0
                y = 0

            vector_data[frame_idx][coord_idx] = [x, y]
        previousFrame = frame

    for frame in vector_data:
        saveLine(path, frame, "vector")

def createRelativeFile(path, data):
    print(path)
    relative_data = np.zeros((29, 12, 2))
    for frame_idx, frame in enumerate(data):

        #Calculate centre for each frame so head or body movement doesn't effect the results
        xMax = 0
        xMin = 0
        yMax = 0
        yMin = 0
        for coord_idx, coord in enumerate(frame):
            if (coord_idx == 0):
                xMax = coord[0]
                xMin = coord[0]
                yMax = coord[1]
                yMin = coord[1]

            if coord[0] > xMax:
                xMax = coord[0]
            if coord[0] < xMin:
                xMin = coord[0]

            if coord[1] > yMax:
                yMax = coord[1]
            if coord[1] < yMin:
                yMin = coord[1]
        centre = getCentre(xMax, xMin, yMax, yMin)
        
        for coord_idx, coord in enumerate(frame):
            #Convert to relative coordinate based on the center of the lips data for each frame
            x = coord[0] - centre[0]
            y = coord[1] - centre[1]
            relative_data[frame_idx][coord_idx] = [x, y]

    for frame in relative_data:
        saveLine(path, frame, "relative")

def getCentre(xMax, xMin, yMax, yMin):
    xMid = float(xMin) + ((float(xMax) - float(xMin)) / 2)
    yMid = float(yMin) + ((float(yMax) - float(yMin)) / 2)
    centre = [xMid, yMid]
    return centre

def convertPath(path, type):
    filename = "".join(path.rsplit(".txt", 1))
    filename = filename + "-" + type + ".txt"
    return filename

def saveLine(path, data, type):
    filename = convertPath(path, type)

    f = open(filename, "a")
    data = str(data)
    data = formatData(data)
    f.write(data + "\n")

def formatData(data):
    #trim whitespace from start and end of numbers
    data = re.sub(r"(\[)[\s]+", "[", data, 0, re.MULTILINE)
    data = re.sub(r"[\s]+(\[)[\s]+", ",[", data, 0, re.MULTILINE)

    data = data.replace("\n", "")
    data = data.replace("[", "", 1)
    # #Replace last ] character with nothing
    data = "".join(data.rsplit("]", 1))

    #Replace whitespace with comma
    data = re.sub(r"\s+",',',data)

    data = data.replace(".,", ".0,")
    data = data.replace(".]", ".0]")
    return data
files = []

for folder in folders:
    #Combine base folder path with folder names then convert to relative path for walk to process
    folder = relpath(base_folder + folder)
    for (dirpath, dirnames, filenames) in walk(folder):
        if (len(filenames) > 0):
            for file in filenames:
                if "_lips.txt" in file:
                    if int(file.split("_")[1]) <= MAXFORWORD:
                        files.append(dirpath + "\\" + file)

for file in files:
    relative_path = convertPath(file, "relative")
    if delete_previous == True and os.path.exists(relative_path):
        os.remove(relative_path)
    if exists(relative_path) == False:
        data = read_face_alignment_data_file(file)
        createRelativeFile(file, data)
    elif validate_files == True and len(open(relative_path, "r").readlines()) < 29:
        os.remove(relative_path)
        data = read_face_alignment_data_file(file)
        createRelativeFile(file, data)

    vector_path = convertPath(file, "vector")
    if delete_previous == True and os.path.exists(vector_path):
        os.remove(vector_path)
    if exists(vector_path) == False:
        data = read_face_alignment_data_file(relative_path)
        createVectorFile(file, data)
    elif validate_files == True and len(open(vector_path, "r").readlines()) < 29:
        os.remove(vector_path)
        data = read_face_alignment_data_file(relative_path)
        createVectorFile(file, data)
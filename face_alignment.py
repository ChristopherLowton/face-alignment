import math
import os
import face_alignment
from skimage import io
import cv2
from os.path import relpath
from os import walk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import collections
import re
import datetime
import numpy as np

IMG_SIZE = 256
preview_frames = False
video_length = 1.16
video_frames = 29

fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device='cuda')

pred_type = collections.namedtuple('prediction_type', ['slice', 'color'])
pred_types = {'face': pred_type(slice(0, 17), (0.682, 0.780, 0.909, 0.5)),
              'eyebrow1': pred_type(slice(17, 22), (1.0, 0.498, 0.055, 0.4)),
              'eyebrow2': pred_type(slice(22, 27), (1.0, 0.498, 0.055, 0.4)),
              'nose': pred_type(slice(27, 31), (0.345, 0.239, 0.443, 0.4)),
              'nostril': pred_type(slice(31, 36), (0.345, 0.239, 0.443, 0.4)),
              'eye1': pred_type(slice(36, 42), (0.596, 0.875, 0.541, 0.3)),
              'eye2': pred_type(slice(42, 48), (0.596, 0.875, 0.541, 0.3)),
              'lips': pred_type(slice(48, 60), (0.596, 0.875, 0.541, 0.3)),
              'teeth': pred_type(slice(60, 68), (0.596, 0.875, 0.541, 0.4))
              }

key_list = list(pred_types.keys())
values_list = list(pred_types.values())

# 2D-Plot
plot_style = dict(marker='o',
                  markersize=4,
                  linestyle='-',
                  lw=2)

def crop_center_square(frame):
    y, x = frame.shape[0:2]
    min_dim = min(y, x)
    start_x = (x // 2) - (min_dim // 2)
    start_y = (y // 2) - (min_dim // 2)
    return frame[start_y : start_y + min_dim, start_x : start_x + min_dim]

def load_video(path, max_frames=0, resize=(IMG_SIZE, IMG_SIZE)):
    print(path)
    cap = cv2.VideoCapture(path)
    frames = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = crop_center_square(frame)
            frame = cv2.resize(frame, resize)
            # frame = frame[:, :, [2, 1, 0]]

            preds = fa.get_landmarks(frame)[-1]

            for pred_type in pred_types:
                saveData(path, preds, str(pred_type), pred_types[pred_type].slice.start, pred_types[pred_type].slice.stop)

            if preview_frames:
                showFrames(frame, preds)
            
            #print(str(preds))

            frames.append(frame)
            # cv2.imshow('frame', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            if len(frames) == max_frames:
                break
    finally:
        cap.release()
    # return np.array(frames)

def showFrames(frame, preds):
    fig = plt.figure(figsize=plt.figaspect(.5))
    ax = fig.add_subplot(1, 2, 1)
    ax.imshow(frame)

    for pred_type in pred_types.values():
        ax.plot(preds[pred_type.slice, 0],
                preds[pred_type.slice, 1],
                color=pred_type.color, **plot_style)
    ax.axis('off')
    plt.show()

def saveData(path, preds, type, start, stop):
    filename = "".join(path.rsplit(".mp4", 1))
    filename = filename + "_" + type + ".txt"
    f = open(filename, "a")
    data = str(preds[start:stop])
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

print("-------------------------")

base_folder = "C:\\Users\\Chris\\Documents\\Lip Reading in the Wild Data\\lipread_mp4\\"

folders = [
    "ABOUT",
    "ABSOLUTELY",
    "ABUSE"
]

files = []

#File number to start from in every folder, inclusively.
start_file_number = 0
MAX_FILES = 50000000
for folder in folders:
    #Combine base folder path with folder names then convert to relative path for walk to process
    folder = relpath(base_folder + folder)
    
    #Find all files to process in folders
    for (dirpath, dirnames, filenames) in walk(folder):
        if (len(filenames) > 0):
            for file in filenames:
                if ".mp4" in file:
                    file_number = int(file.split("_")[1].split(".")[0])
                    if file_number <= MAX_FILES and file_number >= start_file_number:
                        files.append(dirpath + "\\" + file)


print(str(len(files)) + " total files to process")

start_time = datetime.datetime.now()
print("Start time: " + str(start_time))

print("-------------------------")

for file in files:
    load_video(file)

print("-------------------------")

end_time = datetime.datetime.now()
print("End time: " + str(end_time))

total_time = end_time - start_time
print("Total time: " + str(total_time))

print("-------------------------")

print(str(len(files)) + " total files processed")

time_per_file = total_time / len(files)
print("Time per file: " + str(time_per_file))

print("-------------------------")
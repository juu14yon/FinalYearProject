import cv2
import csv
import os
from HeadTilt import HeadTilt

WIDTH, HEIGHT = 1366, 768
COORDINATES = []
for y in range(0, HEIGHT + 1, HEIGHT//10):
    for x in range(0, WIDTH + 1, WIDTH//20):
        COORDINATES.append([x, y])


distance = 50 # centimeter
ht = HeadTilt()

file = open("data/data.csv", mode='a', newline='')
writer = csv.writer(file)
new_row = [
            "alpha", "beta",
            "distance", 
            "lpx", "lpy", 
            "lvx", "lvy", "lvz",
            "rpx", "rpy", 
            "rvx", "rvy", "rvz", 
            "x", "y"]

writer.writerow(new_row)

parent='./data/'
folders = [f for f in os.listdir(parent) if os.path.isdir(os.path.join(parent, f))]

for f in folders:
    for i in range(1, 232):
        path = "data/" + f + "/" + str(i) + ".jpg"
        if not os.path.isfile(path):
            continue

        frame = cv2.imread(path)

        frame.flags.writeable = False
        ht.start(frame)
        frame.flags.writeable = True

        flag, alpha, beta = ht.angles()

        left_d = ht.diameter("L")
        right_d = ht.diameter("R")  
        irisDiam = max(left_d, right_d)
        distance = 90 - (irisDiam - 1)*2.5
        leftp1, leftp2, rightp1, rightp2 = ht.gaze(distance)

        x, y = COORDINATES[i-1]

        if ht.isFace and len(leftp1)>1:
            new_row = [
                        alpha, beta,
                        distance, 
                        leftp1[0], leftp1[1], 
                        ht.vecLeft[0], ht.vecLeft[1], ht.vecLeft[2],
                        rightp1[0], rightp1[1], 
                        ht.vecRight[0], ht.vecRight[1], ht.vecRight[2], 
                        x, y]

            writer.writerow(new_row)
        else:
            print(path)


import pandas as pd
import numpy as np
import cv2

# Read csv of predicted points
df = pd.read_csv("csv/predicted-RF.csv")
df.sort_values(by=['y1', 'x1'], inplace=True)

# Start video writing
file_name = f'visualized.mp4'
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
captured_video = cv2.VideoWriter(file_name, fourcc, 10.0, (1366, 768))

# Visualise actual and predicted points
for index, row in df.iterrows():
    img = np.zeros([768, 1366, 3], dtype=np.uint8)
    point = (int(row["x1"]), int(row["y1"]))
    pred = (int(row["x2"]), int(row["y2"]))
    cv2.circle(img, pred, 1, [100, 0, 255], 60)
    cv2.circle(img, point, 1, [0, 0, 255], 10)
    cv2.line(img, point, pred, [0, 0, 100], 1)
    captured_video.write(img)
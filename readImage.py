import numpy as np
import math
from PIL import Image

im = Image.open("TestImage1c.jpg")
print(im.format, im.size, im.mode)
col, row = im.size
data = np.zeros((row * col, 3))
pixels = im.load()
print col, row
for i in range(row):
    for j in range(col):
        r, g, b = pixels[j, i]
        data[col * i + j, :] = r, g, b
grayscale = np.zeros(row * col)
for i in range(row):
    for j in range(col):
        grayscale[col * i + j] = data[col * i + j, 0] * 0.3 + data[col * i + j, 1] * 0.59 + data[col * i + j, 2] * 0.11
grayscale.resize((row, col))
# im = Image.fromarray(grayscale)
# im.show()
# greyscale done

sobel = np.zeros((row, col, 2))
magnitude = np.zeros((row, col))
thita = np.zeros((row, col))
# Gx, Gy, G, thita
max = 0
min = 9999

threshold = 100
for i in range(1, row - 1):
    for j in range(1, col - 1):
        sobel[i, j, 0] = grayscale[i - 1, j + 1] + 2 * grayscale[i, j + 1] + grayscale[i + 1, j + 1] \
                         - grayscale[i - 1, j - 1] - 2 * grayscale[i, j - 1] - grayscale[i + 1, j - 1]
        sobel[i, j, 1] = grayscale[i - 1, j - 1] + 2 * grayscale[i - 1, j] + grayscale[i - 1, j + 1] \
                         - grayscale[i + 1, j - 1] - 2 * grayscale[i + 1, j] - grayscale[i + 1, j + 1]
        magnitude[i, j] = (sobel[i, j, 0] ** 2 + sobel[i, j, 1] ** 2) ** 0.5
        if sobel[i, j, 0] == 0:
            thita[i, j] = math.atan(sobel[i, j, 1] / 0.01)
        else:
            thita[i, j] = math.atan(sobel[i, j, 1] / sobel[i, j, 0])
        if magnitude[i, j] > max:
            max = magnitude[i, j]
        if magnitude[i, j] < min:
            min = magnitude[i, j]
print max, min
count = 0
for i in range(1, row - 1):
    for j in range(1, col - 1):
        magnitude[i, j] = magnitude[i, j] / max * 255
        if magnitude[i, j] > threshold:
            magnitude[i, j] = 255
            count += 1
        else:
            magnitude[i, j] = 0
# shrink = magnitude
# shrink
# for i in range (1, row -1 ):
#     for j in range(1, col-1):
#         if (magnitude[i-1,j-1]==0) | (magnitude[i-1,j]==0) | (magnitude[i+1,j]==0) | (magnitude[i+1,j+1]==0):
#             shrink[i,j]=0

# im = Image.fromarray(magnitude)
# im.show()

point = np.zeros((count, 2))
count = 0
for i in range(1, row - 1):
    for j in range(1, col - 1):
        if magnitude[i, j] == 255:
            point[count, :] = i, j
            count += 1

# hough transform
angle = 720
p = 4000
hough = np.zeros((angle, p))
for i in range(count):
    for j in range(i + 1, count):
        x1, y1 = point[i, :]
        x2, y2 = point[j, :]
        if y1 == y2:
            tmpAngle = math.atan((x2 - x1) / 0.001)
        else:
            tmpAngle = math.atan((x2 - x1) / (y1 - y2))
        tmpP = x1 * math.cos(tmpAngle) + y1 * math.sin(tmpAngle)
        tmpAngle = tmpAngle / (2 * math.pi) * 360
        if tmpAngle < 0: tmpAngle = tmpAngle + 360
        tmpAngle = int(tmpAngle * 2)
        tmpP = int(tmpP)+2000
        hough[tmpAngle, tmpP] += 1

threshold = 100
for i in range(angle):
    for j in range(p):
        if hough[i, j] > threshold:
            count += 1

effectiveHough = np.zeros((count, 3))
count = 0
for i in range(0, angle):
    for j in range(0, p):
        tmp = hough[i, j]
        top = 0 if i - 3 < 0 else i - 3
        bottom = angle - 1 if i + 3 > angle - 1 else i + 3
        left = 0 if j - 3 < 0 else j - 3
        right = p - 1 if j + 3 > p - 1 else j + 3
        maxFlag = 1
        for k in range(top, bottom + 1):
            for l in range(left, right + 1):
                if tmp < hough[k, l]:
                    maxFlag = 0
        if (tmp > threshold) and maxFlag == 1:
            effectiveHough[count, :] = hough[i, j], i, j
            count += 1
print count

# for i in range(100):
#     print effectiveHough[i,0]

for i in range(count):
    for j in range(i + 1, count):
        if effectiveHough[i, 0] < effectiveHough[j, 0]:
            tmpNum, tmpAngle, tmpP = effectiveHough[i, :]
            effectiveHough[i] = effectiveHough[j]
            effectiveHough[j] = tmpNum, tmpAngle, tmpP

for i in range(100):
    print effectiveHough[i]

for i in range(row):
    for j in range(col):
        for k in range(4):
            if int(i * math.cos(effectiveHough[k, 1] / 720.0 * 2 * math.pi) +
                                   j * math.sin(effectiveHough[k, 1] / 720.0 * 2 * math.pi)) - effectiveHough[
                k, 2] +2000 == 0:
                magnitude[i, j] = 255

im = Image.fromarray(magnitude)
im.show()

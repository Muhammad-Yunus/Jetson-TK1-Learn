import cv2
import numpy as np

def test(img, N, S):
    t0 = cv2.getTickCount()
    for i in range(N):
        blur= cv2.pyrMeanShiftFiltering(img,21,49)
        gray_image= cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
    t1 = cv2.getTickCount()
    print ("%s:\t%d iterations took %f seconds." % (S, N, (t1-t0)/cv2.getTickFrequency()))


img = cv2.imread("captured_photo.jpg")
print("image size: ", img.shape)

N = 100
test(img, N, "Mat")
test(cv2.UMat(img), N, "UMat")

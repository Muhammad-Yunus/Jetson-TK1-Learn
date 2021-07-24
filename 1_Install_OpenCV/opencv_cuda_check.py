import cv2
count = cv2.cuda.getCudaEnabledDeviceCount()
print("Number of CUDA device : %d" % count)

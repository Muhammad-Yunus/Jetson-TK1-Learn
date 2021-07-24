import cv2

cap = cv2.VideoCapture(0)

ret, img = cap.read()

if ret : 
	cv2.imwrite("captured_photo.jpg", img)
else :
	print("Error when capturing photo")

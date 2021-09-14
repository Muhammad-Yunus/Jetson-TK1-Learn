import cv2

e1 = cv2.getTickCount()
img = cv2.imread("lena.jpg", cv2.IMREAD_COLOR)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, (0,0), fx=30, fy=30)
gray = cv2.GaussianBlur(gray, (7, 7), 1.5)
gray = cv2.Canny(gray, 0, 50)
gray = cv2.resize(gray, (0,0), fx=0.033, fy=0.033)
e2 = cv2.getTickCount()
t = (e2 - e1)/cv2.getTickFrequency()
print( t )

cv2.imshow("edges", gray)
cv2.waitKey()
cv2.destroyAllWindows()
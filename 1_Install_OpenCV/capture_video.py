import cv2

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        cv2.imshow('frame',frame)
        if cv2.waitKey(10) == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
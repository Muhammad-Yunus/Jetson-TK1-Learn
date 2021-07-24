from flask import Flask, render_template, Response

import cv2
import json 
import datetime
import numpy as np
import queue
import threading

from utils import Utils
utils = Utils()
print("[INFO] finish import module!")

#classesFile = "batman-superman.json"
classesFile = "coco.json"
with open(classesFile) as json_labels :
    classes = json.load(json_labels)
print("[INFO] finish load class data!")

# load petrained model (.pb & .pbtxt) faster R-CNN with backbone Inception V2
#modelConfiguration = "model/yolov3-tiny.cfg"
#modelWeights = "model/yolov3-tiny-custom.weights"
modelConfiguration = "model/coco_yolov3-tiny.cfg"
modelWeights = "model/coco_yolov3-tiny.weights"
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
print("[INFO] finish load model!")

# set CUDA as backend & target OpenCV DNN
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# get output layers
layerOutput = [net.getLayerNames()[-1]]
print("[INFO] finish preparation!")

class YOLO():
    def __init__(self):
        self.output = []
        self.frame = []

        # parameter
        self.target_w = 224
        self.target_h = 224

    def main(self):
         if self.frame != [] :
             blob = cv2.dnn.blobFromImage(
                         self.frame, 
                         1/255, 
                         (self.target_w, self.target_h), 
                         [0, 0, 0],
                         1, 
                         crop=False)
 
             # predict classess & box
             net.setInput(blob)
             self.output = net.forward(layerOutput)
             
             t, _ = net.getPerfProfile()
             print('inference time: %.2f s' % (t / cv2.getTickFrequency()))

    def detect_object(self, frame):
        self.frame = frame

        if self.output != [] :
            return utils.postprocess(self.output, frame, classes, font_size=0.8, color_maps=color_maps)
        else :
            return frame
      
      
class CustomVideoCapture():
    def __init__(self, name):
        self.name = name
        self.cap = cv2.VideoCapture(self.name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while self.cap.isOpened() :
            ret, frame = self.cap.read()
            if not ret :
                self.cap.release()
                print("[INFO] Invalid image!")

                print("[INFO] Restart camera in 2 seconds!")
                time.sleep(2)

                print("[INFO] Initialize new camera!")
                self.cap = None
                while self.cap == None :
                    try :
                        self.cap = cv2.VideoCapture(self.name)
                    except Exception as e:
                        print("[ERROR] 'error when initialize camera,' ", e)
                        time.sleep(1)
                continue
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        try :
            return True, self.q.get()
        except Exception as e:
            print("[ERROR] Custom Video Capture read,", e)
            return False, None

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        return self.cap.release()

      
app = Flask(__name__)
yolo = YOLO()
print("[INFO] finish create app & yolo object!")

camera = CustomVideoCapture(0) #cv2.VideoCapture(0)
print("[INFO] finish open camera!")

color_maps = {}
for key in classes :
    color_maps[key] = (np.random.randint(0,255), 
                       np.random.randint(0,255), 
                       np.random.randint(0,255))


def gen_frames():  
    while True:
        try :
          success, frame = camera.read()
          if not success:
              break
          else:
              frame = frame[:, 80:-80]
  
              yolo.main()
              frame  = yolo.detect_object(frame)
              ret, buffer = cv2.imencode('.jpg', frame)
              frame = buffer.tostring()
  
              yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except :
          camera.release()
          print("[INFO] program stopped!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    print("[INFO] load path /video_feed!")
    return Response(gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try : 
      app.run(host="0.0.0.0")
    except KeyboardInterrupt:
      camera.release()
      print("[INFO] program stopped!")
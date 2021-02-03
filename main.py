from flask import Flask, request, render_template, redirect, url_for, send_file, Response
from os import listdir

import os
import time
import imutils
import cv2
import sys
import numpy as np

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
  movies = [ filename for filename in listdir('./static/data') if not filename.startswith('.') ]

  return render_template("index.html", movies=movies)

@app.route('/video_feed')
def video_feed():
  video = cv2.VideoCapture('baby.mov')
  return Response(gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(video):

  while True:
    success, image = video.read()
    ret, jpeg = cv2.imencode('.jpg', image)
    frame = jpeg.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/download', methods=['POST'])
def download():
  mv =  request.form["movie"]
  DLfile = './static/data/'+ mv
  return send_file(DLfile, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():

  # 画像処理
  # img = cv2.imread('aa.jpeg')
  # img_gs = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # cv2.imwrite('./static/data/aaa.jpeg', img_gs)

  fs = request.files['file']
  video_path = os.path.join('./static/data/',fs.filename)
  fs.save(video_path)

  # time.sleep(2)

  cap = cv2.VideoCapture(video_path)
  # cap = cv2.VideoCapture('baby.mov')

  fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
  out = cv2.VideoWriter(video_path, fourcc, 20.0, (320, 568), isColor=False)

  # while(cap.isOpened()):
  while True:
    ret, frame = cap.read()
    if ret == True:
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      # print(out)
      # cv2.imshow('view', gray);
      out.write(gray)
      if cv2.waitKey(1) & 0xFF == 27:
        break
    else:
      break

  out.release()
  cap.release()
  cv2.destroyAllWindows()

  return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, threaded=True)

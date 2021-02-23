from flask import Flask, request, render_template, redirect, url_for, send_file, Response
from os import listdir
from datetime import datetime

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

  fs = request.files['file']
  date = datetime.now().strftime("%y%m%d%H%M%S")
  video_path = os.path.join('./static/data/', fs.filename.split('.', 1)[0] + date + ".mov")
  fs.save(video_path)

  time.sleep(3)

  cap = cv2.VideoCapture(video_path)

  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  fps = int(cap.get(cv2.CAP_PROP_FPS))

  fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
  out = cv2.VideoWriter(video_path, fourcc, fps, (width, height), isColor=False)

  for x in range(1, count):
    ret, frame = cap.read()
    if ret:
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      out.write(gray)
    else:
      print(x)

  out.release()
  cap.release()
  cv2.destroyAllWindows()

  return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, threaded=True)

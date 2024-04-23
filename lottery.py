import cv2
import time
import shutil
import numpy as np
import pytesseract
from pytesseract import Output
from fastapi import FastAPI, File, UploadFile
from typing import Annotated
#print(cv2.__version__)

app = FastAPI()

start = time.time()
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
end = time.time()

def GetData(label_no_crop):
  label_no_crop_gray = cv2.cvtColor(label_no_crop, cv2.COLOR_BGR2GRAY)
  th, threshold = cv2.threshold(label_no_crop_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  
  imag2char = pytesseract.image_to_string(threshold, lang="eng")
  return imag2char

def FileCrop(url):
  img = cv2.imread(url)
  d = pytesseract.image_to_data(img, output_type=Output.DICT)

  n_boxes = len(d['text'])
  for i in range(n_boxes):
      if int(float(d['conf'][i])) > 60:
          (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
          img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
  
  #ตัวเลขเบอร์
  img = cv2.rectangle(img, (280, 20), (520, 70), ( 9, 9, 255), 2)
  label_no_crop=img[20:70,280:520]
  return label_no_crop

@app.get("/")
def read_root():
  return {"Hello": "Api Thai lottery OCR"}
 
@app.post("/lotto/")
async def create_upload_file(uploaded_file: UploadFile = File(...)):
    file_location = f"files/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
      shutil.copyfileobj(uploaded_file.file, file_object) 
      
    sfile = FileCrop(file_location)
    label_no = GetData(sfile).replace("\n","").replace(" ","")
    return {"no": label_no}
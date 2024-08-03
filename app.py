from fastapi import FastAPI, Request, File, UploadFile
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import numpy as np
import time
import io
import cv2
import pytesseract
from pytesseract import Output
import uvicorn

class ImageType(BaseModel):
 url: str

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

def read_img(img):
  label_no_crop_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  th, label_no_crop_gray = cv2.threshold(label_no_crop_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  
  text = pytesseract.image_to_string(label_no_crop_gray, lang="eng")
  return(text)

@app.get("/")
def welcome(request: Request):
  return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/lotto")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
 
@app.post("/lotto/extract_text")
async def extract_text(request: Request):
    label = ""
    if request.method == "POST":
        form = await request.form()
        # file = form["upload_file"].file
        contents = await form["upload_file"].read()
        image_stream = io.BytesIO(contents)
        image_stream.seek(0)
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)     
        imgs = cv2.rectangle(frame, (280, 20), (520, 70), ( 9, 9, 255), 2)
        label_no_crop=imgs[20:70,280:520]        
        label =  read_img(label_no_crop)
 
    return templates.TemplateResponse("index.html", {"request": request, "label": label})

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=80, log_level="info", reload=True, workers=1)

#async def create_upload_file(uploaded_file: UploadFile = File(...)):
#    file_location = f"files/{uploaded_file.filename}"
#    with open(file_location, "wb+") as file_object:
#      shutil.copyfileobj(uploaded_file.file, file_object) 
#      
#    sfile = FileCrop(file_location)
#    label_no = GetData(sfile).replace("\n","").replace(" ","")
#    return {"no": label_no}

#if __name__ == "__main__":
#    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
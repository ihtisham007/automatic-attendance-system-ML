# Automated Attendance System

"""
Automated Attendance System

This project is an Automated Attendance System using Image Processing and Text Analysis.

## Requirements

- python >= 3.12.2
- dlib==19.24.0
- numpy==1.24.2
- Pillow==9.4.0
- face-recognition==1.3.0
- easyocr==latest

You can install them using the following command:

```bash
pip install -r requirements.txt
```

## Console Arguments 
- For Face Detection
````bash
python ./main.py --detection-type=face
````
- For Text Extraction
``````bash
python ./main.py  --detection-type=text
``````

- Run Backend API
```bash
cd API
```
```bash
npm i
```
```bash
npm start 
```
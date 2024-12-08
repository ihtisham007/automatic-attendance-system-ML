import argparse
import pickle
from tkinter import messagebox
import src.image_processing.face_detection_gui as face_detection
import src.text_analysis.main as text_detection
import tkinter as tk
from pathlib import Path
import face_recognition

# Create the parser
parser = argparse.ArgumentParser(description='Run detection type based on command-line argument.')
# Add the 'detection-type' argument
parser.add_argument('--detection-type', type=str, help='Type of detection to run: face or text')

# Parse the arguments
args = parser.parse_args()

import dlib
print(dlib.cuda.get_num_devices())

def encode_known_faces(
        encoding_location, model
) -> None:
    """
    Loads images in the training directory and builds a dictionary of their
    names and encodings.
    """

    names = []
    encodings = []

    for filepath in Path("images/training/face/").glob("*/*"):
        name = filepath.parent.name
        image = face_recognition.load_image_file(filepath)

        face_locations = face_recognition.face_locations(image, model=model)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding in face_encodings:
            names.append(name)
            encodings.append(encoding)

    name_encodings = {"names": names, "encodings": encodings}
    with encoding_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)
    messagebox.showinfo("Training Complete", "Model has been trained successfully!")

if __name__ == "__main__":
    # Check the 'detection-type' argument value
    if args.detection_type == 'face':
        face_detection.faceDetection()
    elif args.detection_type == 'text':
        root = text_detection.tk.Tk()
        app = text_detection.OCRGui(root)
        root.mainloop()
    elif args.detection_type == 'folder_trigger':
        print('Updating Encoded Model For New Student Be Patient (Working).....')
        encode_known_faces(Path('./output/encodings.pkl'),"HOG")
        print("Completed")



import tkinter as tk
from tkinter import filedialog, messagebox, Radiobutton, StringVar
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageTk, ImageFont
import face_recognition
import pickle
import requests
import cv2
import threading

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")
        self.BOUNDING_BOX_COLOR = "blue"
        self.TEXT_COLOR = "white"
        self.attendance_marked = []
        self.model_var = StringVar(value="hog")
        self.request_url = "http://localhost:3000/api/v1/student/"

        self.label = tk.Label(root, text="Select an option: (HOG for CPU Processing and CNN For GPU Processing)")
        self.label.grid(row=0, columnspan=2, pady=10)

        self.hog_radio = Radiobutton(root, text="HOG Model", variable=self.model_var, value="hog")
        self.hog_radio.grid(row=1, column=0)
        self.cnn_radio = Radiobutton(root, text="CNN Model", variable=self.model_var, value="cnn")
        self.cnn_radio.grid(row=1, column=1)

        self.test_button = tk.Button(root, text="Take Attendance with Image", command=self.test_model)
        self.test_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.webcam_button = tk.Button(root, text="Take Attendance from Webcam", command=self.start_webcam)
        self.webcam_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.load_images()

        self.video_capture = None
        self.thread_running = False

        self.encodings = self.load_encodings()

    def load_images(self):
        label_simple_txt = tk.Label(self.root, text="Simple Image")
        label_simple_txt.grid(row=6, column=0, pady=7)

        desired_width, desired_height = 500, 500
        image = Image.open('images/un_detected_image.jpeg').resize((desired_width, desired_height))
        image_1 = ImageTk.PhotoImage(image)
        self.simple_image = tk.Label(self.root, image=image_1)
        self.simple_image.image = image_1
        self.simple_image.grid(row=7, column=0, pady=10)

        label_detected_txt = tk.Label(self.root, text="Detected Image")
        label_detected_txt.grid(row=6, column=1, pady=17)

        image_2 = ImageTk.PhotoImage(Image.open('images/detected_image.jpeg').resize((desired_width, desired_height)))
        self.detected_image = tk.Label(self.root, image=image_2)
        self.detected_image.image = image_2
        self.detected_image.grid(row=7, column=1, pady=10)

    def load_encodings(self):
        try:
            with self.DEFAULT_ENCODINGS_PATH.open(mode="rb") as f:
                return pickle.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading encodings: {e}")
            return {"names": [], "encodings": []}

    def update_displayed_image(self, image_path, image_type):
        new_img = ImageTk.PhotoImage(Image.open(image_path).resize((500, 500)))
        if image_type == "sample":
            self.simple_image.config(image=new_img)
            self.simple_image.image = new_img
        else:
            self.detected_image.config(image=new_img)
            self.detected_image.image = new_img

    def test_model(self):
        file_path = filedialog.askopenfilename(title="Select an image file")
        if file_path:
            self.update_displayed_image(file_path, "sample")
            self.recognize_faces(image_location=file_path, model=self.model_var.get())
        else:
            messagebox.showwarning("No File Selected", "Please select an image file.")

    def start_webcam(self):
        self.video_capture = cv2.VideoCapture(0)
        self.thread_running = True
        threading.Thread(target=self.process_webcam).start()

    def process_webcam(self):
        while self.thread_running:
            ret, frame = self.video_capture.read()
            if ret:
                frame = self.recognize_faces_from_frame(frame, self.model_var.get())
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.thread_running = False
                    break
            else:
                print("Failed to capture frame from webcam.")
        self.video_capture.release()
        cv2.destroyAllWindows()

    def recognize_faces_from_frame(self, frame, model):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model=model)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name, accuracy = self._recognize_face(face_encoding)
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            label = f"{name} ({accuracy:.2f})"
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            if name not in self.attendance_marked:
                response = requests.post(self.request_url + name + "/saveattendance", json={})
                if response.status_code == 201:
                    response_data = response.json()
                    messagebox.showinfo("Attendance Marked", f"{response_data['studentBio']['name']} is marked present.")
                    self.attendance_marked.append(name)
        return frame

    def _recognize_face(self, unknown_encoding):
        matches = face_recognition.compare_faces(self.encodings["encodings"], unknown_encoding)
        distances = face_recognition.face_distance(self.encodings["encodings"], unknown_encoding)
        best_match_index = None
        accuracy = 0.0
        if matches:
            best_match_index = min(range(len(distances)), key=distances.__getitem__)
            accuracy = 1 - distances[best_match_index]
        if best_match_index is not None and matches[best_match_index]:
            return self.encodings["names"][best_match_index], accuracy
        return "Unknown", accuracy

    def recognize_faces(self, image_location: str, model: str = "hog") -> None:
        input_image = face_recognition.load_image_file(image_location)
        input_face_locations = face_recognition.face_locations(input_image, model=model)
        input_face_encodings = face_recognition.face_encodings(input_image, input_face_locations)

        pillow_image = Image.fromarray(input_image)
        draw = ImageDraw.Draw(pillow_image)

        for bounding_box, unknown_encoding in zip(input_face_locations, input_face_encodings):
            name, accuracy = self._recognize_face(unknown_encoding)
            if name != "Unknown":
                response = requests.post(self.request_url + name + "/saveattendance", json={})
                if response.status_code == 201:
                    response_data = response.json()
                    # print("Attendance Marked", f"{response_data['studentBio']['name']} is marked present.")
            self._display_face(draw, bounding_box, name, accuracy)

        del draw
        output_image_path = Path("output/detected_images/") / f"{Path(image_location).stem}_annotated.jpg"
        pillow_image.save(output_image_path)
        self.update_displayed_image(output_image_path, "detected")

    def _display_face(self, draw, bounding_box, name, accuracy):
        top, right, bottom, left = bounding_box
        draw.rectangle(((left, top), (right, bottom)), outline=self.BOUNDING_BOX_COLOR)
        label = f"{name} ({accuracy:.2f})"
        font = ImageFont.truetype("arial.ttf", size=min((right - left) // len(label), (bottom - top) // 2))
        draw.text((left, top), label, fill=self.TEXT_COLOR, font=font)

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

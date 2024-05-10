import tkinter as tk
from tkinter import filedialog, messagebox, Radiobutton, StringVar
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageTk, ImageFont
import face_recognition
import pickle
import requests
import cv2
import os

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")
        self.BOUNDING_BOX_COLOR = "blue"
        self.TEXT_COLOR = "white"
        self.attendance_marked = []

        self.label = tk.Label(root, text="Select an option: (HOG for CPU Processing and CNN For GPU Processing)")
        self.label.grid(row=0, columnspan=2, pady=10)

        self.model_var = StringVar()
        self.model_var.set("hog")  # Default model is HOG

        self.hog_radio = Radiobutton(
            root, text="HOG Model", variable=self.model_var, value="hog"
        )
        self.hog_radio.grid(row=1, column=0)

        self.cnn_radio = Radiobutton(
            root, text="CNN Model", variable=self.model_var, value="cnn"
        )
        self.cnn_radio.grid(row=1, column=1)

        # self.train_button = tk.Button(
        #     root, text="Train Model", command=self.train_model
        # )
        # self.train_button.grid(row=2, column=0, columnspan=2, pady=5)

        # self.validate_button = tk.Button(
        #     root, text="Validate Model", command=self.validate_model
        # )
        # self.validate_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.test_button = tk.Button(
            root, text="Take Attendance with Image", command=self.test_model
        )
        self.test_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.webcam_button = tk.Button(
            root, text="Take Attendance from Webcam", command=self.face_recognition_webcam
        )
        self.webcam_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Simple Image
        label_simple_txt = tk.Label(root, text="Simple Image")
        label_simple_txt.grid(row=6, column=0, pady=7)

        # Set desired dimensions
        desired_width = 500
        desired_height = 500

        image = Image.open('images/un_detected_image.jpeg')
        # Resize the image to fit the desired dimensions
        resized_image = image.resize((desired_width, desired_height))
        image_1 = ImageTk.PhotoImage(resized_image)
        self.simple_image = tk.Label(root, image=image_1)
        self.simple_image.image = image_1  # Keep a reference to avoid garbage collection
        self.simple_image.grid(row=7, column=0, pady=10)

        # Detected Image
        label_detected_txt = tk.Label(root, text="Detected Image")
        label_detected_txt.grid(row=6, column=1, pady=17)

        image_2 = ImageTk.PhotoImage(Image.open('images/detected_image.jpeg').resize((desired_width,desired_height)))
        self.detected_image = tk.Label(root, image=image_2)
        self.detected_image.image = image_2  # Keep a reference to avoid garbage collection
        self.detected_image.grid(row=7, column=1, pady=10)

        self.request_url = "http://localhost:3000/api/v1/student/"

    def update_displayed_image(self, image_path, image_type):
        # Open the new image and convert it to PhotoImage
        new_img = ImageTk.PhotoImage(Image.open(image_path).resize((500,500)))

        # Update the image displayed in the label
        if image_type == "sample":
            self.simple_image.config(image=new_img)
            self.simple_image.image = new_img
        else:
            self.detected_image.config(image=new_img)
            self.detected_image.image = new_img

    def train_model(self):
        self.encode_known_faces(self.DEFAULT_ENCODINGS_PATH, self.model_var.get())

    def validate_model(self):
        # Commented out until the validate function is defined
        self.validate()
        messagebox.showinfo("Validation Complete", "Validation has been completed!")

    def test_model(self):
        file_path = filedialog.askopenfilename(title="Select an image file")
        if file_path:
            self.update_displayed_image(file_path, "sample")
            self.recognize_faces(image_location=file_path,model=self.model_var.get())
        else:
            messagebox.showwarning("No File Selected", "Please select an image file.")

    def face_recognition_webcam(self):
        # Initialize the video capture object
        video_capture = cv2.VideoCapture(0)

        while True:
            # Capture frame-by-frame
            ret, frame = video_capture.read()

            # Recognize faces in the frame and mark attendance
            frame_with_recognition = self.recognize_faces_from_frame(frame, self.model_var.get())

            # Display the resulting frame
            cv2.imshow('Video', frame_with_recognition)

            # Display the resulting frame
            # cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture object and close the window
        video_capture.release()
        cv2.destroyAllWindows()

    def recognize_faces_from_frame(self, frame, model):
        # Find face locations and encodings in the frame
        face_locations = face_recognition.face_locations(frame, model=model)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Load encodings from the file
        with open(self.DEFAULT_ENCODINGS_PATH, 'rb') as f:
            loaded_encodings = pickle.load(f)

        # Iterate through detected faces
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Recognize the face
            name = self._recognize_face(face_encoding, loaded_encodings)

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # If the face is recognized
            if name:
                print(name)
                # Send request to the API if attendance hasn't been marked already
                if name not in self.attendance_marked:
                    response = requests.post(self.request_url + name + "/saveattendance", json={})
                    if response.status_code == 201:
                        response_data = response.json()
                        messagebox.showinfo("Attendance Marked",
                                            f"{response_data['studentBio']['name']} is marked present.")
                        # Add the recognized face to the list of marked attendance
                        self.attendance_marked.append(name)
                    else:
                        print(f'Error: {response.status_code}')

                # Display the recognized name on the frame
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def recognize_faces(
            self, image_location: str, model: str = "hog", encodings_location: Path = None
    ) -> None:
        """
        Given an unknown image, get the locations and encodings of any faces and
        compares them against the known encodings to find potential matches.
        """
        if encodings_location is None:
            encodings_location = self.DEFAULT_ENCODINGS_PATH

        with encodings_location.open(mode="rb") as f:
            loaded_encodings = pickle.load(f)

        input_image = face_recognition.load_image_file(image_location)

        input_face_locations = face_recognition.face_locations(
            input_image, model=model
        )
        input_face_encodings = face_recognition.face_encodings(
            input_image, input_face_locations
        )

        pillow_image = Image.fromarray(input_image)
        draw = ImageDraw.Draw(pillow_image)

        for bounding_box, unknown_encoding in zip(
                input_face_locations, input_face_encodings
        ):
            name = self._recognize_face(unknown_encoding, loaded_encodings)
            if not name:
                name = "Unknown"
            self._display_face(draw, bounding_box, name)

        del draw
        pillow_image.show()

    def encode_known_faces(
            self,encoding_location, model
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

    def _recognize_face(self, unknown_encoding, loaded_encodings):
        """
        Given an unknown encoding and all known encodings, find the known
        encoding with the most matches.
        """
        boolean_matches = face_recognition.compare_faces(
            loaded_encodings["encodings"], unknown_encoding
        )
        votes = Counter(
            name
            for match, name in zip(boolean_matches, loaded_encodings["names"])
            if match
        )
        if votes:
            return votes.most_common(1)[0][0]

    def validate(self, model: str = "hog"):
        """
        Runs recognize_faces on a set of images with known faces to validate
        known encodings.
        """
        for filepath in Path("tests/validation").rglob("*"):
            if filepath.is_file():
                self.update_displayed_image(filepath.absolute(), "sample")
                self.recognize_faces(
                    image_location=str(filepath.absolute()), model=model
                )

    def recognize_faces(
            self,
            image_location: str,
            model: str = "hog",
    ) -> None:
        """
        Given an unknown image, get the locations and encodings of any faces and
        compares them against the known encodings to find potential matches.
        """
        with self.DEFAULT_ENCODINGS_PATH.open(mode="rb") as f:
            loaded_encodings = pickle.load(f)

        input_image = face_recognition.load_image_file(image_location)

        input_face_locations = face_recognition.face_locations(
            input_image, model=model
        )
        input_face_encodings = face_recognition.face_encodings(
            input_image, input_face_locations
        )

        pillow_image = Image.fromarray(input_image)
        draw = ImageDraw.Draw(pillow_image)

        for bounding_box, unknown_encoding in zip(
                input_face_locations, input_face_encodings
        ):
            name = self._recognize_face(unknown_encoding, loaded_encodings)
            if not name:
                name = "Unknown"
            else:
                response = requests.post(self.request_url +name+"/saveattendance", json={})
                if response.status_code == 201:
                    response_data = response.json()
                    print(response_data['studentBio'])
                    messagebox.showinfo("Attendance Marked", f"{response_data['studentBio']['name']} is marked present.")

                else:
                    print(f'Error: {response.status_code}')
            self._display_face(draw, bounding_box, name)

        del draw
        output_image_path = Path("output/detected_images/") / f"{Path(image_location).stem}_annotated.jpg"
        pillow_image.save(output_image_path)
        self.update_displayed_image(output_image_path,"detected")

    def _display_face(self, draw, bounding_box, name):
        """
        Draws bounding boxes around faces, a caption area, and text captions.
        """
        top, right, bottom, left = bounding_box
        draw.rectangle(((left, top), (right, bottom)), outline=self.BOUNDING_BOX_COLOR)

        # Determine maximum font size based on bounding box dimensions
        max_font_size = min((right - left) // len(name), (bottom - top) // 2)

        # Load font with maximum font size
        font = ImageFont.truetype("arial.ttf", size=max_font_size)

        draw.rectangle(
                ((left, top), (right, bottom)),
                outline=self.BOUNDING_BOX_COLOR,
                width=4
        )
        draw.text(
            (left, top),
            name,
            fill=self.TEXT_COLOR,
            font=font
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

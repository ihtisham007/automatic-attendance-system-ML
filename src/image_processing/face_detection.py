import tkinter as tk
from tkinter import filedialog, messagebox, Radiobutton, StringVar
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageTk
import face_recognition
import pickle

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.DEFAULT_ENCODINGS_PATH = Path("./../../output/encodings.pkl")
        self.BOUNDING_BOX_COLOR = "blue"
        self.TEXT_COLOR = "white"

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

        self.train_button = tk.Button(
            root, text="Train Model", command=self.train_model
        )
        self.train_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.validate_button = tk.Button(
            root, text="Validate Model", command=self.validate_model
        )
        self.validate_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.test_button = tk.Button(
            root, text="Test Model with Unknown Image", command=self.test_model
        )
        self.test_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Simple Image
        label_simple_txt = tk.Label(root, text="Simple Image")
        label_simple_txt.grid(row=5, column=0, pady=7)

        # Set desired dimensions
        desired_width = 500
        desired_height = 500

        image_path_1 = "C:/Python Projects/Automatic Attendance System/images/training/face/elon_musk/161881.jpg"
        image = Image.open(image_path_1)
        # Resize the image to fit the desired dimensions
        resized_image = image.resize((desired_width, desired_height))
        image_1 = ImageTk.PhotoImage(resized_image)
        self.simple_image = tk.Label(root, image=image_1)
        self.simple_image.image = image_1  # Keep a reference to avoid garbage collection
        self.simple_image.grid(row=6, column=0, pady=10)

        # Detected Image
        label_detected_txt = tk.Label(root, text="Detected Image")
        label_detected_txt.grid(row=5, column=1, pady=17)

        image_path_2 = "C:/Python Projects/Automatic Attendance System/output/detected_images/161859_annotated.jpg"
        image_2 = ImageTk.PhotoImage(Image.open(image_path_2).resize((desired_width,desired_height)))
        self.detected_image = tk.Label(root, image=image_2)
        self.detected_image.image = image_2  # Keep a reference to avoid garbage collection
        self.detected_image.grid(row=6, column=1, pady=10)

    def update_displayed_image(self, image_path, image_type):
        # Open the new image and convert it to PhotoImage
        new_img = ImageTk.PhotoImage(Image.open(image_path))

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

        for filepath in Path("./../../images/training").glob("*/*"):
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
            self._display_face(draw, bounding_box, name)

        del draw
        output_image_path = Path("./../../output/detected_images/") / f"{Path(image_location).stem}_annotated.jpg"
        pillow_image.save(output_image_path)
        self.update_displayed_image(output_image_path,"detected")
        pillow_image.show()

    def _display_face(self, draw, bounding_box, name):
        """
        Draws bounding boxes around faces, a caption area, and text captions.
        """
        top, right, bottom, left = bounding_box
        draw.rectangle(((left, top), (right, bottom)), outline=self.BOUNDING_BOX_COLOR)

        draw.rectangle(
            ((left, top), (right, bottom)),
            outline=self.BOUNDING_BOX_COLOR,
        )
        draw.text(
            (left, top),
            name,
            fill=self.TEXT_COLOR,
            size=40
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

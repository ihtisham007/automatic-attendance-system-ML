import tkinter as tk
from tkinter import filedialog, messagebox, Radiobutton, StringVar
from pathlib import Path
from PIL import Image, ImageDraw
import face_recognition
import pickle


class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")
        self.BOUNDING_BOX_COLOR = "blue"
        self.TEXT_COLOR = "white"

        self.label = tk.Label(root, text="Select an option: (HOG for CPU Processing and CNN For GPU Processing)")
        self.label.pack(pady=10)

        self.model_var = StringVar()
        self.model_var.set("hog")  # Default model is HOG

        self.hog_radio = Radiobutton(
            root, text="HOG Model", variable=self.model_var, value="hog"
        )
        self.hog_radio.pack()

        self.cnn_radio = Radiobutton(
            root, text="CNN Model", variable=self.model_var, value="cnn"
        )
        self.cnn_radio.pack()

        self.train_button = tk.Button(
            root, text="Train Model", command=self.train_model
        )
        self.train_button.pack(pady=5)

        self.validate_button = tk.Button(
            root, text="Validate Model", command=self.validate_model
        )
        self.validate_button.pack(pady=5)

        self.test_button = tk.Button(
            root, text="Test Model with Unknown Image", command=self.test_model
        )
        self.test_button.pack(pady=5)

    def train_model(self):
        self.encode_known_faces(self.DEFAULT_ENCODINGS_PATH, self.model_var.get())

    def validate_model(self):
        # Commented out until the validate function is defined
        self.validate()
        messagebox.showinfo("Validation Complete", "Validation has been completed!")

    def test_model(self):
        file_path = filedialog.askopenfilename(title="Select an image file")
        if file_path:
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
            print(draw, name, bounding_box)
            self._display_face(draw, bounding_box, name)

        del draw
        pillow_image.show()

    def encode_known_faces(
            self,encoding_location, model
    ) -> None:
        print("It is working")
        """
        Loads images in the training directory and builds a dictionary of their
        names and encodings.
        """

        names = []
        encodings = []

        for filepath in Path("images/training").glob("*/*"):
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
            print(draw, name, bounding_box)
            self._display_face(draw, bounding_box, name)

        del draw
        pillow_image.show()

    def _display_face(self, draw, bounding_box, name):
        """
        Draws bounding boxes around faces, a caption area, and text captions.
        """
        print("Here ")
        pass
        top, right, bottom, left = bounding_box
        draw.rectangle(((left, top), (right, bottom)), outline=self.BOUNDING_BOX_COLOR)
        print(left, bottom, name)

        draw.rectangle(
            ((left, top), (right, bottom)),
            outline=self.BOUNDING_BOX_COLOR,
        )
        draw.text(
            (left, top),
            name,
            fill=self.TEXT_COLOR,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

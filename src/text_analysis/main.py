import tkinter as tk
from tkinter import filedialog
import cv2
import easyocr
from PIL import Image, ImageTk
from matplotlib import pyplot

class OCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title('OCR GUI')

        # Initialize the EasyOCR reader
        self.reader = easyocr.Reader(['en'])

        # Create the GUI layout
        self.setup_gui()

    def setup_gui(self):
        # Create a frame for the left side (image upload)
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT)

        # Create a label to display the text detection label
        self.detect_label = tk.Label(self.left_frame, text='Detect Text')
        self.detect_label.pack()

        # Create a label to display the image
        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack()

        # Create a button to upload an image
        self.upload_btn = tk.Button(self.left_frame, text='Upload Image', command=self.upload_image)
        self.upload_btn.pack()

        # Create a frame for the right side (extracted text)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT)

        # Create a listbox to display the extracted text
        self.extracted_text = tk.Listbox(self.right_frame, width=100, height=100)
        self.extracted_text.pack()

    def upload_image(self):
        # Get the file path from the file dialog
        file_path = filedialog.askopenfilename()
        if file_path:
            # Read the image using OpenCV
            img = cv2.imread(file_path)
            # Copy uploaded image for drawing rectangle and text
            img_copy = img.copy()
            # Run OCR
            results = self.reader.readtext(img)
            # Update the image and detected text on the GUI
            self.display_image(img, results)
            # Draw rectangle and text on image
            self.print_rectangle_shapes_on_text(img_copy, results)
    def print_rectangle_shapes_on_text(self, img, results):
        pyplot.imshow(img)

        for res in results:
            # bbox coordinates of the detected text
            xy = res[0]
            xy1, xy2, xy3, xy4 = xy[0], xy[1], xy[2], xy[3]
            # text results and confidence of detection
            det, conf = res[1], res[2]
            # plot bounding box
            pyplot.plot([xy1[0], xy2[0], xy3[0], xy4[0], xy1[0]], [xy1[1], xy2[1], xy3[1], xy4[1], xy1[1]], 'r-')
            # show text and confidence
            pyplot.text(xy1[0], xy1[1], f'{det}', color='blue')

        pyplot.axis('off')  # Hide axis
        pyplot.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust margins
        pyplot.savefig('./output/detected_images/text_detected_image.png', bbox_inches='tight', pad_inches=0)  # Save plot as image
        pyplot.close()  # Close plot to prevent displaying in a separate window
        pil_img = Image.open('./output/detected_images/text_detected_image.png')

        # Convert PIL Image to Tkinter PhotoImage
        tk_img = ImageTk.PhotoImage(pil_img)

        # Update detect_label with the new image
        self.detect_label.config(image=tk_img)
        self.detect_label.image = tk_img

    def display_image(self, img, results):
        # Convert the image to RGB (Tkinter compatibility)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_img = Image.fromarray(img)
        # Convert to ImageTk format
        tk_img = ImageTk.PhotoImage(pil_img)
        # Update the label with the new image
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

        self.detect_label.config(image=tk_img)
        self.detect_label.image = tk_img

        # Display the extracted text in the list on the right, line by line
        self.extracted_text.delete(0, tk.END)
        for res in results:
            # Split the detected text into lines
            lines = res[1].split('\n')
            for line in lines:
                self.extracted_text.insert(tk.END, line)


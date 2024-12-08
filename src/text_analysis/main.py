import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import easyocr
from PIL import Image, ImageTk
import requests
import numpy as np

class OCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title('OCR GUI')
        self.reader = easyocr.Reader(['en'])
        self.present_student = []
        self.setup_gui()

    def setup_gui(self):
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.detect_label = tk.Label(self.left_frame, text='Detect Text')
        self.detect_label.pack(pady=5)

        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack(pady=5)

        self.upload_btn = tk.Button(self.left_frame, text='Upload Image', command=self.upload_image)
        self.upload_btn.pack(pady=5)

        self.webcam_btn = tk.Button(self.left_frame, text='Mark Attendance via Webcam', command=self.mark_attendance_via_webcam)
        self.webcam_btn.pack(pady=5)

        self.send_attendance_btn = tk.Button(self.left_frame, text="Send Attendance", command=self.send_attendance_manual)
        self.send_attendance_btn.pack(pady=5)

        self.extracted_text = tk.Listbox(self.right_frame, width=100, height=100)
        self.extracted_text.pack(pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            img = cv2.imread(file_path)
            results = self.reader.readtext(img)
            self.display_image(self.resize_image(img, [300, 300]), results)
            self.annotate_image(img, results)
            self.prompt_send_attendance()

    def mark_attendance_via_webcam(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = self.reader.readtext(frame)
            self.annotate_frame(frame, results)
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        self.prompt_send_attendance()

    def annotate_image(self, img, results):
        for res in results:
            xy = res[0]
            det = res[1]
            cv2.polylines(img, [np.array(xy, np.int32).reshape((-1, 1, 2))], True, (0, 255, 0), 2)
            student_name = self.get_student_name(det)
            cv2.putText(img, f'{det}: {student_name}', (xy[0][0], xy[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        self.display_image(img, results)

    def annotate_frame(self, frame, results):
        for res in results:
            xy = res[0]
            det = res[1]
            cv2.polylines(frame, [np.array(xy, np.int32).reshape((-1, 1, 2))], True, (0, 255, 0), 2)
            student_name = self.get_student_name(det)
            print(student_name)
            x, y = xy[0]
            cv2.putText(frame, f'{det}: {student_name}', (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            print(det)

    def prompt_send_attendance(self):
        confirm_send = messagebox.askokcancel("Send Attendance", "Send attendance for detected students?")
        if confirm_send:
            self.send_attendance_manual()

    def send_attendance(self, student_id):
        api_url = f'http://localhost:3000/api/v1/student/{student_id}/saveattendance'
        response = requests.post(api_url)
        print(f"Attendance sent for student ID: {student_id}")

    def send_attendance_manual(self):
        for student in self.present_student:
            self.send_attendance(student['id'])

    def resize_image(self, img, size):
        return cv2.resize(img, (size[0], size[1]))

    def display_image(self, img, results):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        tk_img = ImageTk.PhotoImage(pil_img)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img
        self.extracted_text.delete(0, tk.END)
        for res in results:
            lines = res[1].split('\n')
            for line in lines:
                self.extracted_text.insert(tk.END, line)

    def get_student_name(self, student_id):
        api_url = f'http://localhost:3000/api/v1/student/{student_id}/getstudentname'
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and data['data']:
                self.present_student.append(data['data'])
                return data['data'][0]['name']
        return 'Unknown'


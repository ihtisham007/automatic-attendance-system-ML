import tkinter as tk
from src.image_processing.face_detection import FaceRecognitionApp

def main():
    root = tk.Tk()
    app = FaceRecognitionApp(root)

    # Set window size and center on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 600
    window_height = 400
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Configure grid to make columns expand evenly
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()
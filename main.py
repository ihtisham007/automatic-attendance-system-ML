import argparse
import src.image_processing.face_detection_gui as face_detection
import src.text_analysis.main as text_detection

# Create the parser
parser = argparse.ArgumentParser(description='Run detection type based on command-line argument.')
# Add the 'detection-type' argument
parser.add_argument('--detection-type', type=str, help='Type of detection to run: face or text')

# Parse the arguments
args = parser.parse_args()

if __name__ == "__main__":
    # Check the 'detection-type' argument value
    if args.detection_type == 'face':
        face_detection.faceDetection()
    elif args.detection_type == 'text':
        root = text_detection.tk.Tk()
        app = text_detection.OCRGui(root)
        root.mainloop()
    else:
        print("Invalid detection type. Please choose 'face' or 'text'.")
import cv2
import os
from config import get_settings
from face_recognition2.src.helpers.enums.pathenums import PathEnums

# Directory to save images
OUTPUT_DIR = PathEnums.OUTPUT_DIR.value
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize the webcam
camera = cv2.VideoCapture(get_settings().CAMER_INPUT)

if not camera.isOpened():
    print("Error: Could not access the camera.")
    exit()

def capture_images(person_class, name):
    person_dir = os.path.join(OUTPUT_DIR, person_class, name)
    os.makedirs(person_dir, exist_ok=True)

    print(f"Capturing images for {name} ({person_class}). Press SPACE to capture, 'q' to quit.")
    count = 0

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        cv2.imshow("Image Capture", frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # SPACE key to capture
            img_path = os.path.join(person_dir, f"{name}_{count}.jpg")
            cv2.imwrite(img_path, frame)
            count += 1
            print(f"Captured image {count}.")

        elif key == ord('q'):  # 'q' key to quit
            break

    print(f"Finished capturing images for {name} ({person_class}). Total images: {count}")

# Main routine
if __name__ == "__main__":
    person_class = input("Enter the person class (student, doctor, college_dean): ").strip().lower()
    if person_class not in ["student", "doctor", "college_dean"]:
        print("Invalid class. Please restart and enter a valid class.")
        exit()

    person_name = input("Enter the person's name: ").strip()
    if person_name:
        capture_images(person_class, person_name)
    else:
        print("Invalid name. Please restart and enter a valid name.")

# Release resources
camera.release()
cv2.destroyAllWindows()

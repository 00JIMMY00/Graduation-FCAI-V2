from enum import Enum
import os

current_directory = os.getcwd()

class PathEnums(Enum):
    INPUT_DIR = os.path.join(current_directory, "face_recognition2/src/assets", "captured_images")
    OUTPUT_DIR = os.path.join(current_directory, "face_recognition2/src/assets", "captured_images")
    model_path = os.path.join(current_directory, "face_recognition2/src/assets", "face_recognition_model.pkl")
    label_map_path = os.path.join(current_directory, "face_recognition2/src/assets", "label_map.pkl")
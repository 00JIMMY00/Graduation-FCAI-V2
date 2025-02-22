import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import pickle
from enums import PathEnums

# Directory containing the captured images
INPUT_DIR = PathEnums.INPUT_DIR.value
model_path = PathEnums.model_path.value
label_map_path = PathEnums.label_map_path.value

# Function to load images and labels
def load_data():
    images = []
    labels = []
    label_map = {}
    label_counter = 0

    for person_class in os.listdir(INPUT_DIR):
        class_path = os.path.join(INPUT_DIR, person_class)
        if os.path.isdir(class_path):
            for person_name in os.listdir(class_path):
                person_path = os.path.join(class_path, person_name)
                if os.path.isdir(person_path):
                    unique_label = f"{person_class}/{person_name}"
                    if unique_label not in label_map:
                        label_map[unique_label] = label_counter
                        label_counter += 1

                    for img_name in os.listdir(person_path):
                        img_path = os.path.join(person_path, img_name)
                        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            img_resized = cv2.resize(img, (100, 100))  # Resize images to a fixed size
                            images.append(img_resized.flatten())
                            labels.append(label_map[unique_label])

    return np.array(images), np.array(labels), label_map

# Load data
print("Loading data...")
images, labels, label_map = load_data()
print(f"Loaded {len(images)} images from {len(label_map)} unique labels.")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

# Train the model
print("Training the model...")
model = SVC(kernel='linear', probability=True)
model.fit(X_train, y_train)

# Evaluate the model
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy * 100:.2f}%")

# Save the model and label map
print("Saving the model and label map...")
with open(model_path, "wb") as model_file:
    pickle.dump(model, model_file)

with open(label_map_path, "wb") as label_map_file:
    pickle.dump(label_map, label_map_file)

print("Model and label map saved successfully.")

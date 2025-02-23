import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
import pickle
from enums import PathEnums
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam

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
                            img_resized = cv2.resize(img, (100, 100))
                            # Normalize and reshape for CNN input
                            img_resized = img_resized.astype("float32") / 255.0
                            images.append(img_resized.reshape(100, 100, 1))
                            labels.append(label_map[unique_label])

    return np.array(images), np.array(labels), label_map

# Load data
print("Loading data...")
images, labels, label_map = load_data()
print(f"Loaded {len(images)} images from {len(label_map)} unique labels.")

num_classes = len(label_map)
labels_cat = to_categorical(labels, num_classes=num_classes)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(images, labels_cat, test_size=0.2, random_state=42)

# Build CNN model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(100, 100, 1)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
print("Training the CNN model...")
history = model.fit(X_train, y_train, validation_split=0.2, epochs=20, batch_size=32, verbose=1)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Model accuracy: {accuracy * 100:.2f}%")

# Save the model and label map
print("Saving the model and label map...")
model.save(model_path)
with open(label_map_path, "wb") as label_map_file:
    pickle.dump(label_map, label_map_file)

print("Model and label map saved successfully.")

import cv2
import os
import numpy as np

faces = []
labels = []

# Face detector Classifier
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

faces_folder = "faces"

for folder_name in os.listdir(faces_folder):
    folder_path = os.path.join(faces_folder, folder_name)

    if not os.path.isdir(folder_path):
        continue

    # Folder name Format: Name_RollNo (e.g., Riya_89)
    # Extract Roll No (last item after split)
    try:
        roll_no = folder_name.split("_")[-1]
        label = int(roll_no)
    except ValueError:
        print(f"Skipping folder {folder_name}: Invalid Roll No format")
        continue

    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        faces.append(img)
        labels.append(label)

# Train Recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))

# Save trained model inside model folder
if not os.path.exists("model"):
    os.makedirs("model")

recognizer.write("model/trained_model.yml")
print("\n[SUCCESS] Model training completed successfully!")
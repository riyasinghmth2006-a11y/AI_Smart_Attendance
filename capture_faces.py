import cv2
import os

# Face detection Classifier
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Directory to save captured face images
save_dir = "faces"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Get Student Details
student_name = input("Enter Student Name: ")
student_id = input("Enter Student ID/Roll No: ")

# Target folder path: faces/Name_ID
student_folder = os.path.join(save_dir, f"{student_name}_{student_id}")
if not os.path.exists(student_folder):
    os.makedirs(student_folder)

camera = cv2.VideoCapture(0)
count = 0
max_photos = 30  # Number of photos to capture per student

print("\n[INFO] Starting camera. Please ensure good lighting and look at the camera...")
print("[INFO] Photos will be captured automatically. Press 'q' to quit early.\n")

while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Camera could not be accessed.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    for (x, y, w, h) in faces:
        count += 1
        # Crop the detected face area
        face_img = frame[y:y+h, x:x+w]
        file_path = os.path.join(student_folder, f"{student_name}_{count}.jpg")
        cv2.imwrite(file_path, face_img)

        # Draw green bounding box on screen
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(
            frame, 
            f"Captured: {count}/{max_photos}", 
            (50, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            (0, 255, 0), 
            2
        )

    cv2.imshow("Capturing Faces - Look at Camera", frame)

    # Stop when max_photos reached or 'q' is pressed
    if cv2.waitKey(100) & 0xFF == ord('q') or count >= max_photos:
        break

camera.release()
cv2.destroyAllWindows()
print(f"\n[SUCCESS] Successfully captured {count} photos for {student_name}!")
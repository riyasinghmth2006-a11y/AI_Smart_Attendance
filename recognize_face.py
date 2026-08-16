import cv2
import csv
import os
from datetime import datetime

# 1. Load Student Names from CSV
students = {}
if os.path.exists("students.csv"):
    with open("students.csv", mode="r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                try:
                    students[int(row[0].strip())] = row[1].strip()
                except ValueError:
                    continue

# 2. Setup Recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("model/trained_model.yml")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

camera = cv2.VideoCapture(0)
attendance_marked = False # Isse check karenge ki attendance ho gayi ya nahi

print("[INFO] Showing camera... waiting to recognize...")

while True:
    ret, frame = camera.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        label, confidence = recognizer.predict(face_img)

        # Confidence < 100 is a good match
        if confidence < 100 and label in students:
            name = students[label]
            
            # --- ATTENDANCE LOGIC START ---
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            # CSV mein append karo
            with open("attendance.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, label, date_str, time_str])
            
            print(f"[SUCCESS] Attendance Marked for {name}")
            attendance_marked = True
            # --- ATTENDANCE LOGIC END ---

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Marked: {name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        else:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("Attendance System", frame)

    # 3 second wait karne ke baad auto-close logic
    if attendance_marked:
        cv2.waitKey(3000) # 3 seconds rukega taaki aap confirm kar sako ki mark ho gaya
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
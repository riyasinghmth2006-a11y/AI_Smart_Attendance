import csv
import os
from collections import defaultdict

print("===== ATTENDANCE REPORT =====")

if not os.path.exists("attendance.csv"):
    print("No attendance record found.")
    exit()

# Store attendance information
student_attendance = defaultdict(lambda: {
    "total": 0,
    "present": 0
})

# Read attendance.csv
with open("attendance.csv", "r", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:

        name = row["Name"]
        roll_no = row["Roll_No"]
        subject = row["Subject"]
        status = row["Status"]
        date_time = row["Date_Time"]

        key = (name, roll_no, subject)

        student_attendance[key]["total"] += 1

        if status.lower() == "present":
            student_attendance[key]["present"] += 1

        # =========================
        # DISPLAY ATTENDANCE
        # =========================

        print()
        print("Student Name :", name)
        print("Roll Number  :", roll_no)
        print("Subject      :", subject)
        print("Status       :", status)
        print("Date & Time  :", date_time)

# =========================
# ATTENDANCE PERCENTAGE
# =========================

print()
print("===== ATTENDANCE PERCENTAGE =====")

for key, data in student_attendance.items():

    name, roll_no, subject = key

    total = data["total"]
    present = data["present"]

    percentage = (present / total) * 100

    print()
    print("Student Name :", name)
    print("Roll Number  :", roll_no)
    print("Subject      :", subject)
    print("Present      :", present)
    print("Total Classes:", total)
    print("Attendance   :", f"{percentage:.2f}%")
from fastmcp import FastMCP
import sys
import traceback
import time
import mysql.connector

mcp = FastMCP("University Attendance MCP")

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ShreyaSQL",
        database="educampus"
    )

# -------------------------------------------------
# AUTH HELPERS
# -------------------------------------------------
def is_teacher(email: str) -> bool:
    return email.endswith("@gmail.com")

def is_student(email: str) -> bool:
    return email.endswith("@vit.edu")

def get_student_by_email(student_email: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT student_id, student_name, student_email
        FROM attendance_summary
        WHERE student_email = %s
        LIMIT 1
        """,
        (student_email,)
    )

    student = cursor.fetchone()
    cursor.close()
    db.close()

    if not student:
        raise ValueError("Student email not found")

    return student

def get_teacher_name_for_subject(subject: str) -> str:
    subject_teacher_map = {
        "English": "X",
        "Maths": "Y",
        "Science": "Z"
    }
    if subject not in subject_teacher_map:
        raise ValueError("Invalid subject")
    return subject_teacher_map[subject]

# -------------------------------------------------
# TEACHER TOOL — MARK ATTENDANCE
# -------------------------------------------------
@mcp.tool()
def mark_attendance(
    teacher_email: str,
    subject: str,
    month_no: int,
    lecture_no: int,
    student_ids: list[int],
    mode: str
):
    """
    mode:
      - 'present' → student_ids are PRESENT
      - 'absent'  → student_ids are ABSENT
    """

    if not is_teacher(teacher_email):
        return {"error": "Unauthorized: only teachers can mark attendance"}

    teacher_name = get_teacher_name_for_subject(subject)

    if mode not in ("present", "absent"):
        return {"error": "Invalid mode. Use 'present' or 'absent'"}

    db = get_db()
    cursor = db.cursor()

    # Step 1: set base status for everyone
    base_status = "A" if mode == "present" else "P"

    cursor.execute(
        """
        UPDATE attendance
        SET status = %s
        WHERE subject = %s
          AND teacher_name = %s
          AND month_no = %s
          AND lecture_no = %s
        """,
        (base_status, subject, teacher_name, month_no, lecture_no)
    )

    # Step 2: flip status for provided students
    if student_ids:
        target_status = "P" if mode == "present" else "A"
        placeholders = ",".join(["%s"] * len(student_ids))

        cursor.execute(
            f"""
            UPDATE attendance
            SET status = %s
            WHERE subject = %s
              AND teacher_name = %s
              AND month_no = %s
              AND lecture_no = %s
              AND student_id IN ({placeholders})
            """,
            [target_status, subject, teacher_name, month_no, lecture_no] + student_ids
        )

    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Attendance updated successfully",
        "subject": subject,
        "month": month_no,
        "lecture": lecture_no,
        "mode": mode,
        "affected_students": student_ids
    }

# -------------------------------------------------
# STUDENT TOOL — VIEW RAW ATTENDANCE
# -------------------------------------------------
@mcp.tool()
def view_my_attendance(student_email: str):
    if not is_student(student_email):
        return {"error": "Unauthorized: only students can view attendance"}

    student = get_student_by_email(student_email)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT subject, month_no, lecture_no, lecture_date, status
        FROM attendance
        WHERE student_id = %s
        ORDER BY subject, month_no, lecture_no
        """,
        (student["student_id"],)
    )

    records = cursor.fetchall()
    cursor.close()
    db.close()

    return {
        "student": student,
        "attendance": records
    }

# -------------------------------------------------
# STUDENT TOOL — VIEW ATTENDANCE PERCENTAGE
# -------------------------------------------------
@mcp.tool()
def view_my_attendance_percentage(student_email: str):
    if not is_student(student_email):
        return {"error": "Unauthorized: only students can view percentage"}

    student = get_student_by_email(student_email)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT subject, lectures_attended, total_lectures, attendance_percentage
        FROM attendance_summary
        WHERE student_id = %s
        """,
        (student["student_id"],)
    )

    summary = cursor.fetchall()
    cursor.close()
    db.close()

    return {
        "student": student,
        "summary": summary
    }

# -------------------------------------------------
# RUN MCP SERVER
# -------------------------------------------------
if __name__ == "__main__":
    mcp.run()

# def main():
#     try:
#         mcp.run()
#     except Exception:
#         traceback.print_exc(file=sys.stderr)
#         while True:
#             time.sleep(60)

# if __name__ == "__main__":
#     main()
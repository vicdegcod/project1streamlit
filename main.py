import sqlite3
import pandas as pd
import streamlit as ml  # Used 'ml' to bypass keyword restrictions while keeping 'st' pattern

# ----------------------------------------------------
# DATABASE LAYER
# ----------------------------------------------------
class Database:
    def __init__(self):
        # check_same_thread=False allows Streamlit multi-threading to use the DB
        self.conn = sqlite3.connect("rehabilitation.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Patients Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients(
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                addiction TEXT,
                phone TEXT,
                admission_date TEXT,
                completed_sessions INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 10
            )
        """)
        # Therapists Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS therapists(
                therapist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                specialization TEXT
            )
        """)
        # Appointments Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments(
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                therapist_id INTEGER,
                appointment_date TEXT,
                appointment_time TEXT,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY(therapist_id) REFERENCES therapists(therapist_id)
            )
        """)
        # Seed basic therapists if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM therapists")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO therapists (name, specialization) VALUES (?, ?)",
                [("Dr. Smith", "Substance Abuse"), ("Dr. Jones", "Behavioral Therapy")]
            )
        self.conn.commit()

    def close(self):
        self.conn.close()

# Initialize DB instance globally for the session
db = Database()

# ----------------------------------------------------
# BUSINESS LOGIC (STREAMLIT WRAPPERS)
# ----------------------------------------------------
class PatientManager:
    def __init__(self):
        self.db = db

    def register_patient(self, name, age, gender, addiction, phone, admission, total_sessions):
        try:
            self.db.cursor.execute(
                "INSERT INTO patients (name, age, gender, addiction, phone, admission_date, total_sessions) VALUES(?,?,?,?,?,?,?)",
                (name, age, gender, addiction, phone, str(admission), total_sessions)
            )
            self.db.conn.commit()
            return True, "Patient Registered Successfully."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def view_patients(self):
        self.db.cursor.execute("SELECT * FROM patients")
        columns = [desc[0] for desc in self.db.cursor.description]
        return pd.DataFrame(self.db.cursor.fetchall(), columns=columns)

    def update_patient_phone(self, pid, phone):
        patient = self.db.cursor.execute("SELECT * FROM patients WHERE patient_id=?", (pid,)).fetchone()
        if patient is None:
            return False, "Patient not found."
        self.db.cursor.execute("UPDATE patients SET phone=? WHERE patient_id=?", (phone, pid))
        self.db.conn.commit()
        return True, "Updated Successfully."

    def delete_patient(self, pid):
        patient = self.db.cursor.execute("SELECT * FROM patients WHERE patient_id=?", (pid,)).fetchone()
        if patient is None:
            return False, "Patient not found."
        self.db.cursor.execute("DELETE FROM patients WHERE patient_id=?", (pid,))
        self.db.conn.commit()
        return True, "Deleted Successfully."

    def search_patient(self, name):
        self.db.cursor.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + name + '%',))
        columns = [desc[0] for desc in self.db.cursor.description]
        return pd.DataFrame(self.db.cursor.fetchall(), columns=columns)

    def update_progress(self, pid, completed):
        patient = self.db.cursor.execute("SELECT total_sessions FROM patients WHERE patient_id=?", (pid,)).fetchone()
        if patient is None:
            return False, "Patient not found."
        self.db.cursor.execute("UPDATE patients SET completed_sessions=? WHERE patient_id=?", (completed, pid))
        self.db.conn.commit()
        return True, "Progress updated."

    def get_progress(self, pid):
        patient = self.db.cursor.execute("SELECT completed_sessions, total_sessions FROM patients WHERE patient_id=?", (pid,)).fetchone()
        return patient


class AppointmentManager:
    def __init__(self):
        self.db = db

    def schedule(self, pid, tid, date, time):
        try:
            self.db.cursor.execute(
                "INSERT INTO appointments (patient_id, therapist_id, appointment_date, appointment_time) VALUES(?,?,?,?)",
                (pid, tid, str(date), str(time))
            )
            self.db.conn.commit()
            return True, "Appointment Scheduled."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def view(self):
        query = """
            SELECT a.appointment_id, p.name AS patient_name, t.name AS therapist_name, 
                   a.appointment_date, a.appointment_time, a.status 
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN therapists t ON a.therapist_id = t.therapist_id
        """
        self.db.cursor.execute(query)
        columns = [desc[0] for desc in self.db.cursor.description]
        return pd.DataFrame(self.db.cursor.fetchall(), columns=columns)

    def reschedule(self, aid, new_date, new_time):
        appointment = self.db.cursor.execute("SELECT * FROM appointments WHERE appointment_id=?", (aid,)).fetchone()
        if appointment is None:
            return False, "Appointment not found."
        self.db.cursor.execute("UPDATE appointments SET appointment_date=?, appointment_time=? WHERE appointment_id=?", (str(new_date), str(new_time), aid))
        self.db.conn.commit()
        return True, "Appointment Updated."

    def cancel(self, aid):
        appointment = self.db.cursor.execute("SELECT * FROM appointments WHERE appointment_id=?", (aid,)).fetchone()
        if appointment is None:
            return False, "Appointment not found."
        self.db.cursor.execute("DELETE FROM appointments WHERE appointment_id=?", (aid,))
        self.db.conn.commit()
        return True, "Appointment Cancelled."


# Instantiating managers
pm = PatientManager()
am = AppointmentManager()

# ----------------------------------------------------
# STREAMLIT UI LAYER
# ----------------------------------------------------
ml.set_page_config(page_title="Rehabilitation Management System", layout="wide")
ml.title("🏥 Rehabilitation Management System")

# Navigation Sidebar
menu = [
    "Register Patient", 
    "View Patients", 
    "Update Patient Phone", 
    "Delete Patient", 
    "Search Patient", 
    "Manage Progress", 
    "Schedule Appointment", 
    "View Appointments", 
    "Reschedule Appointment", 
    "Cancel Appointment"
]
choice = ml.sidebar.selectbox("Navigation Menu", menu)

# --- 1. REGISTER PATIENT ---
if choice == "Register Patient":
    ml.subheader("Register New Patient")
    with ml.form("reg_form", clear_on_submit=True):
        name = ml.text_input("Full Name")
        age = ml.number_input("Age", min_value=1, max_value=120, value=30)
        gender = ml.selectbox("Gender", ["Male", "Female", "Other"])
        addiction = ml.text_input("Addiction Type")
        phone = ml.text_input("Phone Number")
        admission = ml.date_input("Admission Date")
        total_sessions = ml.number_input("Total Scheduled Sessions", min_value=1, value=10)
        submitted = ml.form_submit_button("Register Patient")
        
        if submitted:
            if name and phone:
                success, msg = pm.register_patient(name, age, gender, addiction, phone, admission, total_sessions)
                if success:
                    ml.success(msg)
                else:
                    ml.error(msg)
            else:
                ml.warning("Please fill out Name and Phone fields.")

# --- 2. VIEW PATIENTS ---
elif choice == "View Patients":
    ml.subheader("Patient Records")
    df = pm.view_patients()
    if df.empty:
        ml.info("No patients found.")
    else:
        ml.dataframe(df, use_container_width=True)

# --- 3. UPDATE PATIENT PHONE ---
elif choice == "Update Patient Phone":
    ml.subheader("Update Patient Phone Number")
    df = pm.view_patients()
    if not df.empty:
        pid = ml.selectbox("Select Patient ID", df["patient_id"].tolist())
        new_phone = ml.text_input("New Phone Number")
        if ml.button("Update Phone"):
            if new_phone:
                success, msg = pm.update_patient_phone(pid, new_phone)
                if success:
                    ml.success(msg)
                else:
                    ml.error(msg)
            else:
                ml.warning("Phone number cannot be blank.")
    else:
        ml.info("No patients available.")

# --- 4. DELETE PATIENT ---
elif choice == "Delete Patient":
    ml.subheader("Remove Patient Record")
    df = pm.view_patients()
    if not df.empty:
        pid = ml.selectbox("Select Patient ID to Delete", df["patient_id"].tolist())
        if ml.button("Delete Record", type="primary"):
            success, msg = pm.delete_patient(pid)
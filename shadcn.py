import sqlite3
import pandas as pd


class Database:
    def __init__(self, db_name="sliprehab.db"):
        self.conn = sqlite3.connect(
            db_name,
            check_same_thread=False
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    # =====================================================
    # CREATE TABLES
    # =====================================================

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            addiction TEXT,
            admission_date TEXT,
            completed_sessions INTEGER DEFAULT 0,
            total_sessions INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS therapists(
            therapist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments(
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            therapist_id INTEGER,
            visit_date TEXT,
            visit_time TEXT,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(client_id)
                REFERENCES clients(client_id),
            FOREIGN KEY(therapist_id)
                REFERENCES therapists(therapist_id)
        )
        """)

        self.conn.commit()

    # =====================================================
    # CLIENT METHODS
    # =====================================================

    def add_client(
        self,
        name,
        age,
        gender,
        addiction,
        admission_date,
        total_sessions
    ):

        self.cursor.execute("""
        INSERT INTO clients(
            name,
            age,
            gender,
            addiction,
            admission_date,
            total_sessions
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            name,
            age,
            gender,
            addiction,
            admission_date,
            total_sessions
        ))

        self.conn.commit()

    def get_clients(self):

        query = """
        SELECT *
        FROM clients
        ORDER BY client_id DESC
        """

        return pd.read_sql(query, self.conn)

    def get_client(self, client_id):

        self.cursor.execute("""
        SELECT *
        FROM clients
        WHERE client_id=?
        """,
        (client_id,)
        )

        return self.cursor.fetchone()

    def update_client(
        self,
        client_id,
        name,
        age,
        gender,
        addiction,
        admission_date,
        total_sessions
    ):

        self.cursor.execute("""
        UPDATE clients
        SET
            name=?,
            age=?,
            gender=?,
            addiction=?,
            admission_date=?,
            total_sessions=?
        WHERE client_id=?
        """,
        (
            name,
            age,
            gender,
            addiction,
            admission_date,
            total_sessions,
            client_id
        ))

        self.conn.commit()

    def delete_client(self, client_id):

        self.cursor.execute("""
        DELETE FROM appointments
        WHERE client_id=?
        """,
        (client_id,)
        )

        self.cursor.execute("""
        DELETE FROM clients
        WHERE client_id=?
        """,
        (client_id,)
        )

        self.conn.commit()

    def search_clients(self, keyword):

        query = """
        SELECT *
        FROM clients
        WHERE
            name LIKE ?
            OR addiction LIKE ?
            OR gender LIKE ?
        ORDER BY name
        """

        return pd.read_sql(
            query,
            self.conn,
            params=(
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )
    def delete_therapist(self, therapist_id):
        self.cursor.execute("""DELETE FROM appointments
    WHERE therapist_id=?
    """,
    (therapist_id,)
    )

    self.cursor.execute("""
    DELETE FROM therapists
    WHERE therapist_id=?
    """,
    (therapist_id,)
    )

    self.conn.commit()

    def close(self):
        self.conn.close()

        # =====================================================
    # THERAPIST METHODS
    # =====================================================

    def add_therapist(
        self,
        name,
        specialization,
        phone
    ):

        self.cursor.execute("""
        INSERT INTO therapists(
            name,
            specialization,
            phone
        )
        VALUES(?,?,?)
        """,
        (
            name,
            specialization,
            phone
        ))

        self.conn.commit()

    def get_therapists(self):

        query = """
        SELECT *
        FROM therapists
        ORDER BY therapist_id DESC
        """

        return pd.read_sql(query, self.conn)

    def get_therapist(self, therapist_id):

        self.cursor.execute("""
        SELECT *
        FROM therapists
        WHERE therapist_id=?
        """,
        (therapist_id,)
        )

        return self.cursor.fetchone()

    def update_therapist(
        self,
        therapist_id,
        name,
        specialization,
        phone
    ):

        self.cursor.execute("""
        UPDATE therapists
        SET
            name=?,
            specialization=?,
            phone=?
        WHERE therapist_id=?
        """,
        (
            name,
            specialization,
            phone,
            therapist_id
        ))

        self.conn.commit()

    def delete_therapist(self, therapist_id):

        self.cursor.execute("""
        DELETE FROM appointments
        WHERE therapist_id=?
        """,
        (therapist_id,)
        )

        self.cursor.execute("""
        DELETE FROM therapists
        WHERE therapist_id=?
        """,
        (therapist_id,)
        )

        self.conn.commit()

    def search_therapists(self, keyword):

        query = """
        SELECT *
        FROM therapists
        WHERE
            name LIKE ?
            OR specialization LIKE ?
            OR phone LIKE ?
        ORDER BY name
        """

        return pd.read_sql(
            query,
            self.conn,
            params=(
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

    # =====================================================
    # APPOINTMENT METHODS
    # =====================================================

    def book_appointment(
        self,
        client_id,
        therapist_id,
        visit_date,
        visit_time
    ):

        self.cursor.execute("""
        INSERT INTO appointments(
            client_id,
            therapist_id,
            visit_date,
            visit_time,
            status
        )
        VALUES(?,?,?,?,?)
        """,
        (
            client_id,
            therapist_id,
            visit_date,
            visit_time,
            "Booked"
        ))

        self.conn.commit()

    def get_appointments(self):

        query = """
        SELECT
            a.appointment_id,
            c.name AS client_name,
            t.name AS therapist_name,
            a.client_id,
            a.therapist_id,
            a.visit_date,
            a.visit_time,
            a.status
        FROM appointments a
        LEFT JOIN clients c
            ON a.client_id = c.client_id
        LEFT JOIN therapists t
            ON a.therapist_id = t.therapist_id
        ORDER BY a.visit_date DESC,
                 a.visit_time DESC
        """

        return pd.read_sql(query, self.conn)

    def get_appointment(self, appointment_id):

        self.cursor.execute("""
        SELECT *
        FROM appointments
        WHERE appointment_id=?
        """,
        (appointment_id,)
        )

        return self.cursor.fetchone()

    def update_appointment(
        self,
        appointment_id,
        client_id,
        therapist_id,
        visit_date,
        visit_time,
        status
    ):

        self.cursor.execute("""
        UPDATE appointments
        SET
            client_id=?,
            therapist_id=?,
            visit_date=?,
            visit_time=?,
            status=?
        WHERE appointment_id=?
        """,
        (
            client_id,
            therapist_id,
            visit_date,
            visit_time,
            status,
            appointment_id
        ))

        self.conn.commit()

    def cancel_appointment(self, appointment_id):

        self.cursor.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE appointment_id=?
        """,
        (appointment_id,)
        )

        self.conn.commit()

    def delete_appointment(self, appointment_id):

        self.cursor.execute("""
        DELETE FROM appointments
        WHERE appointment_id=?
        """,
        (appointment_id,)
        )

        self.conn.commit()

    def search_appointments(self, keyword):

        query = """
        SELECT
            a.appointment_id,
            c.name AS client_name,
            t.name AS therapist_name,
            a.visit_date,
            a.visit_time,
            a.status
        FROM appointments a
        LEFT JOIN clients c
            ON a.client_id = c.client_id
        LEFT JOIN therapists t
            ON a.therapist_id = t.therapist_id
        WHERE
            c.name LIKE ?
            OR t.name LIKE ?
            OR a.status LIKE ?
        ORDER BY a.visit_date DESC
        """

        return pd.read_sql(
            query,
            self.conn,
            params=(
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )
    
    # =====================================================
    # TREATMENT PROGRESS
    # =====================================================

    def update_progress(
        self,
        client_id,
        completed_sessions
    ):

        self.cursor.execute("""
        UPDATE clients
        SET completed_sessions=?
        WHERE client_id=?
        """,
        (
            completed_sessions,
            client_id
        ))

        self.conn.commit()

    def calculate_progress(self, client_id):

        self.cursor.execute("""
        SELECT
            name,
            completed_sessions,
            total_sessions
        FROM clients
        WHERE client_id=?
        """,
        (client_id,)
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        name, completed, total = row

        progress = 0

        if total and total > 0:
            progress = (completed / total) * 100

        return {
            "name": name,
            "completed": completed,
            "total": total,
            "progress": round(progress, 1)
        }

    def get_progress_summary(self):

        query = """
        SELECT
            client_id,
            name,
            addiction,
            completed_sessions,
            total_sessions,
            ROUND(
                CASE
                    WHEN total_sessions > 0
                    THEN (completed_sessions * 100.0 / total_sessions)
                    ELSE 0
                END,
                1
            ) AS progress
        FROM clients
        ORDER BY name
        """

        return pd.read_sql(query, self.conn)

    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    def total_clients(self):

        self.cursor.execute(
            "SELECT COUNT(*) FROM clients"
        )

        return self.cursor.fetchone()[0]

    def total_therapists(self):

        self.cursor.execute(
            "SELECT COUNT(*) FROM therapists"
        )

        return self.cursor.fetchone()[0]

    def total_appointments(self):

        self.cursor.execute(
            "SELECT COUNT(*) FROM appointments"
        )

        return self.cursor.fetchone()[0]

    def booked_appointments(self):

        self.cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Booked'
        """)

        return self.cursor.fetchone()[0]

    def cancelled_appointments(self):

        self.cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Cancelled'
        """)

        return self.cursor.fetchone()[0]

    # =====================================================
    # CHART DATA
    # =====================================================

    def gender_distribution(self):

        query = """
        SELECT
            gender,
            COUNT(*) AS total
        FROM clients
        GROUP BY gender
        """

        return pd.read_sql(query, self.conn)

    def addiction_distribution(self):

        query = """
        SELECT
            addiction,
            COUNT(*) AS total
        FROM clients
        GROUP BY addiction
        ORDER BY total DESC
        """

        return pd.read_sql(query, self.conn)

    # =====================================================
    # EXPORT HELPERS
    # =====================================================

    def export_clients(self):

        return self.get_clients()

    def export_therapists(self):

        return self.get_therapists()

    def export_appointments(self):

        return self.get_appointments()

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    def close(self):

        if self.conn:
            self.conn.close()

            import streamlit as st
import streamlit_shadcn_ui as ui
import plotly.express as px
from database import Database

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Rehabilitation Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# DATABASE
# =====================================================

db = Database()

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

.main-title{
    text-align:center;
    color:#2563eb;
    font-size:42px;
    font-weight:bold;
}

.subtitle{
    text-align:center;
    color:gray;
    margin-bottom:25px;
}

.metric-label{
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🏥 Rehabilitation")

    st.markdown("---")

    st.success(
        "Management System"
    )

    st.write(
        """
        Use the Pages menu to manage:

        - Dashboard
        - Clients
        - Therapists
        - Appointments
        - Treatment Progress
        """
    )

    st.markdown("---")

    st.caption("Version 1.0")

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<h1 class='main-title'>🏥 Rehabilitation Management Dashboard</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='subtitle'>Addiction Recovery & Therapy Management System</p>",
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

clients_df = db.get_clients()
therapists_df = db.get_therapists()
appointments_df = db.get_appointments()

total_clients = db.total_clients()
total_therapists = db.total_therapists()
total_appointments = db.total_appointments()

booked = db.booked_appointments()
cancelled = db.cancelled_appointments()

# =====================================================
# METRIC CARDS
# =====================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    ui.metric_card(
        title="Clients",
        content=str(total_clients),
        description="Registered Clients",
        key="clients_metric"
    )

with c2:
    ui.metric_card(
        title="Therapists",
        content=str(total_therapists),
        description="Available Therapists",
        key="therapists_metric"
    )

with c3:
    ui.metric_card(
        title="Appointments",
        content=str(total_appointments),
        description="Total Appointments",
        key="appointments_metric"
    )

with c4:
    ui.metric_card(
        title="Cancelled",
        content=str(cancelled),
        description="Cancelled Visits",
        key="cancelled_metric"
    )

st.divider()

# =====================================================
# SYSTEM STATUS
# =====================================================

left, right = st.columns([3, 1])

with left:

    st.subheader("System Overview")

    st.write("""
The Rehabilitation Management System provides a centralized platform
for managing rehabilitation clients, therapists, appointments and
treatment progress.

Use the pages listed in the sidebar to access each module.
""")

with right:

    ui.alert_dialog(
        show=True,
        title="System Status",
        description="Database connected successfully."
    )

st.divider()

# =====================================================
# DASHBOARD CHARTS
# =====================================================

st.subheader("📊 Dashboard Analytics")

left_chart, right_chart = st.columns(2)

# -----------------------------------------------------
# CLIENT GENDER DISTRIBUTION
# -----------------------------------------------------

with left_chart:

    st.markdown("### Client Gender Distribution")

    gender_df = db.gender_distribution()

    if not gender_df.empty:

        fig = px.pie(
            gender_df,
            names="gender",
            values="total",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No client records available.")

# -----------------------------------------------------
# ADDICTION DISTRIBUTION
# -----------------------------------------------------

with right_chart:

    st.markdown("### Addiction Categories")

    addiction_df = db.addiction_distribution()

    if not addiction_df.empty:

        fig = px.bar(
            addiction_df,
            x="addiction",
            y="total",
            text="total"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No addiction data available.")

st.divider()

# =====================================================
# TREATMENT PROGRESS CHART
# =====================================================

st.subheader("📈 Client Treatment Progress")

progress_df = db.get_progress_summary()

if not progress_df.empty:

    fig = px.bar(
        progress_df,
        x="name",
        y="progress",
        color="progress",
        text="progress",
        labels={
            "name": "Client",
            "progress": "Progress (%)"
        }
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.info("No treatment progress available.")

st.divider()

# =====================================================
# RECENT CLIENTS & APPOINTMENTS
# =====================================================

left_table, right_table = st.columns(2)

# -----------------------------------------------------
# RECENT CLIENTS
# -----------------------------------------------------

with left_table:

    st.subheader("👥 Recent Clients")

    if not clients_df.empty:

        display = clients_df[
            [
                "client_id",
                "name",
                "gender",
                "addiction",
                "completed_sessions",
                "total_sessions"
            ]
        ].head(5)

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No clients registered.")

# -----------------------------------------------------
# RECENT APPOINTMENTS
# -----------------------------------------------------

with right_table:

    st.subheader("📅 Recent Appointments")

    if not appointments_df.empty:

        display = appointments_df[
            [
                "appointment_id",
                "client_name",
                "therapist_name",
                "visit_date",
                "status"
            ]
        ].head(5)

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No appointments found.")

st.divider()
# =====================================================
# QUICK SUMMARY
# =====================================================

st.subheader("📋 System Summary")

summary1, summary2, summary3 = st.columns(3)

with summary1:
    st.success(f"👥 Registered Clients: {total_clients}")
    st.info(f"🩺 Registered Therapists: {total_therapists}")

with summary2:
    st.success(f"📅 Total Appointments: {total_appointments}")
    st.warning(f"❌ Cancelled Appointments: {cancelled}")

with summary3:
    if total_clients > 0:
        average = total_appointments / total_clients
    else:
        average = 0

    st.success(f"📈 Average Visits per Client: {average:.2f}")

    completion = 0

    if total_appointments > 0:
        completion = (booked / total_appointments) * 100

    st.info(f"✅ Active Appointment Rate: {completion:.1f}%")

st.divider()

# =====================================================
# DATABASE SUMMARY
# =====================================================

st.subheader("📊 Database Overview")

overview = {
    "Clients": total_clients,
    "Therapists": total_therapists,
    "Appointments": total_appointments,
    "Booked": booked,
    "Cancelled": cancelled
}

st.dataframe(
    overview.items(),
    column_config={
        0: "Category",
        1: "Total"
    },
    hide_index=True,
    use_container_width=True
)

st.divider()

# =====================================================
# EXPORT SECTION
# =====================================================

st.subheader("📥 Export Data")

export1, export2, export3 = st.columns(3)

with export1:
    csv = clients_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Clients",
        csv,
        "clients.csv",
        "text/csv",
        use_container_width=True
    )

with export2:
    csv = therapists_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Therapists",
        csv,
        "therapists.csv",
        "text/csv",
        use_container_width=True
    )

with export3:
    csv = appointments_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Appointments",
        csv,
        "appointments.csv",
        "text/csv",
        use_container_width=True
    )

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    <hr>

    <center>

    <h4>
    🏥 Rehabilitation Management System
    </h4>

    <p>
    Built with Streamlit • SQLite • Plotly • streamlit-shadcn-ui
    </p>

    </center>
    """,
    unsafe_allow_html=True
)

import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd

from database import Database

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Client Management",
    page_icon="👥",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================

db = Database()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("👥 Client Management")

st.caption(
    "Register, update, search and manage rehabilitation clients."
)

st.divider()

# =====================================================
# LOAD CLIENTS
# =====================================================

clients = db.get_clients()

# =====================================================
# TABS
# =====================================================

tab = ui.tabs(
    options=[
        "Add Client",
        "View Clients",
        "Update Client",
        "Delete Client"
    ],
    default_value="Add Client",
    key="client_tabs"
)

# =====================================================
# ADD CLIENT
# =====================================================

if tab == "Add Client":

    st.subheader("➕ Register New Client")

    with st.container(border=True):

        left, right = st.columns(2)
        
    with left:
            name = st.text_input(
                "Client Name"
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=18
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

    with right:

            addiction = st.text_input(
                "Addiction Type"
            )

            admission_date = st.date_input(
                "Admission Date"
            )

            total_sessions = st.number_input(
                "Total Therapy Sessions",
                min_value=1,
                value=10
            )

    st.divider()

submitted = ui.button(
            text="Add Client",
            key="add_client_button"
        )

if submitted:

            if not name.strip():
                st.error(
                    "Client name is required."
                )

            elif not addiction.strip():
                st.error(
                    "Addiction type is required."
                )

            else:

                db.add_client(
                    name=name,
                    age=int(age),
                    gender=gender,
                    addiction=addiction,
                    admission_date=str(admission_date),
                    total_sessions=int(total_sessions)
                )

                st.success(
                    f"✅ {name} has been registered successfully."
                )

                st.rerun()

                # =====================================================
# VIEW CLIENTS
# =====================================================

elif tab == "View Clients":

    st.subheader("📋 Registered Clients")

    clients = db.get_clients()

    if clients.empty:
        st.info("No clients have been registered yet.")

    else:

        search = st.text_input(
            "🔍 Search by Name, Gender or Addiction",
            placeholder="Type to search..."
        )

        filtered = clients.copy()

        if search.strip():

            keyword = search.strip().lower()

            filtered = filtered[
                filtered["name"].str.lower().str.contains(keyword, na=False)
                |
                filtered["gender"].str.lower().str.contains(keyword, na=False)
                |
                filtered["addiction"].str.lower().str.contains(keyword, na=False)
            ]

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "Total Clients",
                len(filtered)
            )

        with m2:
            total_sessions = int(
                filtered["total_sessions"].sum()
            )

            st.metric(
                "Therapy Sessions",
                total_sessions
            )

        with m3:
            completed = int(
                filtered["completed_sessions"].sum()
            )

            st.metric(
                "Completed Sessions",
                completed
            )

        st.divider()

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # =====================================================
        # CLIENT PROGRESS SUMMARY
        # =====================================================

        if not filtered.empty:

            summary = filtered.copy()

            summary["Progress (%)"] = (
                summary["completed_sessions"]
                .div(summary["total_sessions"].replace(0, 1))
                * 100
            ).round(1)

            st.subheader("📈 Client Progress Summary")

            st.dataframe(
                summary[
                    [
                        "client_id",
                        "name",
                        "addiction",
                        "completed_sessions",
                        "total_sessions",
                        "Progress (%)"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            csv = summary.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download Client Report (CSV)",
                data=csv,
                file_name="clients_report.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.info("No matching clients found.")

            # =====================================================
# UPDATE CLIENT
# =====================================================

elif tab == "Update Client":

    st.subheader("✏️ Update Client")

    clients = db.get_clients()

    if clients.empty:
        st.info("No clients available to update.")

    else:

        options = {
            f"{row.client_id} - {row.name}": row.client_id
            for _, row in clients.iterrows()
        }

        selected = st.selectbox(
            "Select Client",
            list(options.keys())
        )

        client_id = options[selected]

        client = clients[
            clients["client_id"] == client_id
        ].iloc[0]

        with st.form("update_client_form"):

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Client Name",
                    value=client["name"]
                )

                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=int(client["age"])
                )

                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=[
                        "Male",
                        "Female",
                        "Other"
                    ].index(client["gender"])
                    if client["gender"] in ["Male", "Female", "Other"]
                    else 0
                )

            with col2:

                addiction = st.text_input(
                    "Addiction Type",
                    value=client["addiction"]
                )

                admission_date = st.text_input(
                    "Admission Date",
                    value=str(client["admission_date"])
                )

                total_sessions = st.number_input(
                    "Total Therapy Sessions",
                    min_value=1,
                    value=int(client["total_sessions"])
                )

            submitted = st.form_submit_button(
                "💾 Update Client"
            )

            if submitted:

                if not name.strip():
                    st.error("Client name is required.")

                elif not addiction.strip():
                    st.error("Addiction type is required.")

                else:

                    db.update_client(
                        client_id=client_id,
                        name=name,
                        age=int(age),
                        gender=gender,
                        addiction=addiction,
                        admission_date=admission_date,
                        total_sessions=int(total_sessions)
                    )

                    st.success(
                        "✅ Client updated successfully."
                    )

                    st.rerun()
                    
                    # =====================================================
# DELETE CLIENT
# =====================================================

elif tab == "Delete Client":

    st.subheader("🗑 Delete Client")

    clients = db.get_clients()

    if clients.empty:
        st.info("No clients available.")

    else:

        options = {
            f"{row.client_id} - {row.name}": row.client_id
            for _, row in clients.iterrows()
        }

        selected = st.selectbox(
            "Select Client",
            list(options.keys()),
            key="delete_client_select"
        )

        client_id = options[selected]

        client = clients[
            clients["client_id"] == client_id
        ].iloc[0]

        with st.container(border=True):

            st.warning(
                "Deleting this client will also delete all associated appointments."
            )

            c1, c2 = st.columns(2)

            with c1:
                st.write("**Name**")
                st.write(client["name"])

                st.write("**Gender**")
                st.write(client["gender"])

                st.write("**Age**")
                st.write(client["age"])

            with c2:
                st.write("**Addiction**")
                st.write(client["addiction"])

                st.write("**Admission Date**")
                st.write(client["admission_date"])

                st.write("**Total Sessions**")
                st.write(client["total_sessions"])

            st.divider()

            confirm = st.checkbox(
                "I understand this action cannot be undone.",
                key="confirm_delete_client"
            )

            if confirm:

                if ui.button(
                    text="Delete Client",
                    key="delete_client_button"
                ):

                    db.delete_client(client_id)

                    st.success(
                        "✅ Client deleted successfully."
                    )

                    st.rerun()
                    import streamlit as st
import streamlit_shadcn_ui as ui

from database import Database

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Therapist Management",
    page_icon="🩺",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================

db = Database()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🩺 Therapist Management")

st.caption(
    "Register, update and manage rehabilitation therapists."
)

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

therapists = db.get_therapists()

# =====================================================
# TABS
# =====================================================

tab = ui.tabs(
    options=[
        "Add Therapist",
        "View Therapists",
        "Update Therapist",
        "Delete Therapist"
    ],
    default_value="Add Therapist",
    key="therapist_tabs"
)

# =====================================================
# ADD THERAPIST
# =====================================================

if tab == "Add Therapist":

    st.subheader("➕ Register New Therapist")

    with st.container(border=True):

        name = st.text_input(
            "Therapist Name"
        )

        specialization = st.text_input(
            "Specialization"
        )

        phone = st.text_input(
            "Phone Number"
        )

        st.divider()

        submitted = ui.button(
            text="Add Therapist",
            key="add_therapist_button"
        )

        if submitted:

            if not name.strip():
                st.error(
                    "Therapist name is required."
                )

            elif not specialization.strip():
                st.error(
                    "Specialization is required."
                )

            else:

                db.add_therapist(
                    name=name,
                    specialization=specialization,
                    phone=phone
                )

                st.success(
                    f"✅ {name} has been registered successfully."
                )

                st.rerun()
                # =====================================================
# VIEW THERAPISTS
# =====================================================

elif tab == "View Therapists":

    st.subheader("📋 Registered Therapists")

    therapists = db.get_therapists()

    if therapists.empty:
        st.info("No therapists have been registered yet.")

    else:

        search = st.text_input(
            "🔍 Search by Name, Specialization or Phone",
            placeholder="Type to search..."
        )

        filtered = therapists.copy()

        if search.strip():

            keyword = search.strip().lower()

            filtered = filtered[
                filtered["name"].str.lower().str.contains(keyword, na=False)
                |
                filtered["specialization"].str.lower().str.contains(keyword, na=False)
                |
                filtered["phone"].astype(str).str.lower().str.contains(keyword, na=False)
            ]

        # =====================================================
        # METRICS
        # =====================================================

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Total Therapists",
                len(filtered)
            )

        with c2:
            st.metric(
                "Specializations",
                filtered["specialization"].nunique()
            )

        st.divider()

        # =====================================================
        # THERAPIST TABLE
        # =====================================================

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # =====================================================
        # DOWNLOAD CSV
        # =====================================================

        csv = filtered.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Therapist List",
            data=csv,
            file_name="therapists.csv",
            mime="text/csv",
            use_container_width=True
        )
        # =====================================================
# UPDATE THERAPIST
# =====================================================

elif tab == "Update Therapist":

    st.subheader("✏️ Update Therapist")

    therapists = db.get_therapists()

    if therapists.empty:
        st.info("No therapists available to update.")

    else:

        options = {
            f"{row.therapist_id} - {row.name}": row.therapist_id
            for _, row in therapists.iterrows()
        }

        selected = st.selectbox(
            "Select Therapist",
            list(options.keys())
        )

        therapist_id = options[selected]

        therapist = therapists[
            therapists["therapist_id"] == therapist_id
        ].iloc[0]

        with st.form("update_therapist_form"):

            name = st.text_input(
                "Therapist Name",
                value=therapist["name"]
            )

            specialization = st.text_input(
                "Specialization",
                value=therapist["specialization"]
            )

            phone = st.text_input(
                "Phone Number",
                value=str(therapist["phone"])
            )

            submitted = st.form_submit_button(
                "💾 Update Therapist"
            )

            if submitted:

                if not name.strip():
                    st.error(
                        "Therapist name is required."
                    )

                elif not specialization.strip():
                    st.error(
                        "Specialization is required."
                    )

                else:

                    db.update_therapist(
                        therapist_id=therapist_id,
                        name=name,
                        specialization=specialization,
                        phone=phone
                    )

                    st.success(
                        "✅ Therapist updated successfully."
                    )

                    st.rerun()
                    def update_therapist(
    self,
    therapist_id,
    name,
    specialization,
    phone
):self.cursor.execute("""
    UPDATE therapists
    SET
        name=?,
        specialization=?,
        phone=?
    WHERE therapist_id=?
    """,
    (
        name,
        specialization,
        phone,
        therapist_id
    ))

    self.conn.commit()

    # =====================================================
# DELETE THERAPIST
# =====================================================

elif tab == "Delete Therapist":

    st.subheader("🗑 Delete Therapist")

    therapists = db.get_therapists()

    if therapists.empty:
        st.info("No therapists available.")

    else:

        options = {
            f"{row.therapist_id} - {row.name}": row.therapist_id
            for _, row in therapists.iterrows()
        }

        selected = st.selectbox(
            "Select Therapist",
            list(options.keys()),
            key="delete_therapist_select"
        )

        therapist_id = options[selected]

        therapist = therapists[
            therapists["therapist_id"] == therapist_id
        ].iloc[0]

        with st.container(border=True):

            st.warning(
                "Deleting this therapist will also remove all appointments assigned to them."
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name**")
                st.write(therapist["name"])

                st.write("**Specialization**")
                st.write(therapist["specialization"])

            with col2:
                st.write("**Phone Number**")
                st.write(therapist["phone"])

                assigned = len(
                    db.get_appointments()[
                        db.get_appointments()["therapist_id"] == therapist_id
                    ]
                )

                st.write("**Assigned Appointments**")
                st.write(assigned)

            st.divider()

            confirm = st.checkbox(
                "I understand this action cannot be undone.",
                key="confirm_delete_therapist"
            )

            if confirm:

                if ui.button(
                    text="Delete Therapist",
                    key="delete_therapist_button"
                ):

                    db.delete_therapist(therapist_id)

                    st.success(
                        "✅ Therapist deleted successfully."
                    )

                    st.rerun()

                    import streamlit as st
import streamlit_shadcn_ui as ui
from database import Database

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Appointments",
    page_icon="📅",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================

db = Database()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("📅 Therapy Appointment Management")

st.caption(
    "Book, view, and manage therapy sessions between clients and therapists."
)

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

clients = db.get_clients()
therapists = db.get_therapists()

# =====================================================
# TABS
# =====================================================

tab = ui.tabs(
    options=[
        "Book Appointment",
        "View Appointments",
        "Cancel Appointment"
    ],
    default_value="Book Appointment",
    key="appointment_tabs"
)

# =====================================================
# BOOK APPOINTMENT
# =====================================================

if tab == "Book Appointment":

    st.subheader("➕ Book New Appointment")

    if clients.empty:
        st.warning("No clients available. Please add clients first.")

    elif therapists.empty:
        st.warning("No therapists available. Please add therapists first.")

    else:

        client_options = {
            f"{row.client_id} - {row.name}": row.client_id
            for _, row in clients.iterrows()
        }

        therapist_options = {
            f"{row.therapist_id} - {row.name}": row.therapist_id
            for _, row in therapists.iterrows()
        }

        with st.container(border=True):

            col1, col2 = st.columns(2)

            with col1:

                client_selected = st.selectbox(
                    "Select Client",
                    list(client_options.keys())
                )

                visit_date = st.date_input("Visit Date")

            with col2:

                therapist_selected = st.selectbox(
                    "Select Therapist",
                    list(therapist_options.keys())
                )

                visit_time = st.time_input("Visit Time")

            st.divider()

            submitted = ui.button(
                text="Book Appointment",
                key="book_appointment_button"
            )

            if submitted:

                db.book_appointment(
                    client_id=client_options[client_selected],
                    therapist_id=therapist_options[therapist_selected],
                    visit_date=str(visit_date),
                    visit_time=str(visit_time)
                )

                st.success("✅ Appointment booked successfully.")

                st.rerun()

                # =====================================================
# VIEW APPOINTMENTS
# =====================================================

elif tab == "View Appointments":

    st.subheader("📋 All Appointments")

    appointments = db.get_appointments()

    if appointments.empty:
        st.info("No appointments found.")

    else:

        search = st.text_input(
            "🔍 Search by Client or Therapist",
            placeholder="Type a name..."
        )

        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Booked", "Cancelled"]
        )

        filtered = appointments.copy()

        # -------------------------------------------------
        # SEARCH FILTER
        # -------------------------------------------------

        if search.strip():

            keyword = search.strip().lower()

            filtered = filtered[
                filtered["client_name"].str.lower().str.contains(keyword, na=False)
                |
                filtered["therapist_name"].str.lower().str.contains(keyword, na=False)
            ]

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        # =====================================================
        # METRICS
        # =====================================================

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Total", len(filtered))

        with c2:
            st.metric(
                "Booked",
                len(filtered[filtered["status"] == "Booked"])
            )

        with c3:
            st.metric(
                "Cancelled",
                len(filtered[filtered["status"] == "Cancelled"])
            )

        st.divider()

        # =====================================================
        # TABLE VIEW
        # =====================================================

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
# CANCEL APPOINTMENT
# =====================================================

elif tab == "Cancel Appointment":

    st.subheader("❌ Cancel Appointment")

    appointments = db.get_appointments()

    booked = appointments[appointments["status"] == "Booked"]

    if booked.empty:
        st.info("No active (booked) appointments available.")

    else:

        options = {
            f"{row.appointment_id} | {row.client_name} → {row.therapist_name} | {row.visit_date} {row.visit_time}":
            row.appointment_id
            for _, row in booked.iterrows()
        }

        selected = st.selectbox(
            "Select Appointment",
            list(options.keys())
        )

        appointment_id = options[selected]

        selected_row = booked[
            booked["appointment_id"] == appointment_id
        ].iloc[0]

        with st.container(border=True):

            st.warning(
                "⚠️ This appointment will be marked as CANCELLED."
            )

            st.write("**Client:**", selected_row["client_name"])
            st.write("**Therapist:**", selected_row["therapist_name"])
            st.write("**Date:**", selected_row["visit_date"])
            st.write("**Time:**", selected_row["visit_time"])

            st.divider()

            confirm = st.checkbox(
                "I confirm cancellation of this appointment."
            )

            if confirm:

                if ui.button(
                    text="Cancel Appointment",
                    key="cancel_appointment_button"
                ):

                    db.cancel_appointment(appointment_id)

                    st.success("✅ Appointment cancelled successfully.")

                    st.rerun()

                    # =====================================================
# EXPORT APPOINTMENTS
# =====================================================

st.divider()

st.subheader("📥 Export Appointments")

appointments = db.get_appointments()

if appointments.empty:

    st.info("No appointment data available to export.")

else:

    # =====================================================
    # EXPORT FULL DATA
    # =====================================================

    csv_all = appointments.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download All Appointments",
        data=csv_all,
        file_name="appointments_all.csv",
        mime="text/csv",
        use_container_width=True
    )

    # =====================================================
    # OPTIONAL FILTERED EXPORT
    # =====================================================

    st.markdown("### Filtered Export")

    col1, col2 = st.columns(2)

    with col1:
        export_status = st.selectbox(
            "Select Status for Export",
            ["All", "Booked", "Cancelled"],
            key="export_status"
        )

    with col2:
        keyword = st.text_input(
            "Search Client/Therapist (optional)",
            key="export_search"
        )

    export_df = appointments.copy()

    if export_status != "All":
        export_df = export_df[export_df["status"] == export_status]

    if keyword.strip():

        k = keyword.strip().lower()

        export_df = export_df[
            export_df["client_name"].str.lower().str.contains(k, na=False)
            |
            export_df["therapist_name"].str.lower().str.contains(k, na=False)
        ]

    st.write(f"📊 Exporting {len(export_df)} records")

    csv_filtered = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Filtered Appointments",
        data=csv_filtered,
        file_name="appointments_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "🏥 Rehabilitation Management System | Appointments Module Complete"
)

import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
from database import Database

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Treatment Progress",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================

db = Database()

# =====================================================
# TITLE
# =====================================================

st.title("📈 Treatment Progress Management")

st.caption(
    "Track and update client recovery progress."
)

st.divider()

# =====================================================
# LOAD CLIENTS
# =====================================================

clients = db.get_clients()

# =====================================================
# TABS
# =====================================================

tab = ui.tabs(
    options=[
        "Update Progress",
        "View Progress"
    ],
    default_value="Update Progress",
    key="progress_tabs"
)

# =====================================================
# UPDATE PROGRESS
# =====================================================

if tab == "Update Progress":

    st.subheader("✏️ Update Client Progress")

    if clients.empty:
        st.info("No clients available.")

    else:

        options = {
            f"{row.client_id} - {row.name}": row.client_id
            for _, row in clients.iterrows()
        }

        selected = st.selectbox(
            "Select Client",
            list(options.keys())
        )

        client_id = options[selected]

        client = clients[
            clients["client_id"] == client_id
        ].iloc[0]

        st.write(f"**Client:** {client['name']}")
        st.write(f"**Total Sessions:** {client['total_sessions']}")

        completed = st.number_input(
            "Completed Sessions",
            min_value=0,
            max_value=int(client["total_sessions"]),
            value=int(client["completed_sessions"])
        )

        submitted = ui.button(
            text="Update Progress",
            key="update_progress_btn"
        )

        if submitted:

            db.update_progress(
                client_id,
                completed
            )

            st.success("✅ Progress updated successfully.")

            st.rerun()

            # =====================================================
# VIEW PROGRESS
# =====================================================

elif tab == "View Progress":

    st.subheader("📊 Client Treatment Progress")

    clients = db.get_clients()

    if clients.empty:
        st.info("No client progress data available.")

    else:

        options = {
            f"{row.client_id} - {row.name}": row.client_id
            for _, row in clients.iterrows()
        }

        selected = st.selectbox(
            "Select Client",
            list(options.keys())
        )

        client_id = options[selected]

        result = db.calculate_progress(client_id)

        if result is None:
            st.error("Client not found.")

        else:

            # =================================================
            # METRICS
            # =================================================

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Completed Sessions",
                    result["completed"]
                )

            with c2:
                st.metric(
                    "Total Sessions",
                    result["total"]
                )

            with c3:
                st.metric(
                    "Progress",
                    f"{result['progress']}%"
                )

            st.divider()

            # =================================================
            # PROGRESS BAR
            # =================================================

            st.progress(result["progress"] / 100)

            if result["progress"] == 100:
                st.success("🎉 Treatment Completed")

            elif result["progress"] >= 75:
                st.success("Excellent Progress")

            elif result["progress"] >= 50:
                st.info("Good Progress")

            elif result["progress"] >= 25:
                st.warning("Moderate Progress")

            else:
                st.error("Just Started")

            st.divider()

            # =================================================
            # REPORT GENERATION
            # =================================================

            report = f"""
Treatment Progress Report

Client: {result['name']}
Completed Sessions: {result['completed']}
Total Sessions: {result['total']}
Progress: {result['progress']}%
"""

            st.download_button(
                label="📄 Download Progress Report",
                data=report,
                file_name="progress_report.txt",
                mime="text/plain"
            )

            # =====================================================
# OVERALL PROGRESS SUMMARY
# =====================================================

st.divider()

st.subheader("📋 All Clients Progress Overview")

clients = db.get_clients()

if clients.empty:

    st.info("No client data available.")

else:

    summary = clients.copy()

    # =====================================================
    # CALCULATE PROGRESS
    # =====================================================

    summary["Progress (%)"] = (
        summary["completed_sessions"]
        .div(summary["total_sessions"].replace(0, 1))
        * 100
    ).round(1)

    # =====================================================
    # DISPLAY TABLE
    # =====================================================

    st.dataframe(
        summary[
            [
                "client_id",
                "name",
                "addiction",
                "completed_sessions",
                "total_sessions",
                "Progress (%)"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = summary.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Full Progress Report (CSV)",
        data=csv,
        file_name="treatment_progress_report.csv",
        mime="text/csv",
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "📈 Treatment Progress Module Complete | Rehabilitation Management System"
)


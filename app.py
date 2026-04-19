# ================= IMPORTS =================
import matplotlib.pyplot as plt
plt.style.use('default')
from database import create_tables, add_task, get_tasks, delete_task, log_study_time, update_task_status
from auth import register_user, login_user
from planner import generate_study_plan

from datetime import datetime
import streamlit as st
import pandas as pd
import time

# ================= CONFIG =================
st.set_page_config(page_title="FocusFlow", layout="wide")

# ================= SESSION =================
for key, default in {
    "user": None,
    "study_time": 0,
    "end_time": None,
    "running": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

create_tables()

# ================= UI CARD =================
def card(title, value):
    st.markdown(f"""
    <div class="card">
        <div class="subtext">{title}</div>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

# ================= TITLE =================
st.title("🚀 FocusFlow – Study Planner")

# ================= THEME =================
theme = st.toggle("🌙 Dark Mode")

if theme:
    bg = "#0f172a"
    sidebar = "#020617"
    card_bg = "#1e293b"
    text = "#e2e8f0"
    subtext = "#94a3b8"
else:
    bg = "#f8fafc"
    sidebar = "#ffffff"
    card_bg = "#ffffff"
    text = "#111827"
    subtext = "#64748b"

st.markdown(f"""
<style>
html, body, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}

header[data-testid="stHeader"] {{
    background-color: {bg} !important;
}}

div[data-testid="stToolbar"] {{
    background-color: {bg} !important;
}}

div[data-testid="stAppViewContainer"] {{
    background-color: {bg} !important;
}}

section[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {text} !important;
}}

p, span, div {{
    color: {text} !important;
}}

input, textarea {{
    background-color: {card_bg} !important;
    color: {text} !important;
}}

div[data-baseweb="select"] > div {{
    background-color: {card_bg} !important;
    color: {text} !important;
}}

.stButton>button {{
    background-color: #4f46e5 !important;
    color: white !important;
}}

.card {{
    background-color: {card_bg};
    padding: 20px;
    border-radius: 16px;
}}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.user:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("## 🔐 Welcome to FocusFlow")
    st.caption("Smart Study Planner")

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("🚀 Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("🆕 Register"):
        success, msg = register_user(username, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= MAIN APP =================
else:

    user_id = st.session_state.user[0]
    username = st.session_state.user[1]
    tasks = get_tasks(user_id)

    st.sidebar.markdown("## 🚀 FocusFlow")
    st.sidebar.markdown('<div class="subtext">Stay consistent, stay ahead</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.success(f"👋 {username}")

    menu = st.sidebar.radio(
        "",
        ["🏠 Dashboard", "📊 Analytics", "📌 Tasks", "🎯 Focus Mode"]
    )

    # ================= DASHBOARD =================
    if menu == "🏠 Dashboard":

        completed = sum(1 for t in tasks if t[6] == "Completed")
        pending = sum(1 for t in tasks if t[6] == "Pending")

        st.markdown("## 📊 Overview")
        st.markdown('<div class="subtext">Your study performance at a glance</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            card("Total Tasks", len(tasks))
        with c2:
            card("Completed", completed)
        with c3:
            card("Pending", pending)

    # ================= ANALYTICS =================
    elif menu == "📊 Analytics":

        st.markdown("## 📊 Analytics Dashboard")
        st.markdown('<div class="subtext">Track your productivity and progress</div>', unsafe_allow_html=True)

        total = len(tasks)
        completed = sum(1 for t in tasks if t[6] == "Completed")
        pending = sum(1 for t in tasks if t[6] == "Pending")

        score = int((completed / total) * 100) if total else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            card("Productivity", f"{score}%")
        with c2:
            card("Completed", completed)
        with c3:
            card("Pending", pending)

        st.markdown("### 📈 Productivity Progress")
        st.progress(score / 100)

        # Bar Chart
        st.markdown("### 📊 Task Distribution")
        fig1, ax1 = plt.subplots()
        ax1.bar(["Completed", "Pending"], [completed, pending])
        st.pyplot(fig1)

        # Pie Chart (FIXED INDENTATION ONLY)
        st.markdown("### 🥧 Completion Ratio")
        fig2, ax2 = plt.subplots()

        total = completed + pending

        if total == 0:
            ax2.text(0.5, 0.5, "No Data Available", ha='center', va='center')
        else:
            ax2.pie(
                [completed, pending],
                labels=["Completed", "Pending"],
                autopct="%1.1f%%"
            )

        st.pyplot(fig2)

    # ================= TASKS =================
    elif menu == "📌 Tasks":

        st.markdown("## 📌 Tasks")
        st.markdown('<div class="subtext">Manage your study tasks efficiently</div>', unsafe_allow_html=True)

        df = pd.DataFrame(tasks, columns=[
            "ID", "User", "Subject", "Deadline", "Hours", "Difficulty", "Status"
        ])

        if df.empty:
            st.warning("No tasks yet. Add your first task 👇")
        else:
            ids = df["ID"].tolist()
            df_clean = df.drop(columns=["ID", "User"])
            df_clean.insert(0, "Task No", range(1, len(df_clean) + 1))

            st.dataframe(df_clean, use_container_width=True)

            id_map = {
                f"{row['Task No']} - {row['Subject']}": ids[i]
                for i, (_, row) in enumerate(df_clean.iterrows())
            }

            selected = st.selectbox("Select Task", list(id_map.keys()))

            if st.button("Delete Task"):
                delete_task(id_map[selected])
                st.rerun()

            new_status = st.selectbox("Status", ["Pending", "Completed"])

            if st.button("Update Status"):
                update_task_status(id_map[selected], new_status)
                st.rerun()

        st.markdown("### ➕ Add Task")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            subject = st.text_input("Subject")
        with c2:
            deadline = st.date_input("Deadline")
        with c3:
            hours = st.slider("Hours", 1, 10)
        with c4:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Add Task"):
            add_task(user_id, subject, str(deadline), hours, difficulty)
            st.rerun()

    # ================= FOCUS MODE =================
    elif menu == "🎯 Focus Mode":

        study_minutes = st.number_input("Minutes", 1, 180, 25)

        if st.button("▶ Start"):
            st.session_state.running = True
            st.session_state.end_time = datetime.now().timestamp() + (study_minutes * 60)

        if st.session_state.running:
            remaining = int(st.session_state.end_time - datetime.now().timestamp())

            if remaining > 0:
                st.info(f"⏳ {remaining//60}:{remaining%60:02d}")
                time.sleep(1)
                st.rerun()
            else:
                st.success("🎉 Done!")
                log_study_time(user_id, study_minutes)
                st.session_state.running = False

    # ================= LOGOUT =================
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
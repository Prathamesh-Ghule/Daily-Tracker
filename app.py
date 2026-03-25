import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Daily Tracker", page_icon="📅")

# ---------- LOAD & SAVE ----------

def load_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

tasks = load_json("tasks.json")
progress = load_json("progress.json")

st.title"📅 Daily Tracker")
st.subheader("Track your learning, habits, and productivity daily 🚀")

# ---------- SIDEBAR ----------

selected_week = st.sidebar.selectbox(
    "Select Week",
    list(tasks.keys())
)

st.header(selected_week)

week_data = tasks[selected_week]

total_tasks = 0
completed_tasks = 0

# ---------- TASK TRACKING ----------

for day, task_list in week_data.items():
    st.subheader(day)
    
    for task in task_list:
        total_tasks += 1
        
        task_name = task["task"]
        task_desc = task["desc"]
        
        key = f"{selected_week}_{day}_{task_name}"
        
        if key not in progress:
            progress[key] = False
        
        checked = st.checkbox(
            f"{task_name} ({task_desc})",
            value=progress[key],
            key=key
        )
        
        progress[key] = checked
        
        if checked:
            completed_tasks += 1

# Save progress
save_json("progress.json", progress)

# ---------- PROGRESS BAR ----------

if total_tasks > 0:
    progress_percent = completed_tasks / total_tasks
    st.progress(progress_percent)
    st.write(f"✅ {completed_tasks}/{total_tasks} tasks completed")

# ---------- DAILY LOG ----------

st.header("📝 Daily Log")

today = str(date.today())

notes = st.text_area("What did you learn today?")
dsa = st.text_input("DSA solved (e.g., 2 easy / 1 medium)")
hours = st.slider("Hours studied", 0, 5, 2)

if st.button("Save Daily Log"):
    if "logs" not in progress:
        progress["logs"] = {}
    
    progress["logs"][today] = {
        "notes": notes,
        "dsa": dsa,
        "hours": hours
    }
    
    save_json("progress.json", progress)
    st.success("Saved successfully!")

# ---------- PREVIOUS LOGS ----------

st.header("📊 Previous Logs")

if "logs" in progress:
    for log_date, log in progress["logs"].items():
        st.write(f"📅 {log_date}")
        st.write(f"🧠 {log['notes']}")
        st.write(f"💻 {log['dsa']}")
        st.write(f"⏱ {log['hours']} hrs")
        st.write("---")

# ---------- ANALYTICS ----------

st.header("📈 Analytics Dashboard")

total_hours = 0
total_days = 0

if "logs" in progress:
    for log in progress["logs"].values():
        total_hours += log.get("hours", 0)
    total_days = len(progress["logs"])

st.write(f"⏱ Total Hours Studied: {total_hours}")
st.write(f"📅 Total Days Logged: {total_days}")

# ---------- STREAK ----------

def calculate_streak(logs):
    if not logs:
        return 0
    
    dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in logs.keys()])
    
    streak = 0
    today = datetime.today().date()
    
    for i in range(len(dates)-1, -1, -1):
        if dates[i].date() == today - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

streak = calculate_streak(progress.get("logs", {}))
st.write(f"🔥 Current Streak: {streak} days")

# ---------- WEEKLY COMPLETION ----------

weekly_completion = 0

if total_tasks > 0:
    weekly_completion = (completed_tasks / total_tasks) * 100

st.write(f"📊 Weekly Completion: {weekly_completion:.2f}%")

# ---------- OVERALL PROGRESS ----------

total_all_tasks = 0
total_completed = 0

for week, days in tasks.items():
    for day, task_list in days.items():
        for task in task_list:
            total_all_tasks += 1
            
            key = f"{week}_{day}_{task['task']}"
            if progress.get(key, False):
                total_completed += 1

if total_all_tasks > 0:
    overall = (total_completed / total_all_tasks) * 100
    st.write(f"🚀 Overall Progress: {overall:.2f}%")

# ---------- GYM TRACKER ----------

st.header("🏋️ Gym Tracker")

today = str(date.today())

if "gym" not in progress:
    progress["gym"] = {}

gym_done = st.checkbox(
    "Did you go to the gym today?",
    value=progress["gym"].get(today, False)
)

progress["gym"][today] = gym_done
save_json("progress.json", progress)

# ---------- GYM HISTORY ----------

st.subheader("📅 Gym History")

if "gym" in progress:
    for day, status in progress["gym"].items():
        status_text = "✅" if status else "❌"
        st.write(f"{day}: {status_text}")

# ---------- GYM CALENDAR ----------

st.subheader("📅 Gym Calendar (Monthly View)")

if "gym" in progress and len(progress["gym"]) > 0:

    gym_data = progress["gym"]
    
    df = pd.DataFrame(list(gym_data.items()), columns=["date", "status"])
    df["date"] = pd.to_datetime(df["date"])
    
    today_dt = datetime.today()
    
    df = df[
        (df["date"].dt.month == today_dt.month) &
        (df["date"].dt.year == today_dt.year)
    ]
    
    if not df.empty:
        df["day"] = df["date"].dt.day
        
        days = pd.date_range(
            start=f"{today_dt.year}-{today_dt.month:02d}-01",
            end=today_dt
        )
        
        full_df = pd.DataFrame({"date": days})
        full_df["day"] = full_df["date"].dt.day
        
        merged = full_df.merge(df[["day", "status"]], on="day", how="left")
        merged["status"] = merged["status"].fillna(False)
        
        merged["status"] = merged["status"].astype(int)
        
        values = merged["status"].values
        
        pad_size = (7 - len(values) % 7) % 7
        values = np.append(values, [0]*pad_size)
        
        grid = values.reshape(-1, 7)
        
        fig, ax = plt.subplots()
        ax.imshow(grid, aspect="auto")
        
        ax.set_title("Gym Activity (Green = Done)")
        ax.set_xticks([])
        ax.set_yticks([])
        
        st.pyplot(fig)
    else:
        st.write("No gym data for this month yet.")
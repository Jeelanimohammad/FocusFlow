from datetime import datetime

def generate_study_plan(tasks):
    plan = []
    suggestions = []

    today = datetime.now().date()

    for task in tasks:
        subject = task[2]
        deadline = datetime.strptime(task[3], "%Y-%m-%d").date()
        hours = task[4]
        difficulty = task[5]

        days_left = (deadline - today).days

        # ===== PRIORITY LOGIC =====
        if days_left <= 2:
            priority = "High 🔴"
        elif days_left <= 5:
            priority = "Medium 🟡"
        else:
            priority = "Low 🟢"

        # ===== SMART HOUR ADJUSTMENT =====
        required_hours = max(1, int(hours))

        # If deadline is near → increase hours
        if days_left <= 2:
            required_hours += 1
            suggestions.append(f"⚡ Increase study time for {subject} (deadline near)")

        # If user studying too little
        if hours < 2:
            suggestions.append(f"📈 You should spend more time on {subject}")

        # If enough time available
        if days_left > 5 and hours > 4:
            suggestions.append(f"😌 You can reduce load for {subject}")

        # ===== TIME SLOT LOGIC =====
        start_hour = 6  # start from 6 PM
        end_hour = start_hour + required_hours

        time_slot = f"{start_hour}:00 - {end_hour}:00"

        plan.append({
            "subject": subject,
            "priority": priority,
            "daily_hours": required_hours,
            "time_slot": time_slot
        })

    # Remove duplicate suggestions
    suggestions = list(set(suggestions))

    return plan, suggestions

    # Filter only pending tasks
    pending_tasks = [t for t in tasks if t[5] != "Completed"]

    # Sort by deadline (earliest first)
    pending_tasks.sort(key=lambda x: x[3])

    # Start time (you can change this)
    current_time = datetime.strptime("18:00", "%H:%M")

    for task in pending_tasks:
        subject = task[2]
        hours = task[4]

        # Calculate end time
        end_time = current_time + timedelta(hours=hours)

        # Format time
        start_str = current_time.strftime("%I:%M %p")
        end_str = end_time.strftime("%I:%M %p")

        # Add to plan
        plan.append({
            "subject": subject,
            "priority": "High",
            "daily_hours": hours,
            "time_slot": f"{start_str} - {end_str}"
        })

        # Suggestions based on hours
        if hours >= 4:
            suggestions.append(f"{subject}: High workload! Take short breaks.")
        elif hours <= 1:
            suggestions.append(f"{subject}: Try increasing study time.")

        # Add break (15 mins)
        current_time = end_time + timedelta(minutes=15)

    return plan, suggestions
from collections import defaultdict
from datetime import datetime, timedelta

def generate_weekly_plan(tasks, max_hours_per_day=6):
    """
    Smart weekly scheduler:
    - Hard tasks get more priority
    - Avoid overload per day
    """

    # Priority weight
    difficulty_weight = {
        "Hard": 3,
        "Medium": 2,
        "Easy": 1
    }

    # Sort tasks by priority (Hard first)
    tasks_sorted = sorted(
        tasks,
        key=lambda x: difficulty_weight.get(x[5], 1),
        reverse=True
    )

    # Week structure
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = defaultdict(list)
    day_hours = defaultdict(int)

    current_day = 0

    for task in tasks_sorted:
        subject = task[2]
        hours = task[4]
        difficulty = task[5]

        assigned = False

        # try placing in week
        for _ in range(7):
            day = week_days[current_day]

            if day_hours[day] + hours <= max_hours_per_day:
                schedule[day].append({
                    "subject": subject,
                    "hours": hours,
                    "difficulty": difficulty
                })
                day_hours[day] += hours
                assigned = True
                break

            current_day = (current_day + 1) % 7

        # if not fit → force add to last day
        if not assigned:
            schedule["Sunday"].append({
                "subject": subject,
                "hours": hours,
                "difficulty": difficulty
            })

    return schedule
import json
import os
from datetime import datetime, date, timedelta

from input_validation import (
    get_valid_string,
    get_valid_days_of_week,
    get_valid_time,
    get_valid_end_time,
    get_valid_percentage,        # NEW – for grade-weight prompts
)
from display import print_divider, print_section

# ── Persistence ───────────────────────────────────────────────────────────────
SCHEDULE_FILE = "data/schedule.json"

# ── Priority constants ────────────────────────────────────────────────────────
PRIORITY_MAX = 100   # reserved for classes and sleep – never lower

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# In-memory store
_schedule = []


# ── JSON helpers ──────────────────────────────────────────────────────────────

def _time_to_str(t) -> str:
    """Serialise a time object to 'HH:MM' for JSON storage."""
    return t.strftime("%H:%M")


def _str_to_time(s: str):
    """Deserialise a 'HH:MM' string from JSON back to a time object."""
    return datetime.strptime(s, "%H:%M").time()


def save_schedule():
    """Write the current in-memory schedule to data/schedule.json."""
    os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
    payload = []
    for course in _schedule:
        payload.append({
            "course_name":      course["course_name"],
            "days":             course["days"],
            "start_time":       _time_to_str(course["start_time"]),
            "end_time":         _time_to_str(course["end_time"]),
            "priority":         course.get("priority", PRIORITY_MAX),
            # Grade weights – used to compute assignment priorities
            "homework_weight":  course.get("homework_weight", 30.0),
            "quiz_weight":      course.get("quiz_weight",     20.0),
            "exam_weight":      course.get("exam_weight",     50.0),
        })
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  💾 Schedule saved.")


def load_schedule():
    """Load schedule from data/schedule.json into _schedule (called at startup)."""
    global _schedule
    if not os.path.exists(SCHEDULE_FILE):
        return
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
        _schedule = []
        for item in data:
            _schedule.append({
                "course_name":     item["course_name"],
                "days":            item["days"],
                "start_time":      _str_to_time(item["start_time"]),
                "end_time":        _str_to_time(item["end_time"]),
                "priority":        item.get("priority",        PRIORITY_MAX),
                "homework_weight": item.get("homework_weight", 30.0),
                "quiz_weight":     item.get("quiz_weight",     20.0),
                "exam_weight":     item.get("exam_weight",     50.0),
            })
        print(f"  ✔ Loaded {len(_schedule)} course(s) from saved schedule.")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠ Could not load schedule ({e}). Starting fresh.")


# ── CRUD ──────────────────────────────────────────────────────────────────────

def add_class():
    """Prompt the user to enter course info and add it to the schedule."""
    print_section("Enter Class Schedule")

    while True:
        course_name = get_valid_string("Enter course name (or 'done' to finish): ")

        if course_name.lower() == "done":
            print("\n  Class schedule entry complete.")
            print_divider()
            break

        days = get_valid_days_of_week(
            "Enter meeting days (e.g. Mon,Wed,Fri): ",
            DAYS_OF_WEEK
        )
        start_time = get_valid_time("Enter class start time (HH:MM, 24h format): ")
        end_time   = get_valid_end_time(
            "Enter class end time (HH:MM, 24h format): ",
            start_time
        )

        # ── Grade weights (drive assignment-priority calculations) ────────────
        print("\n  Enter grade weights for this course.")
        print("  These percentages adjust assignment priorities automatically.")
        homework_weight = get_valid_percentage("  Homework % of final grade  (e.g. 30): ")
        quiz_weight     = get_valid_percentage("  Quiz     % of final grade  (e.g. 20): ")
        exam_weight     = get_valid_percentage("  Exam/Test% of final grade  (e.g. 50): ")

        course = {
            "course_name":     course_name,
            "days":            days,
            "start_time":      start_time,
            "end_time":        end_time,
            "priority":        PRIORITY_MAX,   # classes are always max priority
            "homework_weight": homework_weight,
            "quiz_weight":     quiz_weight,
            "exam_weight":     exam_weight,
        }

        _schedule.append(course)
        save_schedule()
        print(f"\n  ✔ Course '{course_name}' added (priority {PRIORITY_MAX})!")
        print()


def view_schedule(schedule=None):
    """Display the stored class schedule including weights and priority."""
    if schedule is None:
        schedule = _schedule

    print_section("Current Class Schedule")

    if not schedule:
        print("  No classes entered yet.")
        print_divider()
        return

    for course in schedule:
        days_str  = ", ".join(course["days"])
        start_str = course["start_time"].strftime("%I:%M %p")
        end_str   = course["end_time"].strftime("%I:%M %p")
        print(f"  Course    : {course['course_name']}")
        print(f"  Days      : {days_str}")
        print(f"  Time      : {start_str} – {end_str}")
        print(f"  Priority  : {course.get('priority', PRIORITY_MAX)}  (max – cannot be displaced)")
        print(f"  Weights   : HW {course.get('homework_weight', 30):.0f}%  |  "
              f"Quiz {course.get('quiz_weight', 20):.0f}%  |  "
              f"Exam {course.get('exam_weight', 50):.0f}%")
        print()

    print_divider()


def get_schedule():
    """Return the in-memory class schedule list."""
    return _schedule


# ── Time-query helpers ────────────────────────────────────────────────────────

def is_class_time(day_name: str, hour_float: float, schedule: list) -> bool:
    """Return True if any class is running during hour_float on day_name."""
    for course in schedule:
        if day_name in course["days"]:
            start = course["start_time"].hour + course["start_time"].minute / 60
            end   = course["end_time"].hour   + course["end_time"].minute   / 60
            if start <= hour_float < end:
                return True
    return False


def get_first_class_time(day_name: str, schedule: list):
    """
    Return the earliest class start time (as a time object) on the given
    weekday name, or None if no class falls on that day.
    """
    times = [
        c["start_time"]
        for c in schedule
        if day_name in c["days"]
    ]
    return min(times) if times else None


# ── Sleep schedule ────────────────────────────────────────────────────────────

def get_sleep_window(target_date: date, schedule: list):
    """
    Compute an 8-hour sleep window that ends at the first class of the
    *next* day (i.e. the minimum wake-up time needed for tomorrow's class).

    Priority = PRIORITY_MAX (100) — sleep cannot be displaced by study tasks.

    Returns:
        (sleep_start: datetime, wake_up: datetime)  — or None if no class tomorrow.

    Example:
        First class on Tuesday is 09:00 → sleep 01:00 Mon night → 09:00 Tue.
    """
    next_day      = target_date + timedelta(days=1)
    next_day_name = next_day.strftime("%A")
    first_class   = get_first_class_time(next_day_name, schedule)

    if first_class is None:
        return None   # no class tomorrow – no forced bedtime

    wake_up_dt    = datetime.combine(next_day, first_class)
    sleep_start_dt = wake_up_dt - timedelta(hours=8)

    return sleep_start_dt, wake_up_dt

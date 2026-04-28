from datetime import date, datetime, timedelta
from class_schedule import is_class_time, get_sleep_window

# Maximum study hours any single assignment can consume in one day
MAX_HOURS_PER_DAY = 3.0

# Waking study window (24-h clock integers, end is exclusive)
STUDY_START_HOUR = 8
STUDY_END_HOUR   = 22


# Availability helpers

def _sleep_overlap_hours(target_date: date, schedule: list) -> float:

    window = get_sleep_window(target_date, schedule)
    if window is None:
        return 0.0

    sleep_start_dt, wake_up_dt = window

    study_window_start = datetime.combine(target_date, datetime.min.time()).replace(
        hour=STUDY_START_HOUR, minute=0, second=0, microsecond=0
    )
    study_window_end = study_window_start.replace(hour=STUDY_END_HOUR)

    overlap_start = max(sleep_start_dt, study_window_start)
    overlap_end   = min(wake_up_dt,    study_window_end)

    if overlap_end > overlap_start:
        delta = (overlap_end - overlap_start).total_seconds()
        return delta / 3600.0
    return 0.0


def _available_study_hours_on_day(day: date, schedule: list) -> float:
    """
    Free study hours on *day* after subtracting class time and any
    sleep-window overlap with the study window.  Capped at MAX_HOURS_PER_DAY.
    """
    day_name     = day.strftime("%A")
    total_window = STUDY_END_HOUR - STUDY_START_HOUR   # 14 h

    class_hours = sum(
        1
        for h in range(STUDY_START_HOUR, STUDY_END_HOUR)
        if is_class_time(day_name, h, schedule)
    )

    sleep_hours = _sleep_overlap_hours(day, schedule)
    free_hours  = total_window - class_hours - sleep_hours
    return min(max(free_hours, 0.0), MAX_HOURS_PER_DAY)


# Sleep-block builder

def _build_sleep_session(target_date: date, schedule: list):
    """
    Return a sleep-session dict for *target_date* (tonight's sleep that
    ends at the next day's first class), or None if there is no class tomorrow.

    This session carries priority=100 and is injected into the plan display.
    """
    window = get_sleep_window(target_date, schedule)
    if window is None:
        return None

    sleep_start_dt, wake_up_dt = window
    label = (f"{sleep_start_dt.strftime('%I:%M %p')} "
             f"– {wake_up_dt.strftime('%I:%M %p')}")
    return {
        "name":     f"Sleep  ({label})",
        "type":     "Sleep",
        "hours":    8.0,
        "priority": 100,          # max – never displaced
    }


# Core planner

def generate_study_plan(assignments: list, schedule: list) -> dict:
    """
    Build a day-keyed study plan.

    Sorting rules:
    1. Higher priority assignment → scheduled first within each day.
    2. Among equal-priority assignments, earlier due date comes first.

    Each day in the plan also receives a sleep-block entry when there is a
    class the following day (priority 100, shown at the top of the day).
    """
    today = date.today()
    plan  = {}   # date → [session, ...]

    # Sort assignments: priority DESC, due date ASC
    sorted_assignments = sorted(
        assignments,
        key=lambda a: (-a.get("priority", 30), a["due_date"])
    )

    for assignment in sorted_assignments:
        remaining_hours = assignment["hours"]
        due             = assignment["due_date"].date()

        # Collect days with free time between today and the deadline
        available_days = []
        cursor = today
        while cursor < due:
            free = _available_study_hours_on_day(cursor, schedule)
            if free > 0:
                available_days.append((cursor, free))
            cursor += timedelta(days=1)

        if not available_days:
            # No room before deadline – warn and pin to due date
            plan.setdefault(due, []).append({
                "name":     assignment["name"],
                "type":     assignment["type"],
                "hours":    remaining_hours,
                "priority": assignment.get("priority", 30),
                "warning":  "No free days found before deadline!",
            })
            continue

        # Spread hours evenly; respect per-day cap and remaining budget
        hours_per_day = remaining_hours / len(available_days)

        for day, free_hours in available_days:
            if remaining_hours <= 0:
                break

            session_hours = min(hours_per_day, free_hours, remaining_hours)
            session_hours = round(session_hours, 2)

            plan.setdefault(day, []).append({
                "name":     assignment["name"],
                "type":     assignment["type"],
                "hours":    session_hours,
                "priority": assignment.get("priority", 30),
            })

            remaining_hours = round(remaining_hours - session_hours, 2)

    # Inject sleep blocks into each plan day
    for day in list(plan.keys()):
        sleep_session = _build_sleep_session(day, schedule)
        if sleep_session:
            plan[day].append(sleep_session)

    # Sort sessions within each day: priority DESC
    for day in plan:
        plan[day].sort(key=lambda s: -s.get("priority", 0))

    return dict(sorted(plan.items()))

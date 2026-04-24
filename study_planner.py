from datetime import date, datetime, timedelta
from class_schedule import is_class_time

# Maximum study hours per assignment per day
MAX_HOURS_PER_DAY = 3.0

# Daily window we assume is available for studying (8 AM – 10 PM)
STUDY_START_HOUR = 8
STUDY_END_HOUR = 22


def _available_study_hours_on_day(day: date, schedule: list) -> float:

    day_name = day.strftime("%A")        # e.g. "Monday"
    total_window = STUDY_END_HOUR - STUDY_START_HOUR  # 14 hours

    # Count how many whole hours inside the window are occupied by class
    class_hours = sum(
        1
        for h in range(STUDY_START_HOUR, STUDY_END_HOUR)
        if is_class_time(day_name, h, schedule)
    )

    free_hours = total_window - class_hours
    return min(free_hours, MAX_HOURS_PER_DAY)


def generate_study_plan(assignments: list, schedule: list) -> dict:

    today = date.today()
    plan = {}  # date → [session, ...]

    # Sort by due date (earliest deadline = highest priority)
    sorted_assignments = sorted(assignments, key=lambda a: a["due_date"])

    for assignment in sorted_assignments:
        remaining_hours = assignment["hours"]
        due = assignment["due_date"].date()

        # Build list of available days from today up to (but not including) due date
        available_days = []
        cursor = today
        while cursor < due:
            free = _available_study_hours_on_day(cursor, schedule)
            if free > 0:
                available_days.append((cursor, free))
            cursor += timedelta(days=1)

        if not available_days:
            # No free days before deadline — schedule on due date as a warning
            plan.setdefault(due, []).append({
                "name": assignment["name"],
                "type": assignment["type"],
                "hours": remaining_hours,
                "warning": "No free days found before deadline!"
            })
            continue

        # Distribute hours evenly across available days, respecting per-day cap
        hours_per_day = remaining_hours / len(available_days)

        for day, free_hours in available_days:
            if remaining_hours <= 0:
                break

            # Don't exceed available free time or the per-day cap
            session_hours = min(hours_per_day, free_hours, remaining_hours)
            session_hours = round(session_hours, 2)

            plan.setdefault(day, []).append({
                "name": assignment["name"],
                "type": assignment["type"],
                "hours": session_hours
            })

            remaining_hours -= session_hours
            remaining_hours = round(remaining_hours, 2)

    # Sort the plan by date for display
    return dict(sorted(plan.items()))

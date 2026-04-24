
from input_validation import (
    get_valid_string,
    get_valid_days_of_week,
    get_valid_time,
    get_valid_end_time
)
from display import print_divider, print_section

# In-memory storage for the class schedule during the session
_schedule = []

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


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
        end_time = get_valid_end_time(
            "Enter class end time (HH:MM, 24h format): ",
            start_time
        )

        course = {
            "course_name": course_name,
            "days": days,
            "start_time": start_time,
            "end_time": end_time
        }

        _schedule.append(course)
        print(f"\n  ✔ Course '{course_name}' successfully added!")
        print()


def view_schedule(schedule=None):
    """Display the stored class schedule."""
    if schedule is None:
        schedule = _schedule

    print_section("Current Class Schedule")

    if not schedule:
        print("  No classes entered yet.")
        print_divider()
        return

    for course in schedule:
        days_str = ", ".join(course["days"])
        start_str = course["start_time"].strftime("%I:%M %p")
        end_str = course["end_time"].strftime("%I:%M %p")
        print(f"  Course : {course['course_name']}")
        print(f"  Days   : {days_str}")
        print(f"  Time   : {start_str} – {end_str}")
        print()

    print_divider()


def get_schedule():
    """Return the in-memory class schedule list."""
    return _schedule


def is_class_time(day_name, hour_float, schedule):

    from datetime import datetime

    for course in schedule:
        if day_name in course["days"]:
            start = course["start_time"].hour + course["start_time"].minute / 60
            end = course["end_time"].hour + course["end_time"].minute / 60
            if start <= hour_float < end:
                return True

    return False

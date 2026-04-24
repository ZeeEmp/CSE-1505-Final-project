from datetime import datetime, date, time

def get_valid_string(prompt):
    """Return a non-empty string from the user."""
    while True:
        value = input(f"  {prompt}").strip()
        if value:
            return value
        print("  ⚠ Input cannot be empty. Please try again.")


def get_valid_positive_float(prompt):
    """Return a positive float value from the user."""
    while True:
        raw = input(f"  {prompt}").strip()
        try:
            value = float(raw)
            if value > 0:
                return value
            print("  ⚠ Value must be greater than 0.")
        except ValueError:
            print("  ⚠ Please enter a valid number (e.g. 2.5).")


# Assignment-specific validators


def get_valid_assignment_type(prompt, types):

    print(f"\n  {prompt}:")
    for i, t in enumerate(types, start=1):
        print(f"    {i}. {t}")

    while True:
        raw = input("  Enter number: ").strip()
        try:
            index = int(raw) - 1
            if 0 <= index < len(types):
                return types[index]
            print(f"  ⚠ Please enter a number between 1 and {len(types)}.")
        except ValueError:
            print("  ⚠ Please enter a valid number.")


def get_valid_due_date(prompt):

    while True:
        raw = input(f"  {prompt}").strip()
        try:
            due = datetime.strptime(raw, "%m/%d/%Y")
            if due.date() < date.today():
                print("  ⚠ Due date cannot be in the past.")
            else:
                return due
        except ValueError:
            print("  ⚠ Invalid date format. Please use MM/DD/YYYY.")


def get_valid_study_hours(prompt):

    return get_valid_positive_float(prompt)

# Schedule-specific validators

DAY_ABBREVIATIONS = {
    "mon": "Monday",
    "tue": "Tuesday",
    "wed": "Wednesday",
    "thu": "Thursday",
    "fri": "Friday",
    "sat": "Saturday",
    "sun": "Sunday",
    # Also allow full names
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}


def get_valid_days_of_week(prompt, all_days):

    print(f"  Available days: Mon, Tue, Wed, Thu, Fri, Sat, Sun")
    while True:
        raw = input(f"  {prompt}").strip()
        parts = [p.strip().lower() for p in raw.split(",") if p.strip()]

        if not parts:
            print("  ⚠ Please enter at least one day.")
            continue

        resolved = []
        valid = True
        for part in parts:
            full = DAY_ABBREVIATIONS.get(part)
            if full is None:
                print(f"  ⚠ Unrecognised day: '{part}'. Use Mon/Tue/Wed/Thu/Fri/Sat/Sun.")
                valid = False
                break
            if full not in resolved:
                resolved.append(full)

        if valid:
            return resolved


def get_valid_time(prompt):

    while True:
        raw = input(f"  {prompt}").strip()
        try:
            t = datetime.strptime(raw, "%H:%M").time()
            return t
        except ValueError:
            print("  ⚠ Invalid time format. Please use HH:MM (e.g. 09:30 or 14:00).")


def get_valid_end_time(prompt, start_time):

    while True:
        end = get_valid_time(prompt)
        if end > start_time:
            return end
        print(
            f"  ⚠ End time must be later than start time "
            f"({start_time.strftime('%H:%M')}). Please try again."
        )

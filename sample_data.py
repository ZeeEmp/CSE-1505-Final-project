"""
sample_data.py
──────────────
Generates realistic demo JSON files so users can explore all major features
of the Study Session Planner without entering data manually.

Exported API
  generate_sample_data() → bool   write data/schedule.json & data/assignments.json
  delete_sample_data()   → bool   remove both files (+ data/ dir if empty)
  SAMPLE_MARKER                   string written into every sample file so the
                                  app can detect whether live data is present
"""

import json
import os
import shutil
from datetime import date, timedelta

# ── Paths (match the constants in class_schedule.py / assignment.py)
DATA_DIR       = "data"
SCHEDULE_FILE  = os.path.join(DATA_DIR, "schedule.json")
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")

# Sentinel written into sample files so we can detect & warn if real data exists
SAMPLE_MARKER = "__SAMPLE_DATA__"

# ── Anchor dates relative to today so the plan always looks reasonable
_TODAY = date.today()
_D = lambda n: (_TODAY + timedelta(days=n)).strftime("%m/%d/%Y")


# ══════════════════════════════════════════════════════════════════
#  Sample payload definitions
# ══════════════════════════════════════════════════════════════════

SAMPLE_SCHEDULE = [
    # ── STEM-heavy semester, four courses ──────────────────────────
    {
        "course_name":     "Calculus II",
        "days":            ["Monday", "Wednesday", "Friday"],
        "start_time":      "09:00",
        "end_time":        "10:00",
        "priority":        100,
        "homework_weight": 30.0,
        "quiz_weight":     20.0,
        "exam_weight":     50.0,
    },
    {
        "course_name":     "Computer Science 101",
        "days":            ["Tuesday", "Thursday"],
        "start_time":      "11:00",
        "end_time":        "12:30",
        "priority":        100,
        "homework_weight": 40.0,
        "quiz_weight":     10.0,
        "exam_weight":     50.0,
    },
    {
        "course_name":     "English Composition",
        "days":            ["Monday", "Wednesday", "Friday"],
        "start_time":      "14:00",
        "end_time":        "15:00",
        "priority":        100,
        "homework_weight": 35.0,
        "quiz_weight":     15.0,
        "exam_weight":     50.0,
    },
    {
        "course_name":     "Biology 201",
        "days":            ["Tuesday", "Thursday"],
        "start_time":      "09:30",
        "end_time":        "11:00",
        "priority":        100,
        "homework_weight": 25.0,
        "quiz_weight":     25.0,
        "exam_weight":     50.0,
    },
]

SAMPLE_ASSIGNMENTS = [
    # ── Spread across near / mid / far deadlines ───────────────────
    {
        "name":     "Calculus Quiz 3",
        "type":     "Quiz",
        "due_date": _D(3),           # very soon → high urgency demo
        "hours":    1.5,
        "priority": 20,
        "course":   "Calculus II",
    },
    {
        "name":     "English Essay Draft",
        "type":     "Homework",
        "due_date": _D(8),
        "hours":    3.0,
        "priority": 35,
        "course":   "English Composition",
    },
    {
        "name":     "CS Lab Assignment",
        "type":     "Lab",
        "due_date": _D(10),
        "hours":    2.0,
        "priority": 40,
        "course":   "Computer Science 101",
    },
    {
        "name":     "Biology Lab Report",
        "type":     "Lab",
        "due_date": _D(9),
        "hours":    2.5,
        "priority": 25,
        "course":   "Biology 201",
    },
    {
        "name":     "Calculus Homework 5",
        "type":     "Homework",
        "due_date": _D(6),
        "hours":    2.5,
        "priority": 30,
        "course":   "Calculus II",
    },
    {
        "name":     "CS Programming Project",
        "type":     "Project",
        "due_date": _D(13),
        "hours":    8.0,
        "priority": 40,
        "course":   "Computer Science 101",
    },
    {
        "name":     "Biology Midterm Exam",
        "type":     "Exam",
        "due_date": _D(16),          # far deadline → spread-hours demo
        "hours":    6.0,
        "priority": 50,
        "course":   "Biology 201",
    },
    {
        "name":     "English Final Paper",
        "type":     "Project",
        "due_date": _D(21),
        "hours":    10.0,
        "priority": 40,
        "course":   "English Composition",
    },
]


# ══════════════════════════════════════════════════════════════════
#  Public helpers
# ══════════════════════════════════════════════════════════════════

def _file_is_sample(path: str) -> bool:
    """Return True if *path* exists and contains the sample marker."""
    if not os.path.exists(path):
        return True          # missing file → safe to overwrite
    try:
        with open(path) as f:
            raw = f.read()
        return SAMPLE_MARKER in raw
    except OSError:
        return False


def generate_sample_data() -> bool:
    """
    Write sample schedule + assignments to the data/ directory.

    Returns True on success, False if real (non-sample) data was detected
    and the user chose not to overwrite.
    """
    # ── Safety check: don't silently clobber real data ─────────────
    real_data_files = []
    for path in (SCHEDULE_FILE, ASSIGNMENTS_FILE):
        if os.path.exists(path) and not _file_is_sample(path):
            real_data_files.append(path)

    if real_data_files:
        print("\n  ⚠  The following file(s) contain YOUR data (not sample data):")
        for p in real_data_files:
            print(f"       {p}")
        confirm = input("\n  Overwrite with sample data? (yes / no): ").strip().lower()
        if confirm != "yes":
            print("  ✗ Sample generation cancelled – your data is untouched.")
            return False

    # ── Write schedule ──────────────────────────────────────────────
    os.makedirs(DATA_DIR, exist_ok=True)

    schedule_payload = list(SAMPLE_SCHEDULE)   # already JSON-safe strings
    schedule_payload.append({"__meta__": SAMPLE_MARKER})

    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule_payload, f, indent=2)

    # ── Write assignments ───────────────────────────────────────────
    # Rebuild dates relative to today each time generate is called
    fresh_assignments = []
    for a in SAMPLE_ASSIGNMENTS:
        fresh_assignments.append(dict(a))   # copy so we never mutate the template

    fresh_assignments.append({"__meta__": SAMPLE_MARKER})

    with open(ASSIGNMENTS_FILE, "w") as f:
        json.dump(fresh_assignments, f, indent=2)

    return True


def delete_sample_data() -> bool:
    """
    Remove the sample JSON files.  Refuses to delete real (non-sample) data.

    Returns True if files were removed, False if nothing needed deleting or
    the files contained real data.
    """
    removed = []
    protected = []

    for path in (SCHEDULE_FILE, ASSIGNMENTS_FILE):
        if not os.path.exists(path):
            continue
        if _file_is_sample(path):
            os.remove(path)
            removed.append(path)
        else:
            protected.append(path)

    if protected:
        print("\n  ⚠  The following file(s) contain real data and were NOT deleted:")
        for p in protected:
            print(f"       {p}")

    # Remove data/ directory only if it is now empty
    if os.path.isdir(DATA_DIR) and not os.listdir(DATA_DIR):
        shutil.rmtree(DATA_DIR, ignore_errors=True)

    return bool(removed)

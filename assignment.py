import json
import os
from datetime import datetime

from input_validation import (
    get_valid_string,
    get_valid_assignment_type,
    get_valid_due_date,
    get_valid_study_hours,
)
from display import print_divider, print_section

# ── Persistence ───────────────────────────────────────────────────────────────
ASSIGNMENTS_FILE = "data/assignments.json"

# In-memory store
_assignments = []

ASSIGNMENT_TYPES = ["Homework", "Quiz", "Project", "Exam", "Lab", "Other"]

# ── Base priorities (0-99; 100 is reserved for classes & sleep) ──────────────
# These are the defaults when no course-grade-weight is available.
# The user may override any value at add-time.
BASE_PRIORITIES = {
    "Homework": 30,
    "Quiz":     20,
    "Project":  40,
    "Exam":     50,
    "Lab":      25,
    "Other":    20,
}

# Map assignment type → the course weight key that drives its priority
_WEIGHT_KEY = {
    "Homework": "homework_weight",
    "Quiz":     "quiz_weight",
    "Exam":     "exam_weight",
}


# ── Priority helpers ──────────────────────────────────────────────────────────

def compute_priority(a_type: str, course_weight: float = None) -> int:
    """
    Compute the scheduling priority for an assignment.

    Rules:
    • If a course_weight (e.g. 40.0 meaning 40% of grade) is supplied,
      that value becomes the priority directly.
    • Otherwise the BASE_PRIORITIES table is used.
    • Result is clamped to [1, 99]  (100 is reserved for classes/sleep).
    """
    raw = course_weight if course_weight is not None else BASE_PRIORITIES.get(a_type, 20)
    return max(1, min(99, int(raw)))


# ── JSON persistence ──────────────────────────────────────────────────────────

def save_assignments():
    """Write the in-memory assignment list to data/assignments.json."""
    os.makedirs(os.path.dirname(ASSIGNMENTS_FILE), exist_ok=True)
    payload = []
    for a in _assignments:
        payload.append({
            "name":     a["name"],
            "type":     a["type"],
            "due_date": a["due_date"].strftime("%m/%d/%Y"),
            "hours":    a["hours"],
            "priority": a.get("priority", BASE_PRIORITIES.get(a["type"], 20)),
            "course":   a.get("course", ""),
        })
    with open(ASSIGNMENTS_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  💾 Assignments saved.")


def load_assignments():
    """Load assignments from data/assignments.json into _assignments (called at startup)."""
    global _assignments
    if not os.path.exists(ASSIGNMENTS_FILE):
        return
    try:
        with open(ASSIGNMENTS_FILE, "r") as f:
            data = json.load(f)
        _assignments = []
        for item in data:
            _assignments.append({
                "name":     item["name"],
                "type":     item["type"],
                "due_date": datetime.strptime(item["due_date"], "%m/%d/%Y"),
                "hours":    item["hours"],
                "priority": item.get("priority", BASE_PRIORITIES.get(item["type"], 20)),
                "course":   item.get("course", ""),
            })
        print(f"  ✔ Loaded {len(_assignments)} assignment(s) from saved data.")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠ Could not load assignments ({e}). Starting fresh.")


# ── CRUD ──────────────────────────────────────────────────────────────────────

def add_assignment(schedule=None):
    """
    Prompt the user to enter a new assignment.

    If a schedule is passed in, the user can optionally link the assignment
    to a course so that the course's grade weights auto-set the priority.
    The computed priority is always shown and can be overridden manually.
    """
    print_section("Add New Assignment")

    name    = get_valid_string("Enter assignment name: ")
    a_type  = get_valid_assignment_type("Select assignment type", ASSIGNMENT_TYPES)
    due_date = get_valid_due_date("Enter due date (MM/DD/YYYY): ")
    hours   = get_valid_study_hours("Enter estimated study hours needed (e.g. 2.5): ")

    # ── Determine priority ────────────────────────────────────────────────────
    base_p       = BASE_PRIORITIES.get(a_type, 20)
    course_name  = ""
    course_weight = None

    if schedule:
        print(f"\n  Link to a course? (grade weights will auto-adjust priority)")
        for i, c in enumerate(schedule, start=1):
            hw  = c.get("homework_weight", 30)
            qz  = c.get("quiz_weight",     20)
            ex  = c.get("exam_weight",     50)
            print(f"    {i}. {c['course_name']}  "
                  f"[HW {hw:.0f}% | Quiz {qz:.0f}% | Exam {ex:.0f}%]")
        print(f"    0. Skip (use base priority {base_p})")

        raw = input("  Enter number: ").strip()
        try:
            idx = int(raw)
            if 1 <= idx <= len(schedule):
                chosen      = schedule[idx - 1]
                course_name = chosen["course_name"]
                weight_key  = _WEIGHT_KEY.get(a_type)
                if weight_key:
                    course_weight = chosen.get(weight_key, base_p)
                    print(f"  → '{course_name}' {a_type} weight = {course_weight:.0f}%  "
                          f"→ priority set to {int(course_weight)}")
                else:
                    print(f"  → Linked to '{course_name}' (no weight key for {a_type}; "
                          f"using base {base_p})")
        except ValueError:
            pass

    computed_p = compute_priority(a_type, course_weight)

    print(f"\n  Computed priority : {computed_p}  "
          f"(base for {a_type}: {base_p} | 100 = max, reserved for classes/sleep)")
    override = input("  Override? Enter 1-99 or press Enter to keep: ").strip()
    if override.isdigit():
        val = int(override)
        if 1 <= val <= 99:
            computed_p = val
            print(f"  → Priority overridden to {computed_p}.")

    assignment = {
        "name":     name,
        "type":     a_type,
        "due_date": due_date,
        "hours":    hours,
        "priority": computed_p,
        "course":   course_name,
    }

    _assignments.append(assignment)
    save_assignments()

    print(f"\n  ✔ Assignment '{name}' added  (priority {computed_p})!")
    print_divider()


def view_assignments(assignments):
    """Display all stored assignments in a formatted table."""
    print_section("Current Assignments")

    header = (f"  {'#':<4} {'Name':<22} {'Type':<10} "
              f"{'Due Date':<12} {'Hrs':<6} {'Pri':<5} {'Course'}")
    print(header)
    print("  " + "─" * 70)

    for i, a in enumerate(assignments, start=1):
        due_str = a["due_date"].strftime("%m/%d/%Y")
        print(
            f"  {i:<4} {a['name']:<22} {a['type']:<10} "
            f"{due_str:<12} {a['hours']:<6.1f} "
            f"{a.get('priority', '?'):<5} {a.get('course', '—')}"
        )

    print_divider()


def get_assignments():
    """Return the in-memory list of all assignments."""
    return _assignments

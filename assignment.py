from datetime import datetime
from input_validation import (
    get_valid_string,
    get_valid_assignment_type,
    get_valid_due_date,
    get_valid_study_hours
)
from display import print_divider, print_section

# In-memory storage for assignments during the session
_assignments = []

ASSIGNMENT_TYPES = ["Homework", "Quiz", "Project", "Exam", "Lab", "Other"]


def add_assignment():
    """Prompt the user to enter a new assignment and store it."""
    print_section("Add New Assignment")

    name = get_valid_string("Enter assignment name: ")
    a_type = get_valid_assignment_type(
        "Select assignment type",
        ASSIGNMENT_TYPES
    )
    due_date = get_valid_due_date("Enter due date (MM/DD/YYYY): ")
    hours = get_valid_study_hours(
        "Enter estimated study hours needed (e.g. 2.5): "
    )

    assignment = {
        "name": name,
        "type": a_type,
        "due_date": due_date,
        "hours": hours
    }

    _assignments.append(assignment)

    print(f"\n  ✔ Assignment '{name}' successfully added!")
    print_divider()


def view_assignments(assignments):
    """Display all stored assignments in a formatted table."""
    print_section("Current Assignments")

    header = f"  {'#':<4} {'Name':<25} {'Type':<12} {'Due Date':<14} {'Est. Hours'}"
    print(header)
    print("  " + "-" * 65)

    for i, a in enumerate(assignments, start=1):
        due_str = a["due_date"].strftime("%m/%d/%Y")
        print(
            f"  {i:<4} {a['name']:<25} {a['type']:<12} "
            f"{due_str:<14} {a['hours']:.1f} hrs"
        )

    print_divider()


def get_assignments():
    """Return the in-memory list of all assignments."""
    return _assignments

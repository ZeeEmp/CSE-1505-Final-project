from assignment     import add_assignment, view_assignments, get_assignments, load_assignments
from class_schedule import add_class, view_schedule, get_schedule, load_schedule
from study_planner  import generate_study_plan
from display        import print_header, print_menu, print_divider, print_study_plan

try:
    from sample_data import (
        generate_sample_data, delete_sample_data,
        SAMPLE_MARKER, DATA_DIR,
    )
    _SAMPLE_AVAILABLE = True
except ImportError:
    _SAMPLE_AVAILABLE = False

import os


# ── Sample-detection helper ───────────────────────────────────────────────────

def _any_sample_file_present() -> bool:
    if not _SAMPLE_AVAILABLE:
        return False
    for fname in ("schedule.json", "assignments.json"):
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            try:
                with open(path) as f:
                    if SAMPLE_MARKER in f.read():
                        return True
            except OSError:
                pass
    return False


# ── Sample actions ────────────────────────────────────────────────────────────

def _handle_generate_sample():
    print("\n  Generating sample data ...")
    print("  " + "-" * 61)
    print("  This will populate your planner with:")
    print("    4 sample courses  (Calculus II, CS 101, English Comp, Biology 201)")
    print("    8 sample assignments spread over the next ~3 weeks")
    print("    Priorities, grade weights, and study-hours pre-filled")
    print()

    success = generate_sample_data()

    if success:
        load_schedule()
        load_assignments()
        print()
        print("  Sample data loaded!  Here is what was created:")
        print_divider()
        view_schedule(get_schedule())
        view_assignments(get_assignments())
        print("  Tip: choose 'Generate study plan' to see it all in action.")
        print("  Tip: choose 'Delete sample data' when you are ready to start fresh.")
        print_divider()
    else:
        print_divider()


def _handle_delete_sample():
    if not _any_sample_file_present():
        print("\n  No sample data found - nothing to delete.")
        print_divider()
        return

    print("\n  This will permanently remove all sample data files.")
    confirm = input("  Are you sure? (yes / no): ").strip().lower()
    if confirm != "yes":
        print("  Cancelled - sample data kept.")
        print_divider()
        return

    removed = delete_sample_data()
    if removed:
        load_schedule()
        load_assignments()
        print("\n  Sample data deleted.  Your planner is now empty and ready.")
    else:
        print("\n  Nothing was deleted.")
    print_divider()


# ── Reusable action functions ─────────────────────────────────────────────────

def _action_view_assignments():
    assignments = get_assignments()
    if not assignments:
        print("\n  No assignments added yet.")
        print_divider()
    else:
        view_assignments(assignments)


def _action_generate_plan():
    assignments = get_assignments()
    schedule    = get_schedule()
    if not assignments:
        print("\n  No assignments to plan. Please add assignments first.")
        print_divider()
    else:
        plan = generate_study_plan(assignments, schedule)
        print_study_plan(plan)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print_header("Study Session Planner")

    load_schedule()
    load_assignments()
    print_divider()

    while True:
        sample_present = _any_sample_file_present()

        # Build menu options and a parallel actions list
        options = [
            "Add a new assignment",
            "Enter / update class schedule",
            "View assignment list",
            "View class schedule",
            "Generate study plan",
        ]
        action_fns = [
            lambda: add_assignment(schedule=get_schedule()),
            add_class,
            _action_view_assignments,
            view_schedule,
            _action_generate_plan,
        ]

        if _SAMPLE_AVAILABLE:
            gen_label = "Re-generate sample data" if sample_present else "Generate sample data"
            options.append(gen_label)
            action_fns.append(_handle_generate_sample)

            if sample_present:
                options.append("Delete sample data")
                action_fns.append(_handle_delete_sample)

        options.append("Exit")
        action_fns.append(None)   # sentinel for exit

        print_menu(options)

        n = len(options)
        choice = input(f"  Enter your choice (1-{n}): ").strip()

        if not choice.isdigit() or not (1 <= int(choice) <= n):
            print(f"\n  Invalid choice. Please enter a number between 1 and {n}.")
            continue

        idx    = int(choice) - 1
        action = action_fns[idx]

        if action is None:          # Exit
            print_divider()
            print("  Goodbye! Good luck with your studies!")
            print_divider()
            break

        action()


if __name__ == "__main__":
    main()

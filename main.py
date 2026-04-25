from assignment    import add_assignment, view_assignments, get_assignments, load_assignments
from class_schedule import add_class, view_schedule, get_schedule, load_schedule
from study_planner  import generate_study_plan
from display        import print_header, print_menu, print_divider, print_study_plan


def main():
    print_header("Study Session Planner")

    # ── Load persisted data at startup ────────────────────────────────────────
    # Order matters: schedule must be loaded first so add_assignment can
    # offer the course-linkage menu immediately on first run.
    load_schedule()
    load_assignments()
    print_divider()

    while True:
        print_menu([
            "Add a new assignment",
            "Enter / update class schedule",
            "View assignment list",
            "View class schedule",
            "Generate study plan",
            "Exit",
        ])

        choice = input("  Enter your choice (1-6): ").strip()

        if choice == "1":
            # Pass current schedule so add_assignment can offer course linkage
            add_assignment(schedule=get_schedule())

        elif choice == "2":
            add_class()

        elif choice == "3":
            assignments = get_assignments()
            if not assignments:
                print("\n  No assignments added yet.")
                print_divider()
            else:
                view_assignments(assignments)

        elif choice == "4":
            view_schedule()

        elif choice == "5":
            assignments = get_assignments()
            schedule    = get_schedule()

            if not assignments:
                print("\n  No assignments to plan. Please add assignments first.")
                print_divider()
            else:
                plan = generate_study_plan(assignments, schedule)
                print_study_plan(plan)

        elif choice == "6":
            print_divider()
            print("  Goodbye! Good luck with your studies!")
            print_divider()
            break

        else:
            print("\n  ⚠ Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()

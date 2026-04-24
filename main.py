from assignment import add_assignment, view_assignments, get_assignments
from class_schedule import add_class, view_schedule, get_schedule
from study_planner import generate_study_plan
from display import print_header, print_menu, print_divider


def main():
    print_header("Study Session Planner")

    while True:
        print_menu([
            "Add a new assignment",
            "Enter class schedule information",
            "View current assignment list",
            "Generate study plan",
            "Exit"
        ])

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_assignment()

        elif choice == "2":
            add_class()

        elif choice == "3":
            assignments = get_assignments()
            if not assignments:
                print("\n  No assignments added yet.")
            else:
                view_assignments(assignments)

        elif choice == "4":
            assignments = get_assignments()
            schedule = get_schedule()

            if not assignments:
                print("\n  No assignments to plan. Please add assignments first.")
            else:
                plan = generate_study_plan(assignments, schedule)
                from display import print_study_plan
                print_study_plan(plan)

        elif choice == "5":
            print_divider()
            print("  Goodbye! Good luck with your studies!")
            print_divider()
            break

        else:
            print("\n  Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()

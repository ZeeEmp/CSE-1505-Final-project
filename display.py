WIDTH = 65  # Console width for dividers and headers


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def print_divider():
    """Print a full-width horizontal rule."""
    print("\n" + "─" * WIDTH + "\n")


def print_header(title: str):
    """Print a bold application header banner."""
    print("\n" + "═" * WIDTH)
    print(f"  {title.upper().center(WIDTH - 2)}")
    print("═" * WIDTH + "\n")


def print_section(title: str):
    """Print a section sub-heading."""
    print("\n" + "─" * WIDTH)
    print(f"  {title}")
    print("─" * WIDTH)


def print_menu(options: list):
    """
    Print a numbered menu from a list of option strings.

    Parameters:
        options (list[str]): Menu item labels.
    """
    print_section("Main Menu")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    print()

# Study plan display
def print_study_plan(plan: dict):
    print_section("Your Personalised Study Plan")

    if not plan:
        print("  No study sessions could be scheduled.")
        print("  Make sure your assignments have future due dates.")
        print_divider()
        return

    total_sessions = 0
    total_hours = 0.0

    for day, sessions in plan.items():
        day_label = day.strftime("%A, %B %d %Y")
        print(f"\n  📅 {day_label}")
        print("  " + "·" * 50)

        for session in sessions:
            hours_label = f"{session['hours']:.1f} hr{'s' if session['hours'] != 1 else ''}"
            warning = session.get("warning", "")
            warn_tag = f"  ⚠ {warning}" if warning else ""

            print(
                f"     • [{session['type']}] {session['name']}"
                f"  →  {hours_label}{warn_tag}"
            )
            total_sessions += 1
            total_hours += session["hours"]

    print("\n  " + "─" * 50)
    print(f"  Total: {total_sessions} session(s) | {total_hours:.1f} total study hours")
    print_divider()

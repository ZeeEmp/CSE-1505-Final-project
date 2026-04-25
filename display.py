WIDTH = 65  # Console width for dividers and headers


# ── Layout helpers ────────────────────────────────────────────────────────────

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


# ── Priority legend ───────────────────────────────────────────────────────────

def print_priority_legend():
    """
    Print a compact reference table explaining the priority scale.
    Called automatically when the study plan is displayed.
    """
    print("\n  Priority scale  (higher = scheduled first, cannot be displaced)")
    print("  " + "─" * 50)
    rows = [
        ("Sleep / Classes", "100", "System max – always protected"),
        ("Exam / Test",      "50", "High-stakes – bump up if exam is >50% of grade"),
        ("Project",          "40", "Multi-stage work"),
        ("Homework",         "30", "Scales with HW % of final grade"),
        ("Lab",              "25", ""),
        ("Quiz / Other",     "20", "Scales with Quiz % of final grade"),
    ]
    for label, pri, note in rows:
        note_str = f"  ({note})" if note else ""
        print(f"  {label:<20} P={pri:<5}{note_str}")
    print()


# ── Study-plan display ────────────────────────────────────────────────────────

def print_study_plan(plan: dict):
    """
    Render the study plan.

    Each day shows:
    • 💤 Sleep block (priority 100, top of day, shown with time window)
    • Study sessions in priority order, with [P:xx] badge
    • ⚠ warnings for sessions that couldn't be scheduled before deadline
    """
    print_section("Your Personalised Study Plan")
    print_priority_legend()

    if not plan:
        print("  No study sessions could be scheduled.")
        print("  Make sure your assignments have future due dates.")
        print_divider()
        return

    total_sessions = 0
    total_hours    = 0.0

    for day, sessions in plan.items():
        day_label = day.strftime("%A, %B %d %Y")
        print(f"\n  📅 {day_label}")
        print("  " + "·" * 50)

        for session in sessions:
            s_type   = session.get("type", "")
            priority = session.get("priority", "")
            pri_tag  = f" [P:{priority}]" if priority != "" else ""

            # ── Sleep block ───────────────────────────────────────────────────
            if s_type == "Sleep":
                print(f"     💤 {session['name']}{pri_tag}")
                continue

            # ── Study session ─────────────────────────────────────────────────
            hrs         = session["hours"]
            hours_label = f"{hrs:.1f} hr{'s' if hrs != 1 else ''}"
            warning     = session.get("warning", "")
            warn_tag    = f"  ⚠ {warning}" if warning else ""

            print(
                f"     • [{s_type}] {session['name']}"
                f"  →  {hours_label}{pri_tag}{warn_tag}"
            )
            total_sessions += 1
            total_hours    += hrs

    print("\n  " + "─" * 50)
    print(f"  Total: {total_sessions} study session(s) | {total_hours:.1f} total study hours")
    print_divider()

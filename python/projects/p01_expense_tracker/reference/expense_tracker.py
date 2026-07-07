"""
Expense Tracker -- Project 01 reference solution.

A CLI application that lets the user add, list, summarise, and delete
personal expenses.  Data is persisted to a JSON file between sessions.

Covers skills from Chapters 01-06:
  - Basic types, f-strings, type conversion
  - Control flow (if/elif/else, while, for)
  - Data structures (lists, dicts)
  - Functions with default arguments
  - OOP (dataclass + class)
  - Modules (json, datetime), error handling, file I/O

Usage:
    python expense_tracker.py           # interactive CLI
    python expense_tracker.py --test    # run non-interactive self-tests
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import date


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Expense:
    """A single expense entry."""

    id: int
    category: str
    amount: float
    description: str
    date: str  # ISO format YYYY-MM-DD


# ---------------------------------------------------------------------------
# Tracker logic
# ---------------------------------------------------------------------------

class ExpenseTracker:
    """Manages a collection of expenses with persistence."""

    def __init__(self, filepath: str = "expenses.json") -> None:
        self.filepath: str = filepath
        self._expenses: list[Expense] = []
        self._next_id: int = 1

    # -- core operations ----------------------------------------------------

    def add(
        self,
        category: str,
        amount: float,
        description: str,
        expense_date: str | None = None,
    ) -> Expense:
        """Create a new expense and return it.

        If *expense_date* is ``None``, today's date is used automatically.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        expense = Expense(
            id=self._next_id,
            category=category.strip().lower(),
            amount=round(amount, 2),
            description=description.strip(),
            date=expense_date or date.today().isoformat(),
        )
        self._expenses.append(expense)
        self._next_id += 1
        return expense

    def delete(self, expense_id: int) -> bool:
        """Delete an expense by its ID.  Returns ``True`` if found."""
        for i, exp in enumerate(self._expenses):
            if exp.id == expense_id:
                self._expenses.pop(i)
                return True
        return False

    def list_expenses(self, category: str | None = None) -> list[Expense]:
        """Return expenses, optionally filtered by category."""
        if category is None:
            return list(self._expenses)
        cat = category.strip().lower()
        return [e for e in self._expenses if e.category == cat]

    def summary(self) -> dict:
        """Return a summary dict with total, by_category, count, average."""
        total = sum(e.amount for e in self._expenses)
        count = len(self._expenses)
        average = round(total / count, 2) if count else 0.0

        by_category: dict[str, float] = {}
        for exp in self._expenses:
            by_category[exp.category] = round(
                by_category.get(exp.category, 0.0) + exp.amount, 2
            )

        return {
            "total": round(total, 2),
            "by_category": by_category,
            "count": count,
            "average": average,
        }

    # -- persistence --------------------------------------------------------

    def save(self) -> None:
        """Write all expenses to the JSON file."""
        data = {
            "next_id": self._next_id,
            "expenses": [asdict(e) for e in self._expenses],
        }
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Load expenses from the JSON file (if it exists)."""
        if not os.path.exists(self.filepath):
            return

        with open(self.filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        self._expenses = [Expense(**item) for item in data.get("expenses", [])]
        self._next_id = data.get("next_id", 1)

        # Safety: make sure _next_id is higher than any existing ID.
        if self._expenses:
            max_id = max(e.id for e in self._expenses)
            if self._next_id <= max_id:
                self._next_id = max_id + 1


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _read_float(prompt: str) -> float | None:
    """Prompt the user for a float.  Returns ``None`` on bad input."""
    try:
        return float(input(prompt))
    except ValueError:
        return None


def _read_int(prompt: str) -> int | None:
    """Prompt the user for an int.  Returns ``None`` on bad input."""
    try:
        return int(input(prompt))
    except ValueError:
        return None


def _print_expenses(expenses: list[Expense]) -> None:
    """Pretty-print a list of expenses as a table."""
    if not expenses:
        print("No expenses found.")
        return

    header = f"{'ID':<4}| {'Date':<11}| {'Category':<11}| {'Amount':>8} | Description"
    separator = "-" * 4 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 9 + "|" + "-" * 22
    print(header)
    print(separator)
    for exp in expenses:
        print(
            f"{exp.id:<4}| {exp.date:<11}| {exp.category:<11}| "
            f"${exp.amount:>7.2f} | {exp.description}"
        )


# ---------------------------------------------------------------------------
# Main interactive loop
# ---------------------------------------------------------------------------

MENU = """
Expense Tracker
===============
1. Add expense
2. List expenses
3. Summary
4. Delete expense
5. Save & Quit
"""


def main(filepath: str = "expenses.json") -> None:
    """Run the interactive expense-tracker CLI."""
    tracker = ExpenseTracker(filepath)
    tracker.load()

    print(MENU)

    while True:
        choice = input("Choice: ").strip()

        if choice == "1":
            # -- Add expense ------------------------------------------------
            category = input("Category: ").strip()
            if not category:
                print("Category cannot be empty.")
                continue

            amount = _read_float("Amount: ")
            if amount is None or amount <= 0:
                print("Please enter a positive number for the amount.")
                continue

            description = input("Description: ").strip()
            expense = tracker.add(category, amount, description)
            print(f"Added expense #{expense.id}\n")

        elif choice == "2":
            # -- List expenses ----------------------------------------------
            cat_filter = input("Filter by category (blank for all): ").strip()
            expenses = tracker.list_expenses(cat_filter or None)
            _print_expenses(expenses)
            print()

        elif choice == "3":
            # -- Summary ----------------------------------------------------
            s = tracker.summary()
            print(f"Total:    ${s['total']:.2f}")
            print(f"Count:    {s['count']}")
            print(f"Average:  ${s['average']:.2f}")
            print("By category:")
            for cat, amt in sorted(s["by_category"].items()):
                print(f"  {cat + ':':<14} ${amt:.2f}")
            print()

        elif choice == "4":
            # -- Delete expense ---------------------------------------------
            eid = _read_int("Expense ID to delete: ")
            if eid is None:
                print("Invalid ID.")
                continue
            if tracker.delete(eid):
                print(f"Deleted expense #{eid}\n")
            else:
                print(f"No expense found with ID {eid}.\n")

        elif choice == "5":
            # -- Save & quit ------------------------------------------------
            tracker.save()
            print("Data saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-5.\n")


# ---------------------------------------------------------------------------
# Self-tests (non-interactive)
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Run basic non-interactive tests to verify core functionality."""
    import tempfile

    print("Running self-tests ...")

    # Use a temporary file so tests never interfere with real data.
    fd, tmpfile = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    try:
        tracker = ExpenseTracker(filepath=tmpfile)

        # --- Test: add expenses -------------------------------------------
        e1 = tracker.add("food", 25.50, "lunch")
        e2 = tracker.add("transport", 12.00, "bus pass")
        e3 = tracker.add("food", 9.75, "coffee and snack")

        assert e1.id == 1, f"Expected id 1, got {e1.id}"
        assert e2.id == 2, f"Expected id 2, got {e2.id}"
        assert e3.id == 3, f"Expected id 3, got {e3.id}"
        assert e1.category == "food"
        assert e2.amount == 12.00
        print("  [PASS] add expenses")

        # --- Test: list all -----------------------------------------------
        all_expenses = tracker.list_expenses()
        assert len(all_expenses) == 3, f"Expected 3, got {len(all_expenses)}"
        print("  [PASS] list all expenses")

        # --- Test: list filtered ------------------------------------------
        food = tracker.list_expenses(category="food")
        assert len(food) == 2, f"Expected 2 food expenses, got {len(food)}"
        transport = tracker.list_expenses(category="transport")
        assert len(transport) == 1
        empty = tracker.list_expenses(category="entertainment")
        assert len(empty) == 0
        print("  [PASS] list filtered by category")

        # --- Test: summary ------------------------------------------------
        s = tracker.summary()
        assert s["count"] == 3
        assert s["total"] == 47.25, f"Expected total 47.25, got {s['total']}"
        assert s["average"] == 15.75, f"Expected avg 15.75, got {s['average']}"
        assert s["by_category"]["food"] == 35.25
        assert s["by_category"]["transport"] == 12.00
        print("  [PASS] summary")

        # --- Test: delete -------------------------------------------------
        assert tracker.delete(2) is True
        assert tracker.delete(999) is False
        assert len(tracker.list_expenses()) == 2
        print("  [PASS] delete expense")

        # --- Test: save / load round-trip ---------------------------------
        tracker.save()

        tracker2 = ExpenseTracker(filepath=tmpfile)
        tracker2.load()

        loaded = tracker2.list_expenses()
        assert len(loaded) == 2, f"Expected 2 after load, got {len(loaded)}"
        ids = {e.id for e in loaded}
        assert ids == {1, 3}, f"Expected IDs {{1, 3}}, got {ids}"
        print("  [PASS] save / load round-trip")

        # --- Test: IDs continue after reload ------------------------------
        e4 = tracker2.add("entertainment", 15.00, "movie ticket")
        assert e4.id == 4, f"Expected id 4 after reload, got {e4.id}"
        print("  [PASS] ID auto-increment continues after reload")

        # --- Test: add with invalid amount --------------------------------
        try:
            tracker2.add("food", -5.00, "bad expense")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        print("  [PASS] rejects negative amount")

        # --- Test: empty tracker summary ----------------------------------
        empty_tracker = ExpenseTracker(filepath=tmpfile)
        s_empty = empty_tracker.summary()
        assert s_empty["total"] == 0.0
        assert s_empty["count"] == 0
        assert s_empty["average"] == 0.0
        assert s_empty["by_category"] == {}
        print("  [PASS] empty tracker summary")

    finally:
        # Clean up the temporary file.
        if os.path.exists(tmpfile):
            os.remove(tmpfile)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        run_tests()
        print("\nAll tests passed!")
    else:
        main()

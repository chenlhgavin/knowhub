# Project 01 - Expense Tracker (CLI)

A command-line expense tracker that ties together the fundamentals from
Chapters 01 through 06: basic types, control flow, data structures, functions,
object-oriented programming, and modules / error handling / file I/O.

## Learning Objectives

| Chapter | Skills practiced |
|---------|-----------------|
| 01 - Basics | `int`, `float`, `str` manipulation, f-strings, type conversion |
| 02 - Control Flow | `if/elif/else`, `while` loop for the menu, `for` loops over expenses |
| 03 - Data Structures | Lists of dicts/dataclasses, dictionary aggregation |
| 04 - Functions | Small, focused helper functions with default arguments |
| 05 - OOP | A `dataclass` for the data model, a class for the tracker logic |
| 06 - Modules & Errors | `json` for persistence, `datetime` for dates, `try/except` for input validation |

## Requirements

Build a program that lets the user manage personal expenses from the terminal.

1. **Add an expense** -- each expense has a category, amount, description, and
   date (defaults to today).
2. **List expenses** -- show all expenses, optionally filtered by category.
3. **Show a summary** -- total spending, spending broken down by category,
   number of expenses, and the average expense amount.
4. **Delete an expense** -- remove an expense by its ID.
5. **Save & quit** -- persist all data to a JSON file so it survives between
   sessions. Load the file automatically on startup.

### Constraints

- Use `input()` for the CLI (no `argparse` -- keep it simple).
- Handle invalid input gracefully (bad numbers, missing IDs, etc.).
- Auto-generate a unique, incrementing integer ID for each expense.

## Expected Behavior

Below is a sample interactive session showing the core workflow.

```
Expense Tracker
===============
1. Add expense
2. List expenses
3. Summary
4. Delete expense
5. Save & Quit

Choice: 1
Category: food
Amount: 25.50
Description: lunch
Added expense #1

Choice: 1
Category: transport
Amount: 12.00
Description: bus pass
Added expense #2

Choice: 1
Category: food
Amount: 9.75
Description: coffee and snack
Added expense #3

Choice: 2
ID  | Date       | Category   | Amount  | Description
----|------------|------------|---------|----------------------
1   | 2026-02-11 | food       |  $25.50 | lunch
2   | 2026-02-11 | transport  |  $12.00 | bus pass
3   | 2026-02-11 | food       |   $9.75 | coffee and snack

Filter by category (blank for all): food
ID  | Date       | Category   | Amount  | Description
----|------------|------------|---------|----------------------
1   | 2026-02-11 | food       |  $25.50 | lunch
3   | 2026-02-11 | food       |   $9.75 | coffee and snack

Choice: 3
Total:    $47.25
Count:    3
Average:  $15.75
By category:
  food:       $35.25
  transport:  $12.00

Choice: 4
Expense ID to delete: 2
Deleted expense #2

Choice: 5
Data saved. Goodbye!
```

## Hints

- Use a **`dataclass`** (from the `dataclasses` module) to represent a single
  expense. This gives you a clean data model with named fields.
- Store all expenses in a **list** on your tracker class.
- Use the **`json`** module for saving and loading. Since dataclasses are not
  directly JSON-serializable, convert each expense to a dict for storage and
  recreate the dataclass instances when loading.
- Track a `_next_id` counter in your tracker class so each new expense gets a
  unique ID.  When loading from a file, set `_next_id` to one more than the
  highest existing ID.
- Use **`datetime.date.today().isoformat()`** to generate today's date as a
  `YYYY-MM-DD` string.
- Wrap `float(input(...))` in a `try/except ValueError` to handle non-numeric
  input for amounts.

## Project Structure

```
p01_expense_tracker/
    README.md              # <-- you are here
    reference/
        expense_tracker.py # complete working solution (peek only if stuck!)
```

## Getting Started

1. Create a new file, e.g. `expense_tracker.py`, in this directory.
2. Define the `Expense` dataclass.
3. Build the `ExpenseTracker` class method by method -- start with `add()` and
   `list_expenses()` before moving on to `summary()`, `delete()`, and
   persistence (`save()` / `load()`).
4. Write the `main()` function with a `while True` menu loop.
5. Test as you go!  The reference solution supports a `--test` flag:
   `python expense_tracker.py --test` -- try to do the same for yours.

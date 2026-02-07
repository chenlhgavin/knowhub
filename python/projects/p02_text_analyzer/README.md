# Project 02: Text Analyzer

**Level**: Intermediate
**Skills**: Chapters 01--08 (Basics through Decorators & Generators)

---

## Overview

Build a text analysis tool that reads text from a string or file and produces
detailed statistics, readability scores, pattern searches, and formatted
reports. This project ties together everything from basic Python through
generators and decorators into a single cohesive program.

---

## Requirements

### Core Features

1. **Text Input** -- accept text as a string or read it from a file using a
   classmethod constructor.

2. **Basic Statistics** -- compute:
   - Total word count
   - Total sentence count
   - Total character count (excluding whitespace)
   - Average word length
   - Number of unique words
   - Top N most frequent words (default N = 10)

3. **Readability Score** -- approximate the Flesch-Kincaid grade level:
   ```
   grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
   ```
   You will need a helper function to estimate syllable count per word.

4. **Pattern Search** -- search the text for a regex pattern and return a list
   of `(line_number, matching_line)` tuples.

5. **Concordance** -- given a word, show it in context: the N words before and
   after each occurrence.

6. **Stopword Filtering** -- exclude common English words (the, a, is, ...) from
   frequency counts. Provide sensible defaults but let the caller override.

7. **Formatted Report** -- generate a single string report that combines all
   analysis results in a readable layout.

### Design Constraints

8. **Generators** -- use generator functions for tokenizing words and splitting
   sentences so that processing large files stays memory-efficient.

9. **Decorators** -- write and apply:
   - A `timer` decorator that measures how long each analysis step takes.
   - A `cache_result` decorator that memoizes results so repeated calls are
     instant.

10. **Dataclasses** -- use `@dataclass` for structured return types (`TextStats`
    and `ReadabilityScore`).

---

## Suggested Structure

```
p02_text_analyzer/
    README.md               # this file
    reference/
        text_analyzer.py    # complete working implementation
```

### Classes and Functions

| Name | Kind | Purpose |
|------|------|---------|
| `timer` | decorator | Measure and store execution time on the function |
| `cache_result` | decorator | Cache return value keyed on input hash |
| `TextStats` | dataclass | word_count, sentence_count, char_count, avg_word_length, unique_words, top_words |
| `ReadabilityScore` | dataclass | flesch_kincaid_grade, avg_sentence_length, avg_syllables_per_word |
| `TextAnalyzer` | class | Main analysis engine |
| `count_syllables` | function | Approximate syllable count for an English word |

### `TextAnalyzer` Methods

| Method | Description |
|--------|-------------|
| `__init__(text, stopwords)` | Store text; use default stopwords if None |
| `from_file(filepath)` | Classmethod; read file and return a new analyzer |
| `_tokenize()` | Generator; yield cleaned, lowercased words |
| `_sentences()` | Generator; yield individual sentences |
| `stats()` | Return a `TextStats` dataclass (timed + cached) |
| `readability()` | Return a `ReadabilityScore` dataclass (timed) |
| `search(pattern)` | Regex search; return [(line_num, line), ...] |
| `concordance(word, context=5)` | Show word with N surrounding words |
| `report()` | Return a formatted string combining all analysis |

---

## Hints

- **Generators for tokenization**: split the text lazily so you never hold all
  tokens in memory at once. When you need a concrete list (for frequency
  counting), materialize only once and reuse.

- **Syllable counting**: a simple heuristic works well enough:
  - Count vowel groups (`[aeiouy]+`) in the word.
  - Subtract 1 if the word ends with a silent `e`.
  - Ensure every word has at least 1 syllable.

- **Decorators**: the `timer` decorator can store elapsed time as an attribute
  on the wrapper function. The `cache_result` decorator can hash the instance's
  text to decide whether to return a cached value.

- **Comprehensions and itertools**: look for opportunities to use dict/list/set
  comprehensions and `itertools` functions (e.g., `islice` for concordance
  windows).

- **Regex for sentences**: splitting on `[.!?]+` is a reasonable first
  approximation. Do not worry about abbreviations or edge cases.

- **The report**: use f-strings and `str.join()` to build a cleanly formatted
  multi-line report.

---

## Running

```bash
# Run the demo
python3 python/projects/p02_text_analyzer/reference/text_analyzer.py

# Run the built-in tests
python3 python/projects/p02_text_analyzer/reference/text_analyzer.py --test
```

---

## Concepts Practiced

| Chapter | Concepts Used |
|---------|---------------|
| 01 Basics | Variables, types, f-strings, operators |
| 02 Control Flow | if/elif/else, for loops, while loops |
| 03 Data Structures | list, dict, set, tuple, comprehensions |
| 04 Functions | def, *args/**kwargs, lambda, closures |
| 05 OOP | Classes, classmethods, dataclasses, dunder methods |
| 06 Modules & Errors | File I/O, exceptions, imports |
| 07 Iterators & Generators | yield, generator functions, lazy evaluation |
| 08 Decorators | Function decorators, functools.wraps, stacking decorators |

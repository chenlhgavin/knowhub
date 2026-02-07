"""
Project 02 -- Text Analyzer
============================
A text analysis tool that demonstrates intermediate Python concepts:
generators, decorators, dataclasses, regex, comprehensions, and file I/O.

Usage:
    python text_analyzer.py              # run demo
    python text_analyzer.py --test       # run built-in tests
    python text_analyzer.py FILE         # analyze a text file
"""

import re
import time
import hashlib
from dataclasses import dataclass, field
from collections import Counter
from functools import wraps
from itertools import islice


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def timer(func):
    """Decorator that measures and stores execution time on the wrapper."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        wrapper.last_elapsed = elapsed
        return result
    wrapper.last_elapsed = 0.0
    return wrapper


def cache_result(func):
    """Decorator that caches the return value keyed on the instance's text hash.

    Works with methods whose first positional argument is `self` and whose
    self has a `_text_hash` attribute.  If the hash matches a previous call,
    the cached result is returned immediately.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        key = (func.__name__, self._text_hash)
        if key not in wrapper._cache:
            wrapper._cache[key] = func(self, *args, **kwargs)
        return wrapper._cache[key]
    wrapper._cache = {}
    return wrapper


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def count_syllables(word: str) -> int:
    """Approximate the number of syllables in an English word.

    Heuristic:
      1. Count groups of consecutive vowels (a, e, i, o, u, y).
      2. Subtract 1 if the word ends with a silent 'e'.
      3. Ensure every word has at least 1 syllable.
    """
    word = word.lower().strip()
    if not word:
        return 0
    # Count vowel groups
    count = len(re.findall(r"[aeiouy]+", word))
    # Silent 'e' at the end
    if word.endswith("e") and not word.endswith("le"):
        count -= 1
    return max(count, 1)


# ---------------------------------------------------------------------------
# Dataclasses for structured results
# ---------------------------------------------------------------------------

@dataclass
class TextStats:
    """Basic text statistics."""
    word_count: int
    sentence_count: int
    char_count: int
    avg_word_length: float
    unique_words: int
    top_words: list[tuple[str, int]] = field(default_factory=list)

    def __str__(self) -> str:
        top = ", ".join(f"{w} ({c})" for w, c in self.top_words)
        return (
            f"Words: {self.word_count}  |  Sentences: {self.sentence_count}  "
            f"|  Characters: {self.char_count}\n"
            f"Avg word length: {self.avg_word_length:.2f}  "
            f"|  Unique words: {self.unique_words}\n"
            f"Top words: {top}"
        )


@dataclass
class ReadabilityScore:
    """Flesch-Kincaid readability metrics."""
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_syllables_per_word: float

    def __str__(self) -> str:
        return (
            f"Flesch-Kincaid grade level: {self.flesch_kincaid_grade:.1f}\n"
            f"Avg sentence length: {self.avg_sentence_length:.1f} words\n"
            f"Avg syllables/word: {self.avg_syllables_per_word:.2f}"
        )


# ---------------------------------------------------------------------------
# Default stopwords
# ---------------------------------------------------------------------------

DEFAULT_STOPWORDS: set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "am", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "shall", "should", "may", "might", "must", "can", "could", "it", "its",
    "i", "me", "my", "we", "us", "our", "you", "your", "he", "him", "his",
    "she", "her", "they", "them", "their", "this", "that", "these", "those",
    "not", "no", "nor", "so", "if", "then", "than", "too", "very", "just",
    "about", "above", "after", "again", "all", "also", "as", "because",
    "before", "between", "both", "each", "from", "into", "more", "most",
    "other", "out", "over", "own", "same", "some", "such", "there", "through",
    "under", "up", "what", "when", "where", "which", "while", "who", "whom",
    "why", "how",
}


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class TextAnalyzer:
    """Analyze text for statistics, readability, patterns, and concordance.

    Examples
    --------
    >>> analyzer = TextAnalyzer("Hello world. Hello again.")
    >>> analyzer.stats().word_count
    4
    """

    def __init__(
        self,
        text: str = "",
        stopwords: set[str] | None = None,
    ) -> None:
        self.text = text
        self.stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS
        # Pre-compute a hash so the cache decorator can detect changes.
        # Include the sorted stopwords so different configurations get
        # separate cache entries.
        fingerprint = self.text + "\x00" + ",".join(sorted(self.stopwords))
        self._text_hash = hashlib.md5(fingerprint.encode()).hexdigest()

    # -- Alternate constructor -----------------------------------------------

    @classmethod
    def from_file(cls, filepath: str, **kwargs) -> "TextAnalyzer":
        """Create a TextAnalyzer by reading an entire file."""
        with open(filepath, encoding="utf-8") as fh:
            text = fh.read()
        return cls(text, **kwargs)

    # -- Generators ----------------------------------------------------------

    def _tokenize(self):
        """Yield cleaned, lowercased words one at a time (generator)."""
        for line in self.text.splitlines():
            for word in re.findall(r"[a-zA-Z']+", line):
                yield word.lower()

    def _sentences(self):
        """Yield individual sentences split on sentence-ending punctuation."""
        for sentence in re.split(r"(?<=[.!?])\s+", self.text.strip()):
            sentence = sentence.strip()
            if sentence:
                yield sentence

    # -- Analysis methods ----------------------------------------------------

    @timer
    @cache_result
    def stats(self, top_n: int = 10) -> TextStats:
        """Compute basic text statistics.

        Uses generators for tokenization, then materializes a word list once
        to compute all metrics without re-scanning.
        """
        words = list(self._tokenize())
        sentences = list(self._sentences())

        word_count = len(words)
        sentence_count = len(sentences)
        char_count = sum(1 for ch in self.text if not ch.isspace())

        avg_word_length = (
            sum(len(w) for w in words) / word_count if word_count else 0.0
        )

        # Frequency counts excluding stopwords
        filtered = [w for w in words if w not in self.stopwords]
        freq = Counter(filtered)
        unique_words = len(set(words))
        top_words = freq.most_common(top_n)

        return TextStats(
            word_count=word_count,
            sentence_count=sentence_count,
            char_count=char_count,
            avg_word_length=round(avg_word_length, 2),
            unique_words=unique_words,
            top_words=top_words,
        )

    @timer
    def readability(self) -> ReadabilityScore:
        """Compute a Flesch-Kincaid grade-level approximation.

        Formula:
            grade = 0.39 * (words / sentences)
                  + 11.8 * (syllables / words)
                  - 15.59
        """
        words = list(self._tokenize())
        sentences = list(self._sentences())

        total_words = len(words)
        total_sentences = len(sentences) or 1  # avoid division by zero
        total_syllables = sum(count_syllables(w) for w in words)

        avg_sentence_length = total_words / total_sentences
        avg_syllables = total_syllables / total_words if total_words else 0.0

        grade = (
            0.39 * avg_sentence_length
            + 11.8 * avg_syllables
            - 15.59
        )

        return ReadabilityScore(
            flesch_kincaid_grade=round(grade, 1),
            avg_sentence_length=round(avg_sentence_length, 1),
            avg_syllables_per_word=round(avg_syllables, 2),
        )

    def search(self, pattern: str) -> list[tuple[int, str]]:
        """Search for a regex pattern and return matching lines.

        Returns a list of (line_number, line_text) tuples.  Line numbers are
        1-based.
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        return [
            (i, line)
            for i, line in enumerate(self.text.splitlines(), start=1)
            if compiled.search(line)
        ]

    def concordance(self, word: str, context: int = 5) -> list[str]:
        """Show each occurrence of *word* surrounded by *context* words.

        Returns a list of strings like '... before WORD after ...'.
        """
        words = list(self._tokenize())
        target = word.lower()
        results: list[str] = []

        for idx, w in enumerate(words):
            if w == target:
                start = max(0, idx - context)
                end = min(len(words), idx + context + 1)
                window = words[start:end]
                # Uppercase the target word for visibility
                window[idx - start] = window[idx - start].upper()
                snippet = " ".join(window)
                if start > 0:
                    snippet = "... " + snippet
                if end < len(words):
                    snippet = snippet + " ..."
                results.append(snippet)

        return results

    # -- Report --------------------------------------------------------------

    def report(self) -> str:
        """Generate a formatted analysis report combining all metrics."""
        s = self.stats()
        r = self.readability()

        divider = "=" * 60
        thin = "-" * 60

        sections: list[str] = []

        # Header
        sections.append(divider)
        sections.append("TEXT ANALYSIS REPORT")
        sections.append(divider)

        # Preview
        preview = self.text[:200].replace("\n", " ")
        if len(self.text) > 200:
            preview += " ..."
        sections.append(f"\nText preview:\n  \"{preview}\"\n")

        # Basic statistics
        sections.append(thin)
        sections.append("BASIC STATISTICS")
        sections.append(thin)
        sections.append(f"  Word count:        {s.word_count}")
        sections.append(f"  Sentence count:    {s.sentence_count}")
        sections.append(f"  Character count:   {s.char_count}")
        sections.append(f"  Avg word length:   {s.avg_word_length:.2f}")
        sections.append(f"  Unique words:      {s.unique_words}")
        sections.append("")

        # Top words
        sections.append(thin)
        sections.append("TOP WORDS (excluding stopwords)")
        sections.append(thin)
        for rank, (word, count) in enumerate(s.top_words, start=1):
            bar = "#" * count
            sections.append(f"  {rank:>2}. {word:<20} {count:>4}  {bar}")
        sections.append("")

        # Readability
        sections.append(thin)
        sections.append("READABILITY")
        sections.append(thin)
        sections.append(f"  Flesch-Kincaid grade level:  {r.flesch_kincaid_grade:.1f}")
        sections.append(f"  Avg sentence length:         {r.avg_sentence_length:.1f} words")
        sections.append(f"  Avg syllables per word:      {r.avg_syllables_per_word:.2f}")
        sections.append("")

        # Timing info
        sections.append(thin)
        sections.append("TIMING")
        sections.append(thin)
        stats_time = getattr(self.stats, "last_elapsed", 0.0)
        read_time = getattr(self.readability, "last_elapsed", 0.0)
        sections.append(f"  stats()        {stats_time:.6f} s")
        sections.append(f"  readability()  {read_time:.6f} s")

        sections.append(divider)

        return "\n".join(sections)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Run built-in tests to verify core functionality."""

    sample = (
        "The quick brown fox jumps over the lazy dog. "
        "The dog barked loudly. "
        "Foxes are clever animals that live in many countries around the world."
    )

    analyzer = TextAnalyzer(sample)

    # -- stats ---------------------------------------------------------------
    s = analyzer.stats()

    assert s.word_count == 25, f"Expected 25 words, got {s.word_count}"
    assert s.sentence_count == 3, f"Expected 3 sentences, got {s.sentence_count}"
    assert s.unique_words > 0, "unique_words should be positive"
    assert s.avg_word_length > 0, "avg_word_length should be positive"
    assert len(s.top_words) > 0, "top_words should not be empty"
    assert s.char_count > 0, "char_count should be positive"

    # Verify caching: second call should return the exact same object.
    s2 = analyzer.stats()
    assert s is s2, "stats() should return cached result on second call"

    # -- readability ---------------------------------------------------------
    r = analyzer.readability()

    assert isinstance(r.flesch_kincaid_grade, float), "grade should be float"
    assert r.avg_sentence_length > 0, "avg_sentence_length should be positive"
    assert r.avg_syllables_per_word > 0, "avg_syllables_per_word should be positive"

    # -- search --------------------------------------------------------------
    results = analyzer.search(r"fox")
    assert len(results) >= 1, "Should find at least one line with 'fox'"
    for line_num, line in results:
        assert isinstance(line_num, int)
        assert "fox" in line.lower()

    # -- concordance ---------------------------------------------------------
    conc = analyzer.concordance("dog", context=3)
    assert len(conc) >= 1, "Should find at least one concordance for 'dog'"
    for snippet in conc:
        assert "DOG" in snippet, "Target word should be uppercased in concordance"

    # -- report --------------------------------------------------------------
    report = analyzer.report()
    assert "TEXT ANALYSIS REPORT" in report
    assert "BASIC STATISTICS" in report
    assert "READABILITY" in report

    # -- count_syllables helper ----------------------------------------------
    assert count_syllables("hello") == 2, f"hello -> {count_syllables('hello')}"
    assert count_syllables("world") == 1, f"world -> {count_syllables('world')}"
    assert count_syllables("beautiful") == 3, f"beautiful -> {count_syllables('beautiful')}"
    assert count_syllables("a") == 1, f"a -> {count_syllables('a')}"
    assert count_syllables("the") == 1, f"the -> {count_syllables('the')}"

    # -- empty text ----------------------------------------------------------
    empty = TextAnalyzer("")
    es = empty.stats()
    assert es.word_count == 0
    assert es.sentence_count == 0

    # -- custom stopwords ----------------------------------------------------
    custom = TextAnalyzer(sample, stopwords=set())
    cs = custom.stats()
    # With no stopwords filtered, "the" should appear in top_words
    top_dict = dict(cs.top_words)
    assert "the" in top_dict, "With empty stopwords, 'the' should be in top_words"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    """Run a demonstration with sample text."""

    sample_text = """\
Python is a high-level programming language. It was created by Guido van \
Rossum and first released in 1991. Python's design philosophy emphasizes \
code readability with the use of significant indentation.

Python is dynamically typed and garbage-collected. It supports multiple \
programming paradigms, including structured, object-oriented, and functional \
programming.

The language provides constructs intended to enable clear programs on both a \
small and large scale. Python consistently ranks as one of the most popular \
programming languages in the world."""

    analyzer = TextAnalyzer(sample_text)

    # Print the full report
    print(analyzer.report())

    # Demonstrate search
    print("\n--- Search for 'python' ---")
    for line_num, line in analyzer.search(r"[Pp]ython"):
        print(f"  Line {line_num}: {line.strip()}")

    # Demonstrate concordance
    print("\n--- Concordance for 'programming' (context=4) ---")
    for snippet in analyzer.concordance("programming", context=4):
        print(f"  {snippet}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        run_tests()
        print("All tests passed!")
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Analyze a file passed as argument
        filepath = sys.argv[1]
        analyzer = TextAnalyzer.from_file(filepath)
        print(analyzer.report())
    else:
        demo()

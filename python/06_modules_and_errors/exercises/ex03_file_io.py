"""Exercise 03: File I/O

Practice reading and writing text files using Python's built-in
file operations:
- Writing lines to a file
- Reading lines from a file
- Counting word frequencies
- Appending to existing files
"""


def write_lines(filepath: str, lines: list[str]) -> int:
    """Write a list of strings to a file, one per line.

    Args:
        filepath: Path to the output file.
        lines: List of strings to write (newlines are added automatically).

    Returns:
        The number of lines written.
    """
    raise NotImplementedError("Implement write_lines")


def read_lines(filepath: str) -> list[str]:
    """Read all lines from a file, stripping trailing whitespace.

    Args:
        filepath: Path to the input file.

    Returns:
        A list of stripped lines.
    """
    raise NotImplementedError("Implement read_lines")


def count_words_in_file(filepath: str) -> dict[str, int]:
    """Count word frequencies in a text file.

    Words are lowercased before counting. A "word" is defined by
    str.split() (split on whitespace).

    Args:
        filepath: Path to the input file.

    Returns:
        A dict mapping each lowercase word to its frequency count.
    """
    raise NotImplementedError("Implement count_words_in_file")


def append_to_file(filepath: str, text: str) -> None:
    """Append text to an existing file.

    Args:
        filepath: Path to the file.
        text: The text to append.
    """
    raise NotImplementedError("Implement append_to_file")


if __name__ == "__main__":
    import tempfile
    import os

    # --- write_lines / read_lines round-trip ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        lines = ["Hello, world!", "Python is great.", "File I/O is useful."]
        count = write_lines(tmp_path, lines)
        assert count == 3

        result = read_lines(tmp_path)
        assert result == lines
    finally:
        os.unlink(tmp_path)

    # --- write_lines empty list ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        count = write_lines(tmp_path, [])
        assert count == 0

        result = read_lines(tmp_path)
        assert result == []
    finally:
        os.unlink(tmp_path)

    # --- count_words_in_file ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write("the cat sat on the mat\n")
        tmp.write("The Cat sat on THE mat\n")
        tmp_path = tmp.name

    try:
        freq = count_words_in_file(tmp_path)
        assert freq["the"] == 4
        assert freq["cat"] == 2
        assert freq["sat"] == 2
        assert freq["on"] == 2
        assert freq["mat"] == 2
    finally:
        os.unlink(tmp_path)

    # --- append_to_file ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write("Line 1\n")
        tmp_path = tmp.name

    try:
        append_to_file(tmp_path, "Line 2\n")
        append_to_file(tmp_path, "Line 3\n")

        result = read_lines(tmp_path)
        assert result == ["Line 1", "Line 2", "Line 3"]
    finally:
        os.unlink(tmp_path)

    print("All ex03_file_io tests passed!")

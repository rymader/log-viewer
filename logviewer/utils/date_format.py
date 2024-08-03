"""Utilities for parsing and formatting strptime-style date format strings."""


class DateFormat:
    """Utility class for working with strptime-style date format strings.

    All methods are static — this class is a namespace for related
    format-parsing logic rather than something to be instantiated.
    Used by date entry widgets to derive display behaviour from the
    system locale format string at runtime.
    """

    @staticmethod
    def detect_separator(date_format: str) -> str:
        """Extract the field separator character from a date format string.

        Scans the format string for the first character that is neither
        a letter nor a format specifier prefix (%). Common separators
        are '/', '-', and '.'.

        Args:
            date_format: A strptime-style format string, e.g. '%m/%d/%Y'.

        Returns:
            The separator character, or '-' if none is found.
        """
        for char in date_format:
            if not char.isalpha() and char != '%':
                return char
        return '-'

    @staticmethod
    def detect_field_lengths(date_format: str) -> list[int]:
        """Return the digit length of each field in the order they appear.

        Supports %d, %m, %Y, and %y tokens. The result reflects the
        display order dictated by the format string (e.g. month-first
        for US locales, day-first for European locales).

        Args:
            date_format: A strptime-style format string, e.g. '%d/%m/%Y'.

        Returns:
            A list of digit lengths, one per field. %Y produces 4;
            all other supported tokens produce 2.
            Example: '%m/%d/%Y' → [2, 2, 4]
        """
        tokens = [t for t in ['%d', '%m', '%Y', '%y'] if t in date_format]
        tokens.sort(key=lambda t: date_format.index(t))
        return [4 if t == '%Y' else 2 for t in tokens]

    @staticmethod
    def to_placeholder(date_format: str) -> str:
        """Convert a strptime format string to a human-readable placeholder.

        Replaces format tokens with their uppercase label equivalents
        for use as entry field placeholder text.

        Args:
            date_format: A strptime-style format string, e.g. '%m/%d/%Y'.

        Returns:
            A human-readable placeholder string, e.g. 'MM/DD/YYYY'.
        """
        return (date_format
                .replace('%m', 'MM')
                .replace('%d', 'DD')
                .replace('%Y', 'YYYY')
                .replace('%y', 'YY'))

    @staticmethod
    def format_group(digits: str, field_lengths: list[int], separator: str) -> str:
        """Format a raw digit string into a separated field group.

        Splits the digit string into chunks according to field_lengths
        and joins them with separator. Separators are inserted only
        between fields that have been reached by the current digit
        count, so partial input formats correctly as the user types.

        Args:
            digits: A string of digit characters only, e.g. '04132026'.
            field_lengths: The digit length of each field in order,
                e.g. [2, 2, 4] for MM/DD/YYYY.
            separator: The character to insert between fields, e.g. '/'.

        Returns:
            The formatted string, e.g. '04/13/2026'. Partial input
            such as '041' produces '04/1'.
        """
        result = ''
        pos = 0
        for i, length in enumerate(field_lengths):
            chunk = digits[pos:pos + length]
            result += chunk
            pos += length
            # Only insert separator if more digits follow and this is not the last field
            if pos < len(digits) and i < len(field_lengths) - 1:
                result += separator
        return result

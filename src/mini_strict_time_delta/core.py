"""Strict parsing of human-readable duration strings into datetime.timedelta.

A "strict" parser rejects anything that is not a single, complete duration
expression of the form

    [N unit ]* N unit

where N is a non-negative integer and unit is one of:
    d, day, days
    h, hour, hours
    m, min, minute, minutes
    s, sec, second, seconds
    ms, millis, millisecond, milliseconds
    us, micro, microsecond, microseconds

The parser is strict by design: ambiguous or partial input ("1", "1h2",
"", "   ", "1.5h", "1 h 2", trailing junk) raises StrictTimeDeltaError
rather than guessing.
"""

from datetime import timedelta


class StrictTimeDeltaError(ValueError):
    """Raised when the input string is not a single, complete duration expression."""


# Mapping of every accepted unit token to the number of microseconds it represents.
# Single source of truth: the parser looks here, the README documents these tokens.
_UNIT_TO_MICROSECONDS = {
    # Days
    "d": 86_400_000_000,
    "day": 86_400_000_000,
    "days": 86_400_000_000,
    # Hours
    "h": 3_600_000_000,
    "hour": 3_600_000_000,
    "hours": 3_600_000_000,
    # Minutes
    "m": 60_000_000,
    "min": 60_000_000,
    "minute": 60_000_000,
    "minutes": 60_000_000,
    # Seconds
    "s": 1_000_000,
    "sec": 1_000_000,
    "second": 1_000_000,
    "seconds": 1_000_000,
    # Milliseconds
    "ms": 1_000,
    "millis": 1_000,
    "millisecond": 1_000,
    "milliseconds": 1_000,
    # Microseconds
    "us": 1,
    "micro": 1,
    "microsecond": 1,
    "microseconds": 1,
}


def parse(text):
    """Parse a strict duration string into a datetime.timedelta.

    Grammar (exactly one complete expression, nothing else):

        duration := pair (pair)*
        pair     := integer unit
        integer  := "0" | [1-9][0-9]*   (non-negative, no leading zeros, no signs)
        unit     := one of the keys in _UNIT_TO_MICROSECONDS

    Pairs must be separated by one or more spaces. The integer and its unit are
    separated by one or more spaces. No leading or trailing whitespace is
    allowed — callers should strip beforehand if they want leniency, because
    accepting whitespace here would invite the "is '  ' a valid duration?"
    question, and strictness is the point of this library.

    Returns a datetime.timedelta whose total microseconds is the sum of
    each (integer, unit) pair. Raises StrictTimeDeltaError on any deviation.
    """
    if not isinstance(text, str):
        raise StrictTimeDeltaError(
            "expected a str, got {0}".format(type(text).__name__)
        )
    if text == "":
        raise StrictTimeDeltaError("empty input")

    if text[0] == " " or text[-1] == " ":
        raise StrictTimeDeltaError("leading or trailing whitespace not allowed")

    # Split on runs of spaces so internal spacing is tolerant: "1h  2m"
    # tokenizes to ["1", "h", "2", "m"]. Leading/trailing whitespace is rejected
    # above. A token boundary is also emitted when the character type changes
    # from digit to non-digit, so "1h" becomes ["1", "h"] and "1 hour" becomes
    # ["1", "hour"].
    tokens = []
    current = []
    prev_digit = None
    for ch in text:
        if ch == " ":
            if current:
                tokens.append("".join(current))
                current = []
                prev_digit = None
        else:
            is_digit = ch in "0123456789"
            if prev_digit is not None and is_digit != prev_digit and current:
                tokens.append("".join(current))
                current = []
            current.append(ch)
            prev_digit = is_digit
    if current:
        tokens.append("".join(current))

    if len(tokens) % 2 != 0:
        raise StrictTimeDeltaError(
            "expected integer/unit pairs, got an odd number of tokens"
        )

    total_microseconds = 0
    for i in range(0, len(tokens), 2):
        number_token = tokens[i]
        unit_token = tokens[i + 1]

        if number_token == "0":
            number = 0
        elif (
            number_token[0] in "123456789"
            and all(c in "0123456789" for c in number_token)
        ):
            # Leading-zero check is intentional: "00", "007", "01" are rejected
            # to avoid a "00 days" == "0 days" vs "01 days" == "1 day"
            # ambiguity that strict parsing should not paper over.
            number = int(number_token)
        else:
            raise StrictTimeDeltaError(
                "expected a non-negative integer without leading zeros, got {0!r}".format(
                    number_token
                )
            )

        if unit_token not in _UNIT_TO_MICROSECONDS:
            raise StrictTimeDeltaError(
                "unknown unit {0!r}".format(unit_token)
            )

        total_microseconds += number * _UNIT_TO_MICROSECONDS[unit_token]

    return timedelta(microseconds=total_microseconds)

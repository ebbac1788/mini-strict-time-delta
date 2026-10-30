# mini-strict-time-delta

Parses strict, human-readable duration strings like `"1d 2h 3m 4s 500ms 100us"` into `datetime.timedelta` objects. Anything that is not a complete, well-formed expression is rejected.

```python
from mini_strict_time_delta import parse, StrictTimeDeltaError

try:
    td = parse("1h 30m")
except StrictTimeDeltaError:
    # bad input
    pass
```

The function `parse(text: str) -> datetime.timedelta` accepts a string of one or more integer/unit pairs separated by spaces. Accepted units (case-sensitive): `d`, `day`, `days`, `h`, `hour`, `hours`, `m`, `min`, `minute`, `minutes`, `s`, `sec`, `second`, `seconds`, `ms`, `millis`, `millisecond`, `milliseconds`, `us`, `micro`, `microsecond`, `microseconds`. Integers must be non-negative with no leading zeros, no signs, no decimals. `StrictTimeDeltaError` (a subclass of `ValueError`) is raised on any deviation.

## Why this exists

Other duration parsers guess at loose input — accepting `"1.5h"`, `"01:30"`, `"  1h  "`, or ignoring trailing junk. That is convenient for user-facing forms but wrong for configuration and contract validation, where a typo should surface as an error rather than silently producing `timedelta(hours=1.5)` when seconds were intended. This library picks the strict side of that trade-off: one grammar, no lenient fallbacks, no guesswork.

## Awkward edge

Internal spacing between pairs is tolerant (`"1h  2m"` is accepted and equal to `"1h 2m"`), but leading and trailing whitespace are rejected. If you are reading durations from a config file that may contain stray newlines or indentation, strip the value yourself before calling `parse`. The library does not do this for you so that `" 1h"` and `"1h"` remain distinguishable to the caller.

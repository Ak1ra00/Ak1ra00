#!/usr/bin/env python3
"""Draw the activity field report from live contribution data.

.github/workflows/activity.yml runs this daily and publishes desktop and compact SVGs to the
`output` branch, so main's history stays free of bot commits.

    tools/activity.py --out DIR                   live data (needs GITHUB_TOKEN)
    tools/activity.py --out DIR --from-json FILE  a saved GraphQL response
    tools/activity.py --out DIR --placeholder     the honest "first sync pending" panel
    tools/activity.py --out DIR --demo            synthetic data, for local previews only

Writes DIR/activity-{dark,light}.svg and matching -compact.svg variants. The login comes from
--login, else $GITHUB_REPOSITORY_OWNER, else Ak1ra00. Standard library only.
"""

import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from svgkit import ASSETS, FULL_W, THEMES, n  # noqa: E402
from design import document, display, display_width, label, rect, rule  # noqa: E402

API = "https://api.github.com/graphql"
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# ------------------------------------------------------------------- data --

def fetch(login, token):
    """The raw GraphQL response for `login`; exits non-zero on any failure."""
    if not token:
        sys.exit("activity: GITHUB_TOKEN is not set (use --demo, --placeholder or --from-json offline)")
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": f"{login}-profile-activity",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        sys.exit(f"activity: GitHub API answered HTTP {err.code}: {detail}")
    except urllib.error.URLError as err:
        sys.exit(f"activity: cannot reach the GitHub API: {err.reason}")


def parse(payload, login):
    """date -> count from a GraphQL response, plus the calendar's own total."""
    if payload.get("errors"):
        sys.exit("activity: GraphQL error: " + "; ".join(
            e.get("message", "unknown") for e in payload["errors"]))
    user = (payload.get("data") or {}).get("user")
    if not user:
        sys.exit(f"activity: GitHub has no user {login!r}")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days[dt.date.fromisoformat(day["date"])] = int(day["contributionCount"])
    if not days:
        sys.exit("activity: the contribution calendar came back empty")
    return days, int(calendar["totalContributions"])


def demo_days(end=dt.date(2026, 10, 29)):
    """A deterministic, plausible-looking year. Never published: --demo stamps it."""
    rng = random.Random(0x5EC21)
    start = end - dt.timedelta(days=364 + (end.weekday() + 1) % 7)
    days, day = {}, start
    while day <= end:
        t = (day - start).days
        burst = 1 + 2.4 * max(0.0, math.sin(t / 47.0)) ** 3 + (2.2 if 318 < t < 352 else 0)
        lam = 1.7 * burst * (1.3 if day.weekday() >= 5 else 1.0)
        count = 0
        if rng.random() > 0.2:  # Poisson(lam), Knuth
            limit, p = math.exp(-lam), rng.random()
            while p > limit:
                count += 1
                p *= rng.random()
        days[day] = count
        day += dt.timedelta(days=1)
    for k in range(1, 12):  # a live streak, so the panel shows one
        days[end - dt.timedelta(days=k)] = max(1, days[end - dt.timedelta(days=k)])
    days[end] = 0  # and "nothing yet today", which must not break it
    return days


# ------------------------------------------------------------------ stats --

def series(days):
    """Every calendar day from first to last, in order; missing days count as zero."""
    first, last = min(days), max(days)
    return [(first + dt.timedelta(days=i), days.get(first + dt.timedelta(days=i), 0))
            for i in range((last - first).days + 1)]


def streaks(seq):
    """(current, longest) runs of days with contributions, over a continuous series.

    The current streak counts back from the last day (today); a today with no
    contributions yet starts the count from yesterday instead of ending it.
    """
    longest = run = 0
    for _, count in seq:
        run = run + 1 if count > 0 else 0
        longest = max(longest, run)
    i = len(seq) - 1
    if i >= 0 and seq[i][1] == 0:
        i -= 1
    current = 0
    while i >= 0 and seq[i][1] > 0:
        current += 1
        i -= 1
    return current, longest


def weekly(seq):
    """[(sunday, total)] in the calendar's Sunday-first weeks."""
    weeks = []
    for day, count in seq:
        sunday = day - dt.timedelta(days=(day.weekday() + 1) % 7)
        if weeks and weeks[-1][0] == sunday:
            weeks[-1][1] += count
        else:
            weeks.append([sunday, count])
    return [tuple(w) for w in weeks]


def summarize(days, total=None):
    seq = series(days)
    current, longest = streaks(seq)
    by_weekday = [0] * 7
    for day, count in seq:
        by_weekday[day.weekday()] += count
    busiest = max(seq, key=lambda dc: (dc[1], dc[0]))  # the most recent on a tie
    return {
        "total": sum(c for _, c in seq) if total is None else total,
        "current": current,
        "longest": longest,
        "busiest": busiest if busiest[1] > 0 else None,
        "weekdays": by_weekday,
        "top": by_weekday.index(max(by_weekday)) if any(by_weekday) else None,
        "weeks": weekly(seq),
        "today": seq[-1][0],
    }


# ---------------------------------------------------------------- drawing --

H = 360
COMPACT_H = 500


def graph(d, st, mode, x, y, width, height):
    """Weekly bars, with a stable baseline even for a single or all-zero week."""
    weeks = st["weeks"] if st else []
    values = [count for _, count in weeks] or [0] * 53
    peak = max(values)
    count = len(values)
    pitch = width / count
    bar_width = min(12, max(1, pitch * 0.65))
    out = [label(d, x, y - 17, "WEEKLY CONTRIBUTIONS", 10),
           label(d, x + width, y - 17, f"{peak:,} / WK" if st else "— / WK", 10, anchor="end")]
    for ratio in (0, 0.5, 1):
        gy = y + height * ratio
        out.append(rule(d, x, gy, x + width, gy,
                        extra='stroke-dasharray="2 5"' if ratio < 1 else ''))
    for i, value in enumerate(values):
        bx = x + i * pitch + (pitch - bar_width) / 2
        bh = value / peak * height if peak else 0
        # A zero is a baseline mark, never a fabricated contribution.
        fill = "accent" if value and value == peak else "fg_soft"
        if value:
            out.append(rect(d, bx, y + height - bh, bar_width, bh, fill, radius=1))
        else:
            out.append(rect(d, bx, y + height - 1, bar_width, 1, "muted"))
    if weeks:
        first, last = weeks[0][0], st["today"]
        out.append(label(d, x, y + height + 22, f"{MONTHS[first.month - 1].upper()} {first.year}", 10))
        out.append(label(d, x + width, y + height + 22,
                         f"{MONTHS[last.month - 1].upper()} {last.year}", 10, anchor="end"))
    if not peak:
        pending = mode == "placeholder"
        message = "First sync pending" if pending else "No contributions yet"
        explanation = "The daily workflow will draw this graph." if pending else "This calendar has no recorded contributions."
        out.append(rect(d, x, y + height / 2 - 28, width, 64, "bg"))
        out.append(display(d, x + width / 2, y + height / 2 - 2, message,
                           22, "fg_soft", anchor="middle"))
        out.append(label(d, x + width / 2, y + height / 2 + 20, explanation,
                         10 if width > 400 else 9, anchor="middle"))
    return "".join(out)


def metric(d, x, y, value, caption, size, width):
    text = str(value)
    fitting = min(size, size * width / max(1, display_width(text, size)))
    return display(d, x, y, text, fitting) + label(d, x, y + 23, caption, 10)


def render(theme, st, login, mode, synced, compact=False):
    """Render an honest, readable report in desktop and phone proportions."""
    if st:
        busiest = st["busiest"]
        desc = (f"Contributions per week: {st['total']:,} in total, "
                f"a current streak of {st['current']} days and a longest of {st['longest']} days"
                + (f", busiest on {busiest[0].isoformat()} with {busiest[1]}" if busiest else "")
                + (f", most active on {DAY_NAMES[st['top']]}s" if st["top"] is not None else "") + ".")
    else:
        desc = "Contribution activity: the first sync is pending; GitHub Actions redraws this panel daily."
    if mode == "demo":
        desc = "DEMO DATA, not real activity. " + desc
    w, h = (440, COMPACT_H) if compact else (FULL_W, H)
    pad = 24 if compact else 32
    d = document(w, h, theme, f"{login}: contribution activity", desc)
    d.add(rect(d, 0, 0, w, h))
    d.add(rule(d, pad, 0.5, w - pad, 0.5, "line"))
    d.add(label(d, pad, 32, "07 / FIELD ACTIVITY", 10, "accent"))
    source = "DEMO DATA" if mode == "demo" else "PUBLIC CONTRIBUTIONS"
    d.add(label(d, w - pad, 32, source, 10, "amber" if mode == "demo" else "fg_dim", anchor="end"))
    d.add(display(d, pad, 85, "A year in motion.", 36 if compact else 44))
    if not compact:
        d.add(label(d, w - pad, 81, f"@{login}", 12, anchor="end"))
    d.add(rule(d, pad, 108, w - pad, 108))

    total = f"{st['total']:,}" if st else "—"
    current = st["current"] if st else "—"
    longest = st["longest"] if st else "—"
    if compact:
        d.add(metric(d, 24, 162, total, "CONTRIBUTIONS", 46, 137))
        d.add(metric(d, 184, 162, current, "CURRENT / DAYS", 36, 99))
        d.add(metric(d, 311, 162, longest, "LONGEST / DAYS", 36, 105))
        d.add(graph(d, st, mode, 24, 238, 392, 175))
        d.add(rule(d, 24, 452, 416, 452))
        stamp = "FIRST SYNC PENDING" if mode == "placeholder" else f"SYNC {synced}"
        d.add(label(d, 24, 475, stamp, 10))
    else:
        d.add(graph(d, st, mode, 32, 156, 504, 136))
        d.add(rule(d, 568, 140, 568, 308))
        d.add(metric(d, 600, 190, total, "CONTRIBUTIONS", 54, 248))
        d.add(metric(d, 600, 273, current, "CURRENT / DAYS", 36, 112))
        d.add(metric(d, 736, 273, longest, "LONGEST / DAYS", 36, 112))
        d.add(rule(d, 32, 326, 848, 326))
        stamp = "FIRST SYNC PENDING" if mode == "placeholder" else f"SYNC {synced}"
        d.add(label(d, 32, 347, stamp, 10))
        d.add(label(d, 848, 347, "AUTO-REDRAWN DAILY", 10, anchor="end"))
    return d


# -------------------------------------------------------------------- cli --

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="directory for activity-{dark,light}.svg")
    ap.add_argument("--login", default=os.environ.get("GITHUB_REPOSITORY_OWNER") or "Ak1ra00")
    source = ap.add_mutually_exclusive_group()
    source.add_argument("--demo", action="store_true", help="synthetic data, stamped DEMO DATA")
    source.add_argument("--placeholder", action="store_true", help='the "first sync pending" panel')
    source.add_argument("--from-json", metavar="FILE", help="render a saved GraphQL response")
    args = ap.parse_args(argv)

    out = os.path.realpath(args.out)
    if args.demo and (out + os.sep).startswith(os.path.realpath(ASSETS) + os.sep):
        sys.exit("activity: --demo output must never land in assets/; pick a scratch directory")

    now = dt.datetime.now(dt.timezone.utc)
    synced = now.strftime("%Y-%m-%d %H:%M UTC")
    if args.placeholder:
        mode, st = "placeholder", None
    elif args.demo:
        mode, st = "demo", summarize(demo_days())
        synced = "2026-10-29 04:17 UTC"  # fixed, so demo renders are reproducible
    else:
        if args.from_json:
            with open(args.from_json, encoding="utf-8") as fh:
                payload = json.load(fh)
        else:
            payload = fetch(args.login, os.environ.get("GITHUB_TOKEN", ""))
        days, total = parse(payload, args.login)
        mode, st = "live", summarize(days, total)

    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        for compact in (False, True):
            suffix = "-compact" if compact else ""
            path = render(theme, st, args.login, mode, synced, compact).save(f"activity-{theme}{suffix}.svg", out)
            print(f"activity: wrote {path} ({os.path.getsize(path) / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()

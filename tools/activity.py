#!/usr/bin/env python3
"""Draw the btop-style activity panel from live contribution data.

.github/workflows/activity.yml runs this daily and publishes the two SVGs to the
`output` branch, so main's history stays free of bot commits.

    tools/activity.py --out DIR                   live data (needs GITHUB_TOKEN)
    tools/activity.py --out DIR --from-json FILE  a saved GraphQL response
    tools/activity.py --out DIR --placeholder     the honest "first sync pending" panel
    tools/activity.py --out DIR --demo            synthetic data, for local previews only

Writes DIR/activity-dark.svg and DIR/activity-light.svg. The login comes from
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

from svgkit import ASSETS, FULL_W, MARGIN, THEMES, Doc, n  # noqa: E402

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
# A btop window: rounded boxes whose titles sit in the border between ┐ and ┌,
# a dotted area graph coloured by height, and segmented meters, all in the
# Oracle btop theme (teal idle -> violet busy -> amber hot).

H = 320
SIZE = 12            # terminal text; box strokes match the font's box-drawing weight
CW = 0.6 * SIZE      # one terminal cell
LINE = 0.1 * SIZE    # thickness of ─ in JetBrains Mono

BX, BY, BW, BH = 32, 38, FULL_W - 64, 248      # the btop box
GX0, GX1, GY0, GY1 = 78, 524, 70, 236          # graph: dot centres span this
SX, SY, SW, SH = 546, 58, 288, 212             # the stats box inside it
WEEKS = 53                                     # columns when there is no data yet


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(round(v) for v in rgb)


def _mix(a, b, t):
    a, b = (tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in (a, b))
    return _hex(x + (y - x) * t for x, y in zip(a, b))


def ramp_stops(d):
    return d.c("cyan"), d.c("violet"), d.c("amber_bright" if d.theme == "dark" else "amber")


def ramp(d, t):
    lo, mid, hi = ramp_stops(d)
    return _mix(lo, mid, t / 0.5) if t <= 0.5 else _mix(mid, hi, (t - 0.5) / 0.5)


def box(d, x, y, w, h, r):
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" '
            f'fill="none" stroke="{d.c("box")}" stroke-width="{n(LINE)}"/>')


def tag(d, x, y, parts, top=True):
    """A btop title in the border line at y: ┐title┌ on top, ┘title└ at the bottom."""
    s = "".join(p[0] for p in parts)
    left, right = ("┐", "┌") if top else ("┘", "└")
    base = y + 0.37 * SIZE  # puts the glyphs' horizontal stroke on the line
    x_end = x + (len(s) + 1) * CW
    return "".join([
        f'<rect x="{n(x + 0.3 * SIZE)}" y="{n(y - 1.5)}" width="{n(x_end - x)}" '
        f'height="3" fill="{d.c("bg")}"/>',
        d.text(x, base, left, SIZE, 400, "box"),
        d.rich(x + CW, base, parts, SIZE),
        d.text(x_end, base, right, SIZE, 400, "box"),
    ])


def tag_end(d, x_right, y, parts, top=True):
    """tag() aligned so its closing glyph ends at x_right."""
    width = (sum(len(p[0]) for p in parts) + 2) * CW
    return tag(d, x_right - width, y, parts, top)


def graph(d, st, mode):
    values = [c for _, c in st["weeks"]] if st else [0] * WEEKS
    cols = 2 * len(values) - 1
    pitch = (GX1 - GX0) / (cols - 1)
    rows = int((GY1 - GY0) / pitch) + 1
    top = GY1 - (rows - 1) * pitch
    out = []

    # the idle matrix every dot sits in, like an unlit braille cell
    pid = d.uid("cell")
    d.define(f'<pattern id="{pid}" width="{n(pitch)}" height="{n(pitch)}" patternUnits="userSpaceOnUse" '
             f'x="{n(GX0 - pitch / 2)}" y="{n(GY1 - pitch / 2)}"><circle cx="{n(pitch / 2)}" '
             f'cy="{n(pitch / 2)}" r="0.8" fill="{d.c("line")}"/></pattern>')
    out.append(f'<rect x="{n(GX0 - pitch / 2)}" y="{n(top - pitch / 2)}" width="{n(GX1 - GX0 + pitch)}" '
               f'height="{n(GY1 - top + pitch)}" fill="url(#{pid})" opacity="0.8"/>')

    vmax = max(values)
    if vmax:
        lo, mid, hi = ramp_stops(d)
        d.define(f'<linearGradient id="heat" gradientUnits="userSpaceOnUse" x1="0" y1="{n(GY1)}" '
                 f'x2="0" y2="{n(top)}"><stop offset="0" stop-color="{lo}"/>'
                 f'<stop offset="0.5" stop-color="{mid}"/><stop offset="1" stop-color="{hi}"/>'
                 f'</linearGradient>', key="heat")
        # one dotted column per half week: a round-capped line dashed every `pitch`
        lines = []
        for col in range(cols):
            i, odd = divmod(col, 2)
            v = (values[i] + values[i + 1]) / 2 if odd else values[i]
            level = 0 if v <= 0 else max(1, math.ceil(v / vmax * rows))
            if level:
                x = n(GX0 + col * pitch)
                lines.append(f'<line x1="{x}" y1="{n(GY1)}" x2="{x}" '
                             f'y2="{n(GY1 - (level - 1) * pitch - 0.01)}"/>')
        out.append(f'<g stroke="url(#heat)" stroke-width="2.8" stroke-linecap="round" '
                   f'stroke-dasharray="0 {n(pitch)}">{"".join(lines)}</g>')
        # scale: the busiest week at the top row, zero on the baseline
        out.append(d.text(GX0 - 10, top + 3.8, str(vmax), 10.5, 700, "fg_soft", anchor="end"))
        out.append(d.text(GX0 - 10, GY1 + 3.8, "0", 10.5, 400, "fg_dim", anchor="end"))
        out.append(d.text(GX0 - 10, top + 15, "/wk", 9, 400, "fg_dim", anchor="end"))
        # month ticks under the first week that starts in each month
        last_x = -99
        for i, (sunday, _) in enumerate(st["weeks"]):
            if i and sunday.month == st["weeks"][i - 1][0].month:
                continue
            x = GX0 + 2 * i * pitch
            if i == 0 and sunday.day > 14:
                continue  # a partial month at the left edge would crowd the next label
            if x - last_x < 30:
                continue
            out.append(d.text(x, GY1 + 19, MONTHS[sunday.month - 1], 10.5, 400, "fg_dim"))
            last_x = x
    else:
        # a btop-style dialog over the idle matrix
        cx, cy = (GX0 + GX1) / 2, (top + GY1) / 2
        if mode == "placeholder":
            lines = [("first sync pending", 15, 700, "fg_soft"),
                     ("regenerated daily by GitHub Actions", 12, 400, "fg_dim")]
        else:
            lines = [("no contributions in the last year", 15, 700, "fg_soft")]
        w = max(len(s) * 0.6 * size for s, size, _, _ in lines) + 56
        h = 30 + 22 * len(lines)
        out.append(f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" '
                   f'rx="6" fill="{d.c("bg")}" stroke="{d.c("box")}" stroke-width="{n(LINE)}"/>')
        out.append(tag(d, cx - w / 2 + 10, cy - h / 2, [("²", "cyan", 700), ("sync", "fg_soft", 700)]))
        y = cy - h / 2 + 34
        for s, size, weight, fill in lines:
            out.append(d.text(cx, y, s, size, weight, fill, anchor="middle"))
            y += 22
    if mode == "demo":
        out.append(d.text((GX0 + GX1) / 2, (top + GY1) / 2 + 15, "DEMO DATA", 46, 800, "amber",
                          anchor="middle", opacity="0.16"))
    return "".join(out)


def stats_box(d, st, login):
    out = [box(d, SX, SY, SW, SH, 6), tag(d, SX + 10, SY, [(login, "fg_soft", 700)])]
    x0, cols = SX + 14, int((SW - 28) / CW)
    x1 = x0 + cols * CW
    dash = "—"

    def plural(k):
        return f"{k} day" if k == 1 else f"{k} days"

    if st:
        busiest = st["busiest"]
        rows = [
            ("contributions", f"{st['total']:,}", "fg_bright", 700),
            ("current streak", plural(st["current"]), "fg", 400),
            ("longest streak", plural(st["longest"]), "fg", 400),
            ("busiest day", f"{busiest[0].isoformat()} · {busiest[1]}" if busiest else dash, "fg", 400),
            ("most active", DAY_NAMES[st["top"]] if st["top"] is not None else dash, "cyan", 700),
        ]
    else:
        rows = [(label, dash, "fg_dim", 400) for label in
                ("contributions", "current streak", "longest streak", "busiest day", "most active")]
    y = SY + 23
    for label, value, color, weight in rows:
        if value == dash:
            color, weight = "fg_dim", 400
        out.append(d.text(x0, y, label, SIZE, 400, "fg_dim"))
        out.append(d.text(x1, y, value, SIZE, weight, color, anchor="end"))
        y += 16.5
    out.append(f'<path d="M{n(x0)} {n(y - 8)}H{n(x1)}" stroke="{d.c("line")}" stroke-width="1"/>')

    # btop-style meters: each weekday's share, scaled so the busiest weekday is full
    y += 9
    cells = cols - 9
    shares = st["weekdays"] if st else [0] * 7
    total, peak = sum(shares), max(shares)
    for i, name in enumerate(WEEKDAYS):
        is_top = st is not None and st["top"] == i
        out.append(d.text(x0, y, name, SIZE, 700 if is_top else 400, "cyan" if is_top else "fg_dim"))
        lit = round(shares[i] / peak * cells) if peak else 0
        rects = []
        for j in range(cells):
            fill = ramp(d, j / (cells - 1)) if j < lit else d.c("bg_raised" if d.theme == "dark" else "line")
            rects.append(f'<rect x="{n(x0 + (4 + j) * CW + 0.7)}" y="{n(y - 8.3)}" width="{n(CW - 1.4)}" '
                         f'height="8" rx="1" fill="{fill}"/>')
        out.append("".join(rects))
        pct = f"{round(100 * shares[i] / total)}%" if total else dash
        out.append(d.text(x1, y, pct, SIZE, 400, "fg" if is_top else "fg_dim", anchor="end"))
        y += 14.5
    return "".join(out)


def render(theme, st, login, mode, synced):
    if st:
        b = st["busiest"]
        desc = (f"Contributions per week over the last 52 weeks: {st['total']:,} in total, "
                f"a current streak of {st['current']} days and a longest of {st['longest']} days"
                + (f", busiest on {b[0].isoformat()} with {b[1]}" if b else "")
                + (f", most active on {DAY_NAMES[st['top']]}s" if st["top"] is not None else "") + ".")
    else:
        desc = "Contribution activity: the first sync is pending; GitHub Actions redraws this panel daily."
    if mode == "demo":
        desc = "DEMO DATA, not real activity. " + desc
    d = Doc(FULL_W, H, theme, f"{login}: contribution activity", desc)
    d.css("@keyframes live{0%,100%{opacity:1}50%{opacity:.25}}.live{animation:live 2.4s ease-in-out infinite}")
    d.add(d.window(MARGIN, MARGIN, FULL_W - 2 * MARGIN, H - 2 * MARGIN))
    d.add(box(d, BX, BY, BW, BH, 7))
    d.add(tag(d, BX + 12, BY, [("¹", "cyan", 700), ("activity", "fg_soft", 700)]))
    d.add(tag_end(d, BX + BW - 12, BY, [("contributions per week", "fg_soft"),
                                        (" · last 52 weeks", "fg_dim")]))
    if mode == "placeholder":
        d.add(tag(d, BX + 12, BY + BH, [("awaiting first sync", "fg_dim")], top=False))
    else:
        d.add(tag(d, BX + 12, BY + BH, [("  synced ", "fg_dim"), (synced, "fg_soft")], top=False))
        d.add(f'<circle class="live" cx="{n(BX + 12 + 1.5 * CW)}" cy="{n(BY + BH)}" r="3" '
              f'fill="{d.c("cyan")}"/>')
    if mode == "demo":
        d.add(tag_end(d, BX + BW - 12, BY + BH, [("DEMO DATA", "amber", 700)], top=False))
    d.add(graph(d, st, mode))
    d.add(stats_box(d, st, login))
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
        path = render(theme, st, args.login, mode, synced).save(f"activity-{theme}.svg", out)
        print(f"activity: wrote {path} ({os.path.getsize(path) / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()

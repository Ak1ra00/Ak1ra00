# tools

Every SVG on the profile is drawn by these scripts. None of them is a
screenshot or a third-party widget. Each script writes a dark and a light variant:

| theme | palette | look |
| --- | --- | --- |
| dark  | the [Oracle](https://github.com/Ak1ra00/oracle) desktop colours | cyan for the point, violet for its blinding, amber for the paper key, on charcoal |
| light | the same three inks | printed on paper, the "paper oracle" |

```
svgkit.py       shared kit: palettes, Hyprland-style windows, text as glyph outlines
hero.py         assets/hero-*.svg      name + the group law on y² = x³ − 3x + 5, animated
fetch.py        assets/fetch-*.svg     fastfetch card with a braille plot of y² = x³ − 3x + 1
cards.py        assets/card-*-*.svg    the six project cards
footer.py       assets/footer-*.svg    sign-off
activity.py     activity-*.svg         contribution panel, redrawn daily by CI on the `output` branch
build.py        runs hero, fetch, cards and footer, then checks every SVG parses
make_glyphs.py  rebuilds glyphs.json from the JetBrains Mono TTFs (needs fonttools)
```

```bash
python3 tools/build.py                          # every static asset
python3 tools/activity.py --demo --out /tmp/a   # preview the activity panel with fake data
```

Everything except `make_glyphs.py` is plain Python 3 with no dependencies.

**Why outlines instead of fonts?** GitHub shows these SVGs through `<img>`,
which cannot load web fonts, and system monospace fonts differ in width.
`glyphs.json` holds JetBrains Mono's outlines, and each SVG places them with
`<use>`, so the lettering is identical on every machine. JetBrains Mono is under
the SIL Open Font License 1.1; see [`fonts/OFL.txt`](fonts/OFL.txt).

**Motion.** Animations are CSS inside each SVG. Every file honours
`prefers-reduced-motion` and shows its finished state when motion is off.

**Activity panel.** `.github/workflows/activity.yml` runs daily, on manual
dispatch, and on every push to `main`. It reads the public contribution
calendar through GraphQL with the workflow's own `GITHUB_TOKEN` and
force-pushes the two SVGs to the orphan `output` branch as a single commit.
That keeps `main`'s history clean and keeps the bot's commits off the
contribution graph.

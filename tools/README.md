# Profile artwork

The profile is built from custom SVGs generated with Python's standard library.
There is no package installation, web server, external font request, or frontend
build step. Run these commands from the repository root:

```bash
python3 tools/build.py
python3 tools/check.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/preview.py --theme dark
python3 tools/preview.py --theme light
```

The build writes **36 static SVGs** into `assets/`: nine panels, each in dark and
light themes, with separate desktop and compact compositions. It replaces the
generated assets, so review their changes alongside the generator changes.
`check.py` validates the SVGs, their internal references, and the README's artwork
references. The unit tests exercise the activity data handling and rendering.

## Layout and drawing

The dark palette uses charcoal, pale green, and lavender; the light palette uses
warm paper and dark green ink. The compact artwork rearranges the content for
narrow screens instead of shrinking the desktop composition. The README's
`<picture>` sources select the appropriate theme and layout.

| File | Purpose |
| --- | --- |
| `design.py` | Shared palettes, display lettering, rules, labels, and geometric elements |
| `svgkit.py` | SVG document assembly, embedded monospace glyphs, and reduced-motion support |
| `hero.py` | Profile identity and the opening illustration |
| `fetch.py` | Workbench inventory: languages, hardware, and desktop |
| `cards.py` | Six project panels, led by vaultless and QUASAR |
| `project_art.py` | Project-specific vector illustrations |
| `footer.py` | Closing statement |
| `activity.py` | Contribution activity, using live data or an explicitly selected offline mode |
| `build.py` | Rebuilds static artwork and checks that every SVG parses |
| `check.py` | Checks generated SVGs and README references |
| `preview.py` | Builds a local HTML preview from the README |
| `test_activity.py` | Activity data and rendering tests |

Animations live inside the SVGs. Reduced-motion rules stop them while keeping
the artwork complete and readable. Every panel includes a title and description;
the README also supplies image alt text.

## Local preview

`preview.py` writes `dist/preview/index-dark.html` or
`dist/preview/index-light.html`. Open the generated file directly in a browser.
It uses the local SVGs and generates activity artwork in
`dist/preview/activity-demo/`, clearly marked as synthetic demo data. `dist/` is
ignored by Git. A different destination can be supplied with `--out FILE.html`.

The preview implements the Markdown and HTML used by this README. GitHub's own
renderer remains the authority for the published profile. Project links and any
remote screenshots still point to their original destinations.

The README loads static artwork from this repository's `main` branch. Local
changes appear on GitHub after they are published to `main`. The new compact
activity images also need a successful run of the activity workflow before
their URLs are available on the `output` branch.

## Lettering

GitHub displays SVGs as images, which cannot load external web fonts. Both
typefaces are therefore bundled as glyph outlines, placed with SVG `<use>`
elements. Normal builds need neither the font files nor font libraries.

- **Space Grotesk Bold** provides display lettering through
  `display-glyphs.json`. Its SIL Open Font License 1.1 is in
  [`fonts/SpaceGrotesk-OFL.txt`](fonts/SpaceGrotesk-OFL.txt).
  `make_display_glyphs.py` regenerates the outlines with `fonttools`; the script
  documents the pinned font source.
- **JetBrains Mono** provides labels and technical text through `glyphs.json`.
  Its SIL Open Font License 1.1 is in [`fonts/OFL.txt`](fonts/OFL.txt).
  `make_glyphs.py` regenerates the outlines with `fonttools` and the Regular,
  Bold, and ExtraBold JetBrains Mono TTF files. Its default font directory is
  `/usr/share/fonts/truetype/jetbrains-mono`; use `--fonts DIR` to select another.

Regenerate glyph data only when the typeface or character set changes. This is
the only workflow that needs `fonttools`; the build, checks, previews, and
activity renderer use the standard library.

## Contribution activity

`.github/workflows/activity.yml` runs daily, on manual dispatch, and on pushes to
`main`. It reads the public contribution calendar through GitHub GraphQL with
the workflow's `GITHUB_TOKEN`, then publishes four SVGs to the orphan `output`
branch: `activity-dark.svg`, `activity-light.svg`, and their `-compact.svg`
variants. Each publication replaces the branch with one commit, keeping generated
activity updates out of `main`.

For local development, choose an offline source explicitly:

```bash
python3 tools/activity.py --demo --out dist/activity-demo
python3 tools/activity.py --placeholder --out dist/activity-placeholder
python3 tools/activity.py --from-json /path/to/calendar.json --out dist/activity-saved
```

`--demo` uses deterministic synthetic data and labels it as such. `--placeholder`
shows that the first sync is pending. `--from-json` accepts a saved GraphQL
response. Live mode is the default and requires `GITHUB_TOKEN` plus access to
`https://api.github.com/graphql`. A live fetch failure stops the command; the
publication workflow does not substitute demo data.

# Profile README — setup

These files belong in a repository named **exactly** `KumarPriyam123` (same as your
username). GitHub treats that repo's README as your profile page. Any other repo name
and it will not show up on your profile.

## First-time setup

```bash
cd KumarPriyam123
git init -b main
git add .
git commit -m "profile readme"
gh repo create KumarPriyam123 --public --source=. --push
```

Without the `gh` CLI: create a new public repo called `KumarPriyam123` on github.com
(GitHub will show a "you found a secret" note when the name matches your username),
then:

```bash
git remote add origin https://github.com/KumarPriyam123/KumarPriyam123.git
git push -u origin main
```

## Files

```
README.md            the profile page
assets/*.svg         light-theme artwork
assets/dark/*.svg    dark-theme artwork
```

Both themes are wired through `<picture>` + `prefers-color-scheme`, so GitHub swaps
them automatically. All text inside the SVGs is vector paths — no font dependency,
so it renders identically on every machine.

## Animation

The SVGs animate on load with CSS keyframes (no JS — GitHub strips scripts from SVG):

| class | effect | used on |
| --- | --- | --- |
| `.dash` | stroke draw-on via `pathLength="1"` + `stroke-dashoffset` | hairlines, the name outline |
| `.f` | fade in | meta rows, path tags, panel chrome |
| `.rise` | fade + 10px translate up | section labels, role line, stat cells |
| `.rot` | 12s loop, four items at ~3s each | the `focus >` line in the header |
| `.d1`-`.d7` | stagger, 0.05s to 1.45s | everything above |

The header name draws itself as an outline first (1.5s), then the solid fill arrives
underneath. Every file honours `prefers-reduced-motion: reduce`: motion is disabled,
elements resolve to their final state, and the rotating line pins to its first item.

Animation replays whenever the page loads. To change the rotating items, edit the
`FOCUS` list in the generator and rebuild.

## Editing the artwork

The SVGs are plain text. To change wording, the safe edit is to regenerate rather than
hand-edit path data. Ask Claude to rebuild any panel — the generator uses JetBrains Mono
converted to outlines at 880px width.

## Still to do

- [ ] Pin your repos: profile → **Customize your pins** → choose 6. Without this,
      GitHub shows your most-starred repos, which is not the same as your best work.
- [ ] Update your GitHub bio to match: `AI Engineer · SDE — retrieval systems,
      agent orchestration, multi-tenant backends. CSE @ NIT Delhi '27`
- [x] Multi-Tenant-Agentic-Data-Pipeline linked (public)
- [ ] Add the JobMatch repo link to the projects table — repo name still unknown
      (JobAutomation is a different project: the n8n application pipeline)
- [ ] Make Clinic-Automation (ClinicQ) and MARL-MAPS public when ready — the table
      links them as soon as you add the URLs
- [ ] Consider renaming the company-assignment repos: Millipixel_assignment_231210062...
      and Azentio_..._231210062_Agentic_Sol sit on your public profile with your roll
      number in the name, and tell every other company where else you interviewed

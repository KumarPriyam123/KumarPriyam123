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

## Editing the artwork

The SVGs are plain text. To change wording, the safe edit is to regenerate rather than
hand-edit path data. Ask Claude to rebuild any panel — the generator uses JetBrains Mono
converted to outlines at 880px width.

## Still to do

- [ ] Pin your repos: profile → **Customize your pins** → choose 6. Without this,
      GitHub shows your most-starred repos, which is not the same as your best work.
- [ ] Update your GitHub bio to match: `AI Engineer · SDE — retrieval systems,
      agent orchestration, multi-tenant backends. CSE @ NIT Delhi '27`
- [ ] Add the JobMatch repo link to the projects table once it is public
- [ ] Make MARL-MAPS and ClinicQ public when you are ready — the table links them as
      soon as you add the URLs

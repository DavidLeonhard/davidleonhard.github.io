# Switching leonhardgebhardt.com to the new design

This replaces the AcademicPages theme with a small custom Jekyll site.
Your everyday workflow stays the same: `bundle exec jekyll serve`, then
`git add -A`, `git commit`, `git push`. Domain, DNS and CNAME are untouched.

Everything happens on a separate branch first, so the live site does not
change until the very last step.

## 1. Start a branch

    cd /Users/leonhardgebhardt/Documents/Website
    git status                 # should say "nothing to commit"
    git branch                 # note the name with the * (main or master)
    git checkout -b redesign

## 2. Remove the old theme, keep what you need

    mkdir -p /tmp/keep
    cp CNAME /tmp/keep/
    cp -R images files /tmp/keep/ 2>/dev/null
    git rm -r -q .
    rm -rf _site .jekyll-cache .sass-cache vendor .bundle
    cp -R /tmp/keep/. .

The old files are not lost: they stay in Git's history and on your main branch.
(This also removes the old `.DS_Store` and `.Rhistory` from Git for good.)

## 3. Add the new files

Unzip the package into the website folder:

    unzip -o ~/Downloads/website-redesign.zip -d .

## 4. Preview locally

    bundle install
    bundle exec jekyll serve

Open http://localhost:4000. The band at the top stays empty until step 5.

## 5. Make the Piranesi halftone

1. Download an etching from an open-access collection, for example the Met
   (metmuseum.org, search "Piranesi Carceri", filter "Open Access") or the
   Rijksmuseum. Save it as `tools/piranesi.jpg` (Git ignores it).
2. Run:

        python3 -m pip install --user pillow numpy
        python3 tools/halftone.py tools/piranesi.jpg assets/img/piranesi-halftone.png --band 0.4

3. Refresh localhost:4000. To adjust: `--band` moves the strip up or down the
   print, `--cell` makes dots finer (5) or bolder (9), `--angle 0` gives a
   straight grid. Update the caption in `_config.yml` (restart the server
   afterwards) and the source in `impressum.md`.

## 6. Fill in the remaining placeholders

- `files/cv.pdf`: put your current CV here (the CV link points to it)
- `impressum.md`: your address and the image source

## 7. Publish

    git add -A
    git commit -m "Redesign: replace AcademicPages with lean layout"
    git checkout main          # or master, see step 1
    git merge redesign
    git push

GitHub Pages rebuilds the site within a minute or two.

## Everyday editing after the switch

- Publications: `_data/publications.yml`
- Talks: `_data/talks.yml` (`selected: true` keeps one visible, the rest fold away)
- Teaching: `_data/teaching.yml`
- About, research themes, statement: `index.html`
- Name, role, links, band image and caption: `_config.yml`
- Colours and fonts: `assets/css/main.css`

Old addresses such as /publications/ and /talks/ redirect to the home page.

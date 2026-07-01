# Morpheme Studios — v2

A redesigned front end for **morphemestudios.com**, rebuilt as a modern, editorial,
photography-led architecture studio site — inspired by Ayers Saint Gross, Woodcliffe,
Minale + Mann and Turner Works.

**Stack:** React 18 · React Router 6 · GSAP 3 (+ ScrollTrigger) · Vite. Content is served by the Django + DRF backend (Morpheme-Studios-Backend).

## Run — local development

> Prerequisite: **Node 20+**. The **backend must be running first** at http://localhost:8000 — follow the backend repo's README ("Local Development") to start it, then come back here.

```bash
# 1. Install dependencies
npm install

# 2. Create a .env file pointing the app at your local backend
#    (create the file in the project root with this single line):
#        VITE_API_URL=http://localhost:8000

# 3. Start the dev server
npm run dev      # http://localhost:5173
```

Open **http://localhost:5173** — the site loads its projects, team, journal and jobs from the backend API. If images or content are missing, confirm the backend is running on port 8000 and that `VITE_API_URL` matches.

```bash
npm run build    # production build → dist/
npm run preview  # preview the production build locally
```

For production, set `VITE_API_URL` to the live API origin at build time, e.g. `VITE_API_URL=https://morphemestudios.com npm run build`.

## What's inside

**Pages** (`src/pages/`)

- `Home` — full-screen hero with parallax, marquee, intro statement, featured projects,
  hover-preview services list, animated stat counters, journal teaser
- `Studio` — philosophy, 4-step approach, leadership grid, three offices
- `Projects` — category filtering, responsive project grid
- `ProjectDetail` — cinematic hero, fact sidebar, parallax gallery, next-project link
- `Journal` — lead article + grid
- `Careers` — values, open roles
- `Contact` — working (frontend-only) form + studio details
- `NotFound` — 404

**Components** (`src/components/`) — `Navbar` (scroll hide/reveal + overlay menu),
`Footer`, `Cursor` (custom trailing cursor), `Loader` (intro counter), `Marquee`,
`Reveal` / `AnimatedHeading` (GSAP scroll entrances), `Parallax`, `ProjectCard`.

**Content** (`src/data/`) — projects, team, services, journal and a single
`images.js` map of curated imagery. All real Morpheme Studios content
(projects, offices, leadership) plus placeholder photography.

**Styles** (`src/styles/`) — `global.css` (design tokens + base),
`components.css`, `pages.css`.

## Design system

- **Palette:** warm bone `#f4f1ea`, near-black ink `#16150f`, clay accent `#9c5a3c`,
  dark sections `#1a1a18`
- **Type:** Fraunces (serif display) + Inter (sans UI/body)
- Custom cursor and scroll-smoothing are disabled on touch / reduced-motion.

## Notes

- The app is fully API-driven: projects, team, journal, jobs and site settings come
  from the backend (`VITE_API_URL`). The contact, careers and newsletter forms POST to
  the backend API.
- Imagery is served from the backend's self-hosted media; manage it via the Django admin.
- Social/legal links in the footer are placeholders (`#`).

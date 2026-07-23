import { useMemo, useState, useRef, useEffect } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'
import Reveal from '../components/Reveal.jsx'
import ProjectCard from '../components/ProjectCard.jsx'
import Seo from '../components/Seo.jsx'
import { api } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizeProject } from '../lib/normalize.js'

export default function Projects() {
  const [active, setActive] = useState('all')
  const headerRef = useRef(null)
  const filterRefs = useRef([])
  const [maxFilterWidth, setMaxFilterWidth] = useState(null)

  // Projects + categories are fetched strictly from the API (DB-driven).
  const { data: projects } = useApi(
    () => api.projects({ page_size: 100 }).then((r) => (r.results || []).map(normalizeProject)),
    [],
    { fallback: [] }
  )
  const { data: apiCats } = useApi(() => api.projectCategories(), [], { fallback: [] })
  const categories = useMemo(() => [{ key: 'all', label: 'All Projects' }, ...(apiCats || [])], [apiCats])

  useEffect(() => {
    if (categories.length > 0 && filterRefs.current.length > 0) {
      let maxW = 0
      filterRefs.current.forEach((el) => {
        if (el) {
          const prevMinW = el.style.minWidth
          el.style.minWidth = 'auto'
          const w = el.offsetWidth
          el.style.minWidth = prevMinW
          if (w > maxW) maxW = w
        }
      })
      if (maxW > 0) {
        setMaxFilterWidth(maxW)
      }
    }
  }, [categories, projects])

  const list = useMemo(
    () => (active === 'all' ? projects : projects.filter((p) => p.category === active)),
    [active, projects]
  )

  useGSAP(() => {
    const tl = gsap.timeline()
    tl.from('.page-title', {
      yPercent: 110,
      duration: 1.2,
      ease: 'power4.out',
      stagger: 0.08,
    })
      .from('.page-head .label, .page-head-sub', {
        y: 20,
        autoAlpha: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out'
      }, '-=0.8')
      .from('.filters', {
        autoAlpha: 0,
        y: 10,
        duration: 0.8
      }, '-=0.4')
  }, { scope: headerRef })

  return (
    <div className="page" ref={headerRef}>
      <Seo title="Projects — Morpheme Studios" description="Cultural, corporate and residential architecture & design work across three continents." />
      <header className="page-head wrap">
        <Reveal><p className="label">Selected Work</p></Reveal>
        <Reveal variant="fade"><h1 className="display page-title">Projects</h1></Reveal>
        <Reveal variant="fade" delay={0.15}>
          <p className="lead maxw-720 page-head-sub">
            Cultural, corporate and residential work across three continents — each
            project a search for one clear idea, carried from sketch to handover.
          </p>
        </Reveal>
      </header>

      {/* Filters */}
      <div className="wrap filters">
        {categories.map((c, i) => (
          <button
            key={c.key}
            ref={(el) => (filterRefs.current[i] = el)}
            style={maxFilterWidth ? { minWidth: `${maxFilterWidth}px` } : {}}
            className={`filter ${active === c.key ? 'is-active' : ''}`}
            onClick={() => setActive(c.key)}
            data-cursor
          >
            {c.label}
            <span className="filter-count">
              {c.key === 'all'
                ? projects.length
                : projects.filter((p) => p.category === c.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* Grid */}
      <section className="section-tight">
        <div className="wrap grid cols-2 projects-grid" key={active}>
          {list.map((p, i) => (
            <Reveal variant="fade" key={p.slug}>
              <ProjectCard project={p} index={i} ratio="ratio-4-3" />
            </Reveal>
          ))}
        </div>
        {list.length === 0 && (
          <p className="wrap body-muted">No projects in this category yet.</p>
        )}
      </section>
    </div>
  )
}

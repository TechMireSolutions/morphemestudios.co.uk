import { useParams, Link, Navigate } from 'react-router-dom'
import { useRef, useEffect } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'

import Reveal from '../components/Reveal.jsx'
import Parallax from '../components/Parallax.jsx'
import Seo from '../components/Seo.jsx'
import { api } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizeProject } from '../lib/normalize.js'

export default function ProjectDetail() {
  const { slug } = useParams()

  useEffect(() => {
    window.scrollTo(0, 0)
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  }, [slug])
  // Strictly API-driven (DB is the source of truth).
  const { data: project, loading } = useApi(
    () => api.project(slug).then(normalizeProject),
    [slug],
    { fallback: null }
  )
  const { data: all } = useApi(
    () => api.projects({ page_size: 100 }).then((r) => (r.results || []).map(normalizeProject)),
    [], { fallback: [] })
  const projects = all || []
  const heroRef = useRef(null)

  useGSAP(
    () => {
      if (!heroRef.current) return
      
      const tl = gsap.timeline()
      
      tl.from('.pd-hero-img', {
        scale: 1.4,
        duration: 2.2,
        ease: 'power4.out',
      })
      .from('.pd-word > span', {
        yPercent: 110,
        duration: 1.2,
        ease: 'power4.out',
        stagger: 0.08,
      }, '-=1.6')
      .from('.pd-hero-meta > *', {
        y: 20,
        autoAlpha: 0,
        duration: 0.9,
        stagger: 0.1,
        ease: 'power3.out'
      }, '-=0.8')

      gsap.to('.pd-hero-img img', {
        yPercent: 18,
        scale: 1.15,
        ease: 'none',
        scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: true },
      })
    },
    { scope: heroRef, dependencies: [slug] }
  )

  if (loading && !project) return <div className="page-loader" />
  if (!project) return <Navigate to="/projects" replace />

  const idx = projects.findIndex((p) => p.slug === slug)
  const next = idx >= 0 ? projects[(idx + 1) % projects.length] : projects[0]

  return (
    <div className="page page-detail">
      <Seo title={`${project.title} — Morpheme Studios`} description={project.excerpt} image={project.cover} />
      {/* Hero */}
      <section ref={heroRef} className="pd-hero">
        <div className="pd-hero-img">
          <img src={project.cover} alt={project.title} />
          <div className="pd-hero-scrim" />
        </div>
        <div className="wrap pd-hero-content">
          <h1 className="pd-hero-title display">
            {project.title.split(' ').map((w, i) => (
              <span key={i} className="pd-word"><span>{w}&nbsp;</span></span>
            ))}
          </h1>
          <div className="pd-hero-meta">
            <span className="label">{project.location}</span>
            <span className="label">{project.year}</span>
            <span className="label">{project.status}</span>
          </div>
        </div>
      </section>

      {/* Overview */}
      <section className="section">
        <div className="wrap pd-overview">
          <div className="pd-overview-side">
            <Reveal variant="stagger">
              <div className="pd-fact">
                <span className="label">Discipline</span>
                <p>{project.type}</p>
              </div>
              <div className="pd-fact">
                <span className="label">Location</span>
                <p>{project.location}</p>
              </div>
              <div className="pd-fact">
                <span className="label">Year</span>
                <p>{project.year}</p>
              </div>
              <div className="pd-fact">
                <span className="label">Services</span>
                <p>{project.services.join(', ')}</p>
              </div>
            </Reveal>
          </div>
          <div className="pd-overview-main">
            <Reveal>
              <p className="h-md pd-excerpt">{project.excerpt}</p>
            </Reveal>
            <Reveal variant="fade" delay={0.15}>
              <p className="lead body-muted pd-desc">{project.description}</p>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Gallery */}
      <section className="section-tight pd-gallery">
        <div className="wrap pd-gallery-wrap">
          {project.gallery.map((item, i) => {
            const src = typeof item === 'string' ? item : item.src
            const caption = typeof item === 'string' ? '' : item.caption
            return (
              <div key={i} className={`pd-shot-wrapper ${i % 3 === 0 ? 'is-full' : ''}`}>
                <Reveal variant="clip" className="pd-shot">
                  <Parallax
                    src={src}
                    alt={caption || `${project.title} — view ${i + 1}`}
                    ratio={i % 3 === 0 ? 'ratio-16-9' : 'ratio-4-3'}
                  />
                </Reveal>
                {caption && (
                  <Reveal variant="fade">
                    <figcaption className="pd-shot-caption">{caption}</figcaption>
                  </Reveal>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* Next project */}
      {next && (
        <section className="section dark pd-next">
          <Link to={`/projects/${next.slug}`} className="wrap pd-next-link" data-cursor="Next">
            <span className="label">Next project</span>
            <h2 className="display pd-next-title">{next.title}</h2>
            <div className="media zoom ratio-16-9 pd-next-media">
              <img src={next.cover} alt={next.title} loading="lazy" />
            </div>
          </Link>
        </section>
      )}
    </div>
  )
}

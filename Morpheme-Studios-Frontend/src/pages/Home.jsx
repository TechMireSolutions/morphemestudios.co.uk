import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'

import Reveal from '../components/Reveal.jsx'
import Seo from '../components/Seo.jsx'
import Marquee from '../components/Marquee.jsx'
import ProjectCard from '../components/ProjectCard.jsx'

import { api, absMedia } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizeProject, normalizePost } from '../lib/normalize.js'

const HERO_IMG = '/assets/architecture.jpg'   // static brand asset (not DB content)

export default function Home() {
  const heroRef = useRef(null)
  const { data: featured } = useApi(
    () => api.projects({ is_featured: true, ordering: 'featured_order' }).then((r) => (r.results || []).map(normalizeProject)),
    [], { fallback: [] })
  const { data: blogList } = useApi(
    () => api.blog({ page_size: 3 }).then((r) => (r.results || []).map(normalizePost)),
    [], { fallback: [] })
  const { data: settings } = useApi(() => api.settings(), [], { fallback: {} })
  const { data: categoryList } = useApi(
    () => api.projectCategories().then((r) => r.results || r || []), 
    [], { fallback: [] }
  )
  const blogTop = (blogList || []).slice(0, 3)
  const defaultServices = [
    { no: '01', title: 'Architecture Design', blurb: 'At Morpheme Studios is an Architecture and design services', image: HERO_IMG },
    { no: '02', title: 'Interior Design', blurb: 'Morpheme Studios’ interior design team complements our architectural designs with carefully curated interiors.', image: HERO_IMG },
    { no: '03', title: 'Retail & Commercial', blurb: 'Creating engaging spaces for retail and commercial environments.', image: HERO_IMG },
    { no: '04', title: 'Competition', blurb: 'We breathe new life into existing structures through thoughtful renovation and restoration.', image: HERO_IMG },
  ]
  const servicesFromCategories = categoryList.map((cat, i) => ({
    no: String(i + 1).padStart(2, '0'),
    title: cat.label,
    blurb: cat.blurb || '',
    image: cat.image ? absMedia(cat.image.file) : HERO_IMG,
  }))
  const services = servicesFromCategories.length > 0 ? servicesFromCategories : defaultServices
  const stats = settings?.stats || []

  // Hero intro + background parallax
  useGSAP(
    () => {
      if (!heroRef.current) return
      // Intro sequence
      const tl = gsap.timeline({ delay: 2.5 }) // after loader completes its lift
      tl.from('.hero-bg', {
        scale: 1.4,
        duration: 2.5,
        ease: 'power4.out',
      })
        .from('.hero-line > span', {
          yPercent: 110,
          duration: 1.4,
          ease: 'power4.out',
          stagger: 0.1,
        }, '-=1.8')
        .from('.hero-meta > *', { y: 30, autoAlpha: 0, duration: 1, stagger: 0.15, ease: 'power3.out' }, '-=0.8')
        .from('.hero-cue', { autoAlpha: 0, duration: 1 }, '-=0.5')

      // Scroll animations
      gsap.to('.hero-bg img', {
        yPercent: 25,
        scale: 1.2,
        ease: 'none',
        scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: true },
      })
      gsap.to('.hero-content', {
        yPercent: -20,
        autoAlpha: 0,
        ease: 'none',
        scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom 40%', scrub: true },
      })

      // Mouse parallax
      const onMove = (e) => {
        const { clientX: x, clientY: y } = e
        // Reduce amplitude to avoid pushing CTA elements outside the hero
        const xPos = (x / window.innerWidth - 0.5) * 20
        const yPos = (y / window.innerHeight - 0.5) * 20
        gsap.to('.hero-content', { x: xPos, y: yPos, duration: 1.5, ease: 'power2.out' })
      }
      window.addEventListener('mousemove', onMove)
      return () => window.removeEventListener('mousemove', onMove)
    },
    { scope: heroRef }
  )

  return (
    <div className="page page-home">
      <Seo title="Morpheme Studios — Architecture & Design" description="An architecture & design practice creating clear, inspirational and personal spaces across cultural, corporate and residential sectors." />
      {/* ---------------- HERO ---------------- */}
      <section ref={heroRef} className="hero">
        <div className="hero-bg">
          <picture>
            <img
              src={HERO_IMG}
              alt="Pynnacles Close Residences — High-end residential architecture in London"
              // eslint-disable-next-line react/no-unknown-property
              fetchpriority="high"
              loading="eager"
              decoding="async"
              onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = '/assets/architecture.jpg' }}
            />
          </picture>
          <div className="hero-scrim" />
        </div>

        <div className="hero-content wrap">
          <p className="label hero-eyebrow">London · Dubai · Karachi</p>
          <h1 className="hero-title">
            <span className="hero-line"><span>Creating the</span></span>
            <span className="hero-line"><span>architecture of</span></span>
            <span className="hero-line"><span className="serif-italic">human wellbeing.</span></span>
          </h1>
          <div className="hero-meta">
            <p className="lead hero-sub">
              Morpheme Studios is an architecture and design practice creating clear,
              inspirational and personal spaces across cultural, corporate and
              residential sectors.
            </p>
            <div className="flex gap-s mt-m hero-btns">
              <Link to="/projects" className="btn btn-fill hero-btn" data-cursor>
                Explore Projects <span className="arrow">→</span>
              </Link>
              <Link to="/studio" className="btn hero-btn" data-cursor>
                The Studio
              </Link>
            </div>
          </div>
        </div>

        <div className="hero-cue">
          <span className="label">Scroll</span>
          <span className="hero-cue-line" />
        </div>
      </section>

      {/* ---------------- MARQUEE ---------------- */}
      <section className="marquee-band">
        <Marquee
          items={['Architecture', 'Interiors', 'Master Planning', 'Arts & Design', 'Hospitality', 'Residential']}
        />
      </section>

      {/* ---------------- FEATURED PROJECTS ---------------- */}
      <section className="section featured">
        <div className="wrap">
          <Reveal variant="stagger" className="section-head between items-end">
            <div>
              <p className="label">Portfolio</p>
              <h2 className="h-lg">Selected Work</h2>
            </div>
            <Link to="/projects" className="link-u section-head-link" data-cursor>View All Projects →</Link>
          </Reveal>
        </div>

        <div className="wrap featured-grid mt-xl">
          {featured.map((p, i) => (
            <Reveal
              key={p.slug}
              variant="fade"
              className="featured-item"
            >
              <ProjectCard project={p} index={i} ratio="ratio-4-3" />
            </Reveal>
          ))}
        </div>
      </section>

      {/* ---------------- SERVICES ---------------- */}
      <ServicesList services={services} />

      {/* ---------------- STATS (dark) ---------------- */}
      <section className="section dark stats">
        <div className="wrap">
          <Reveal variant="stagger" className="stats-grid">
            {stats.map((s) => (
              <div key={s.label} className="stat">
                <Counter value={s.value} suffix={s.suffix} />
                <p className="label">{s.label}</p>
              </div>
            ))}
          </Reveal>
        </div>
      </section>

      {/* ---------------- BLOG TEASER ---------------- */}
      {blogTop.length > 0 && (
      <section className="section blog-teaser">
        <div className="wrap">
          <Reveal className="section-head between items-end">
            <div>
              <p className="label">Blog</p>
              <h2 className="h-lg">Latest Thinking</h2>
            </div>
            <Link to="/blog" className="link-u section-head-link" data-cursor>Read Blog →</Link>
          </Reveal>

          <div className="grid cols-3 keep-2 blog-grid mt-xl">
            {blogTop.map((post) => (
              <Reveal variant="fade" key={post.slug}>
                <Link to={`/blog/${post.slug}`} className="jcard" data-cursor="Read">
                  <div className="media zoom ratio-4-3">
                    <img src={post.image} alt={post.title} loading="lazy" />
                  </div>
                  <div className="jcard-meta">
                    <div className="jcard-top">
                      <span className="label">{post.category}</span>
                      <span className="body-muted jcard-date">{post.date}</span>
                    </div>
                    <h3 className="h-md">{post.title}</h3>
                    <p className="body-muted">{post.excerpt}</p>
                  </div>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>
      )}
    </div>
  )
}

/* ---- Services list with hover-follow image ---- */
function ServicesList({ services = [] }) {
  const ref = useRef(null)
  const previewRef = useRef(null)

  useGSAP(
    () => {
      if (!ref.current || !previewRef.current) return
      const setX = gsap.quickTo(previewRef.current, 'x', { duration: 0.5, ease: 'power3' })
      const setY = gsap.quickTo(previewRef.current, 'y', { duration: 0.5, ease: 'power3' })
      const onMove = (e) => {
        const r = ref.current.getBoundingClientRect()
        setX(e.clientX - r.left)
        setY(e.clientY - r.top)
      }
      ref.current.addEventListener('mousemove', onMove)
      return () => ref.current?.removeEventListener('mousemove', onMove)
    },
    { scope: ref }
  )

  const show = (src) => {
    if (!previewRef.current) return
    previewRef.current.querySelector('img').src = src
    gsap.to(previewRef.current, { autoAlpha: 1, scale: 1, duration: 0.4, ease: 'power3.out' })
  }
  const hide = () => gsap.to(previewRef.current, { autoAlpha: 0, scale: 0.9, duration: 0.3 })

  return (
    <section ref={ref} className="section services">
      <div className="wrap">
        <Reveal className="section-head">
          <p className="label">What we do</p>
          <h2 className="h-lg">Disciplines</h2>
        </Reveal>

        <ul className="services-list">
          {services.map((s) => (
            <li
              key={s.no}
              className="service-row"
              onMouseEnter={() => show(s.image)}
              onMouseLeave={hide}
              data-cursor
            >
              <span className="service-no label">{s.no}</span>
              <h3 className="service-title h-lg">{s.title}</h3>
              <p className="service-blurb body-muted">{s.blurb}</p>
              <span className="service-arrow">→</span>
            </li>
          ))}
        </ul>
      </div>

      <div ref={previewRef} className="services-preview" aria-hidden="true">
        <img src={services[0]?.image || ''} alt="" />
      </div>
    </section>
  )
}

/* ---- Number counter ---- */
function Counter({ value, suffix }) {
  const ref = useRef(null)
  useGSAP(
    () => {
      if (!ref.current) return
      const target = parseInt(value, 10)
      const obj = { v: 0 }
      gsap.to(obj, {
        v: target,
        duration: 1.8,
        ease: 'power2.out',
        scrollTrigger: { trigger: ref.current, start: 'top 85%', once: true },
        onUpdate: () => { if (ref.current) ref.current.firstChild.textContent = Math.round(obj.v) },
      })
    },
    { scope: ref }
  )
  return (
    <p ref={ref} className="stat-value">
      <span>0</span>{suffix}
    </p>
  )
}

import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { gsap } from '../lib/gsap.js'
import { api } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'

const links = [
  { to: '/projects', label: 'Projects' },
  { to: '/studio', label: 'Studio' },
  { to: '/blog', label: 'Blog' },
  { to: '/careers', label: 'Careers' },
  { to: '/contact', label: 'Contact' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [hidden, setHidden] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const lastY = useRef(0)
  const menuRef = useRef(null)
  const location = useLocation()

  const { data: blogList } = useApi(
    () => api.blog({ page_size: 1 }).then((r) => r.results || []),
    [], { fallback: [] }
  )

  const hasBlog = blogList.length > 0
  const dynamicLinks = links.filter((l) => l.to !== '/blog' || hasBlog)

  // Hide on scroll-down, reveal on scroll-up
  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY
      setScrolled(y > 40)
      setHidden(y > lastY.current && y > 300 && !open)
      lastY.current = y
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [open])

  // Close menu on route change
  useEffect(() => { setOpen(false) }, [location.pathname])

  // Animate overlay menu
  useEffect(() => {
    if (!menuRef.current) return
    if (open) {
      document.body.style.overflow = 'hidden'
      const tl = gsap.timeline()
      tl.to(menuRef.current, { clipPath: 'inset(0% 0 0 0)', duration: 0.7, ease: 'power4.inOut' })
        .from('.menu-link', { yPercent: 110, opacity: 0, duration: 0.7, stagger: 0.06, ease: 'power4.out' }, '-=0.25')
        .from('.menu-foot > *', { y: 20, opacity: 0, duration: 0.5, stagger: 0.05 }, '-=0.4')
    } else {
      document.body.style.overflow = ''
      gsap.to(menuRef.current, { clipPath: 'inset(0 0 100% 0)', duration: 0.55, ease: 'power4.inOut' })
    }
  }, [open])

  const isHome = location.pathname === '/'
  const isInternal = !isHome
  const hasBackground = scrolled || isInternal
  const isLogo2 = !isHome || scrolled
  const logoSrc = isLogo2 ? '/logo 2.png' : '/morpheme2.0-1.png'

  return (
    <>
      <header className={`nav ${hidden ? 'nav--hidden' : ''} ${hasBackground ? 'nav--scrolled' : ''}`}>
        <div className="nav-inner wrap">
          <Link to="/" className="nav-logo" data-cursor>
            <img src={logoSrc} alt="Morpheme Studios" className="nav-logo-img" />
          </Link>

          <nav className="nav-links">
            {dynamicLinks.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) => `nav-link link-u ${isActive ? 'is-active' : ''}`}
              >
                {l.label}
              </NavLink>
            ))}
          </nav>

          <button
            className={`nav-toggle ${open ? 'is-open' : ''}`}
            onClick={() => setOpen((o) => !o)}
            aria-label={open ? 'Close menu' : 'Open menu'}
            data-cursor
          >
            <span /><span />
          </button>
        </div>
      </header>

      {/* Full-screen overlay menu (mobile + tablet) */}
      <div ref={menuRef} className="menu" aria-hidden={!open}>
        <div className="menu-inner wrap">
          <nav className="menu-nav">
            <Link to="/" className="menu-link-wrap"><span className="menu-link">Home</span></Link>
            {dynamicLinks.map((l) => (
              <Link key={l.to} to={l.to} className="menu-link-wrap">
                <span className="menu-link">{l.label}</span>
              </Link>
            ))}
          </nav>
          <div className="menu-foot">
            <a href="mailto:connect@morphemestudios.com" className="link-u">connect@morphemestudios.com</a>
            <div className="menu-socials">
              <a href="https://instagram.com/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">Instagram</a>
              <a href="https://linkedin.com/company/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">LinkedIn</a>
              <a href="https://facebook.com/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">Facebook</a>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

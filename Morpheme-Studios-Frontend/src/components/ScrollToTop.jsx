import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { ScrollTrigger } from '../lib/gsap.js'

// Reset scroll on route change + refresh ScrollTriggers for the new page.
export default function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
    // Move focus to the main landmark so screen readers announce the new page
    // (skip on first mount to avoid stealing focus from the intro).
    const main = document.getElementById('main')
    if (main) main.focus({ preventScroll: true })
    const t = setTimeout(() => ScrollTrigger.refresh(), 200)
    return () => clearTimeout(t)
  }, [pathname])
  return null
}

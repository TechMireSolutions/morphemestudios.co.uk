import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { ScrollTrigger } from '../lib/gsap.js'

// Reset scroll on route change + refresh ScrollTriggers for the new page.
export default function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0

    const main = document.getElementById('main')
    if (main) main.focus({ preventScroll: true })

    const t = setTimeout(() => {
      window.scrollTo(0, 0)
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
      ScrollTrigger.refresh()
    }, 100)
    return () => clearTimeout(t)
  }, [pathname])
  return null
}

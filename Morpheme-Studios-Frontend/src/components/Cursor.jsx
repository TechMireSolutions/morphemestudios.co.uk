import { useEffect, useRef } from 'react'
import { gsap } from '../lib/gsap.js'

// Custom trailing cursor; grows + labels on hover targets. Disabled on touch.
export default function Cursor() {
  const dot = useRef(null)
  const ring = useRef(null)
  const label = useRef(null)

  useEffect(() => {
    if (window.matchMedia('(pointer: coarse)').matches) return

    const xToD = gsap.quickTo(dot.current, 'x', { duration: 0.15, ease: 'power3' })
    const yToD = gsap.quickTo(dot.current, 'y', { duration: 0.15, ease: 'power3' })
    const xToR = gsap.quickTo(ring.current, 'x', { duration: 0.45, ease: 'power3' })
    const yToR = gsap.quickTo(ring.current, 'y', { duration: 0.45, ease: 'power3' })

    const move = (e) => {
      xToD(e.clientX); yToD(e.clientY)
      xToR(e.clientX); yToR(e.clientY)
    }

    const over = (e) => {
      const t = e.target.closest('[data-cursor]')
      if (t) {
        ring.current.classList.add('is-active')
        const txt = t.getAttribute('data-cursor')
        if (txt && txt !== 'true') {
          label.current.textContent = txt
          ring.current.classList.add('has-label')
        }
      } else if (e.target.closest('a, button')) {
        ring.current.classList.add('is-hover')
      }
    }
    const out = (e) => {
      if (e.target.closest('[data-cursor]')) {
        ring.current.classList.remove('is-active', 'has-label')
        label.current.textContent = ''
      }
      if (e.target.closest('a, button')) ring.current.classList.remove('is-hover')
    }

    window.addEventListener('mousemove', move)
    document.addEventListener('mouseover', over)
    document.addEventListener('mouseout', out)
    return () => {
      window.removeEventListener('mousemove', move)
      document.removeEventListener('mouseover', over)
      document.removeEventListener('mouseout', out)
    }
  }, [])

  return (
    <>
      <div ref={dot} className="cursor-dot" aria-hidden="true" />
      <div ref={ring} className="cursor-ring" aria-hidden="true">
        <span ref={label} className="cursor-label" />
      </div>
    </>
  )
}

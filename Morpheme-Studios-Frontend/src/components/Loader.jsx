import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'

// First-paint intro: counter + wordmark, then curtain lifts.
export default function Loader({ onDone }) {
  const root = useRef(null)
  const count = useRef(null)
  const word = useRef(null)

  useGSAP(
    () => {
      if (!root.current || !count.current || !word.current) return
      const obj = { v: 0 }
      const tl = gsap.timeline({ onComplete: onDone })
      tl.to(obj, {
        v: 100,
        duration: 1.4,
        ease: 'power2.inOut',
        onUpdate: () => {
          if (count.current) count.current.textContent = String(Math.round(obj.v)).padStart(3, '0')
        },
      })
        .from(word.current.children, {
          yPercent: 110,
          duration: 0.9,
          ease: 'power4.out',
          stagger: 0.08,
        }, 0.1)
        .to(root.current, {
          yPercent: -100,
          duration: 0.9,
          ease: 'power4.inOut',
        }, '+=0.15')
        .set(root.current, { display: 'none' })
    },
    { scope: root }
  )

  return (
    <div ref={root} className="loader">
      <div ref={word} className="loader-word">
        <span>Morpheme</span>
        <span>Studios</span>
      </div>
      <div className="loader-count">
        <span ref={count}>000</span>
      </div>
    </div>
  )
}

import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'

// Seamless looping marquee band. Speed via `duration`.
export default function Marquee({ items = [], duration = 22, className = '' }) {
  const track = useRef(null)

  useGSAP(
    () => {
      const half = track.current.scrollWidth / 2
      gsap.to(track.current, {
        x: -half,
        duration,
        ease: 'none',
        repeat: -1,
      })
    },
    { scope: track }
  )

  const row = [...items, ...items]

  return (
    <div className={`marquee ${className}`}>
      <div ref={track} className="marquee-track">
        {row.map((it, i) => (
          <span key={i} className="marquee-item">
            {it}
            <span className="marquee-dot">✦</span>
          </span>
        ))}
      </div>
    </div>
  )
}

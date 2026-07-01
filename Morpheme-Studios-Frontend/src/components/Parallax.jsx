import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'
import ResilientImage from './ResilientImage.jsx'

// Wraps an image and gives it a gentle parallax drift on scroll.
export default function Parallax({ src, alt, ratio = 'ratio-4-3', amount = 14, className = '', rounded = true }) {
  const wrap = useRef(null)
  const imgRef = useRef(null)

  useGSAP(
    () => {
      if (!wrap.current || !imgRef.current) return
      gsap.fromTo(
        imgRef.current,
        { yPercent: -amount },
        {
          yPercent: amount,
          ease: 'none',
          scrollTrigger: {
            trigger: wrap.current,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
          },
        }
      )
    },
    { scope: wrap }
  )

  return (
    <div
      ref={wrap}
      className={`media ${ratio} ${className}`}
      style={{ borderRadius: rounded ? 'var(--radius)' : 0, overflow: 'hidden' }}
    >
      <ResilientImage
        ref={imgRef}
        src={src}
        alt={alt}
        loading="lazy"
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      />
    </div>
  )
}

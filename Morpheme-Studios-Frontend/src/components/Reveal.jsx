import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'

/**
 * Reveal — scroll-triggered entrance.
 * variant: 'up' | 'fade' | 'clip' | 'stagger'
 * For 'stagger', direct children animate in sequence.
 */
export default function Reveal({
  children,
  as: Tag = 'div',
  variant = 'up',
  delay = 0,
  y = 48,
  stagger = 0.09,
  className = '',
  ...rest
}) {
  const ref = useRef(null)

  useGSAP(
    () => {
      const el = ref.current
      if (!el) return
      const common = {
        scrollTrigger: { trigger: el, start: 'top 85%', once: true },
        ease: 'power3.out',
        duration: 1,
        delay,
      }

      if (variant === 'stagger') {
        const targets = gsap.utils.toArray(el.children)
        if (!targets.length) return
        gsap.from(targets, {
          ...common,
          y,
          autoAlpha: 0,
          stagger,
        })
      } else if (variant === 'fade') {
        gsap.from(el, { ...common, autoAlpha: 0 })
      } else if (variant === 'clip') {
        gsap.from(el, {
          ...common,
          clipPath: 'inset(100% 0 0 0)',
          duration: 1.2,
          ease: 'power4.out',
        })
      } else {
        gsap.from(el, { ...common, y, autoAlpha: 0 })
      }
    },
    { scope: ref }
  )

  return (
    <Tag ref={ref} className={className} {...rest}>
      {children}
    </Tag>
  )
}

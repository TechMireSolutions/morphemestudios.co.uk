import { forwardRef, useEffect, useRef, useState } from 'react'

function useCombinedRefs(...refs) {
  const targetRef = useRef(null)

  useEffect(() => {
    refs.forEach((ref) => {
      if (!ref) return
      if (typeof ref === 'function') {
        ref(targetRef.current)
      } else {
        ref.current = targetRef.current
      }
    })
  }, [refs])

  return targetRef
}

const ResilientImage = forwardRef(function ResilientImage(
  { src, alt, fallback = '/assets/architecture.jpg', ...props },
  ref
) {
  const [currentSrc, setCurrentSrc] = useState(src)
  const innerRef = useRef(null)
  const combinedRef = useCombinedRefs(ref, innerRef)

  useEffect(() => {
    setCurrentSrc(src)
  }, [src])

  useEffect(() => {
    const img = innerRef.current
    if (!img) return

    const handleError = () => {
      if (img.src !== fallback) {
        setCurrentSrc(fallback)
      }
    }

    img.addEventListener('error', handleError)
    return () => img.removeEventListener('error', handleError)
  }, [fallback])

  return (
    <img
      decoding="async"
      {...props}
      ref={combinedRef}
      src={currentSrc}
      alt={alt}
      onError={() => setCurrentSrc(fallback)}
    />
  )
})

export default ResilientImage

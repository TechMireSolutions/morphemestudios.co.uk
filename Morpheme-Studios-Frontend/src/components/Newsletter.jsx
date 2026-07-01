import { useState, useEffect, useRef } from 'react'
import { api, ApiError } from '../lib/api.js'

export default function Newsletter() {
  const [email, setEmail] = useState('')
  const [confirmedEmail, setConfirmedEmail] = useState('')
  const [phase, setPhase] = useState('idle') // idle | sending | confirming | fading | resend | resubmitting
  const [message, setMessage] = useState('')
  const fadeTimer = useRef(null)

  // Auto-fade the confirmation message after 2.5 s, then show resend
  useEffect(() => {
    if (phase === 'confirming') {
      fadeTimer.current = setTimeout(() => {
        setPhase('fading')
        // allow CSS transition to complete before switching to resend
        setTimeout(() => setPhase('resend'), 500)
      }, 2500)
    }
    return () => clearTimeout(fadeTimer.current)
  }, [phase])

  const doSubscribe = async (addr) => {
    try {
      await api.subscribe({ email: addr })
      setConfirmedEmail(addr)
      setMessage('Check your inbox to confirm your subscription.')
      setPhase('confirming')
    } catch (err) {
      const fieldMsg = err instanceof ApiError && err.fields?.email?.[0]
      setMessage(fieldMsg || err?.message || 'Subscription failed. Please try again.')
      setPhase('error')
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    setPhase('sending')
    setMessage('')
    await doSubscribe(email)
    setEmail('')
  }

  const resend = async () => {
    setPhase('resubmitting')
    await doSubscribe(confirmedEmail)
  }

  /* ---- render ---- */
  if (phase === 'confirming' || phase === 'fading') {
    return (
      <div className="footer-col footer-newsletter">
        <p className="label">Newsletter</p>
        <p
          className="body-muted nl-confirm-msg"
          role="status"
          aria-live="polite"
          style={{ opacity: phase === 'fading' ? 0 : 1, transition: 'opacity 0.5s ease' }}
        >
          {message}
        </p>
      </div>
    )
  }

  if (phase === 'resend' || phase === 'resubmitting') {
    return (
      <div className="footer-col footer-newsletter">
        <p className="label">Newsletter</p>
        <p className="body-muted nl-resend-wrap">
          Didn't get it?{' '}
          <button
            className="nl-resend-btn link-u"
            onClick={resend}
            disabled={phase === 'resubmitting'}
            data-cursor
          >
            {phase === 'resubmitting' ? 'Sending…' : 'Resend Email'}
          </button>
        </p>
      </div>
    )
  }

  return (
    <div className="footer-col footer-newsletter">
      <p className="label">Newsletter</p>
      <form className="newsletter-form" onSubmit={submit} noValidate>
        <label htmlFor="nl-email" className="sr-only">Email address</label>
        <input
          id="nl-email"
          type="email"
          required
          placeholder="you@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          aria-invalid={phase === 'error'}
        />
        <button type="submit" className="btn btn-sm" data-cursor disabled={phase === 'sending'}>
          {phase === 'sending' ? 'Subscribing…' : 'Subscribe'}
        </button>
        {phase === 'error' && <span className="field-error" role="alert">{message}</span>}
      </form>
    </div>
  )
}

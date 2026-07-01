import { useState } from 'react'
import Reveal from '../components/Reveal.jsx'
import Seo from '../components/Seo.jsx'
import { api, ApiError } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizeOffice } from '../lib/normalize.js'

export default function Contact() {
  const [sent, setSent] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [fieldErrors, setFieldErrors] = useState({})
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' })
  const { data: offices } = useApi(
    () => api.offices().then((rows) => rows.map(normalizeOffice)), [], { fallback: [] })

  const update = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setFieldErrors({})
    try {
      await api.createLead(form)
      setSent(true)
    } catch (err) {
      if (err instanceof ApiError && err.fields) {
        setFieldErrors(err.fields)
        setError('Please check the highlighted fields.')
      } else {
        setError(err?.message || 'Something went wrong. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page page-contact">
      <Seo title="Contact — Morpheme Studios" description="Tell us about your project, your site or just an idea. London · Ras Al Khaimah · Karachi." />
      <header className="page-head wrap">
        <Reveal><p className="label">Contact</p></Reveal>
        <Reveal variant="fade" delay={0.15}>
          <p className="lead maxw-720 page-head-sub">
            Tell us about your project, your site or just an idea. We read everything
            and reply personally.
          </p>
        </Reveal>
      </header>

      <section className="section-tight">
        <div className="wrap contact-grid">
          {/* Form */}
          <Reveal variant="fade" className="contact-form-wrap">
            {sent ? (
              <div className="contact-sent">
                <h2 className="h-lg">Thank you.</h2>
                <p className="lead body-muted">
                  Your message is on its way to the studio. We’ll be in touch shortly.
                </p>
                <button className="btn" onClick={() => { setSent(false); setForm({ name: '', email: '', phone: '', message: '' }) }} data-cursor>
                  Send another
                </button>
              </div>
            ) : (
              <form className="contact-form" onSubmit={submit} noValidate>
                {error && (
                  <p className="form-error" role="alert">{error}</p>
                )}
                <div className="field">
                  <label htmlFor="contact-name">Full name</label>
                  <input id="contact-name" name="name" required value={form.name} onChange={update('name')} placeholder="Your name" aria-invalid={!!fieldErrors.name} />
                  {fieldErrors.name && <span className="field-error">{fieldErrors.name[0]}</span>}
                </div>
                <div className="field-row">
                  <div className="field">
                    <label htmlFor="contact-email">Email</label>
                    <input id="contact-email" name="email" type="email" required value={form.email} onChange={update('email')} placeholder="you@email.com" aria-invalid={!!fieldErrors.email} />
                    {fieldErrors.email && <span className="field-error">{fieldErrors.email[0]}</span>}
                  </div>
                  <div className="field">
                    <label htmlFor="contact-phone">Phone</label>
                    <input id="contact-phone" name="phone" value={form.phone} onChange={update('phone')} placeholder="Optional" />
                  </div>
                </div>
                <div className="field">
                  <label htmlFor="contact-message">Message</label>
                  <textarea id="contact-message" name="message" required rows={5} value={form.message} onChange={update('message')} placeholder="Tell us about your project…" aria-invalid={!!fieldErrors.message} />
                  {fieldErrors.message && <span className="field-error">{fieldErrors.message[0]}</span>}
                </div>
                <button type="submit" className="btn btn-fill" data-cursor disabled={submitting}>
                  {submitting ? 'Sending…' : <>Send message <span className="arrow">→</span></>}
                </button>
              </form>
            )}
          </Reveal>

          {/* Details */}
          <Reveal variant="up" className="contact-aside">
            <div className="contact-block">
              <p className="label">General enquiries</p>
              <a href="mailto:connect@morphemestudios.com" className="link-u contact-email">
                connect@morphemestudios.com
              </a>
            </div>

            <div className="contact-block">
              <p className="label">Studios</p>
              <ul className="contact-offices">
                {offices.map((o) => (
                  <li key={o.city}>
                    <strong>{o.city}, {o.country}</strong>
                    {o.lines.map((l) => <span key={l} className="body-muted">{l}</span>)}
                    <span className="body-muted">{o.phone}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="contact-block">
              <p className="label">Follow</p>
              <div className="contact-socials">
                <a href="https://instagram.com/morphemestudios" target="_blank" rel="noreferrer" className="link-u">Instagram</a>
                <a href="https://linkedin.com/company/morphemestudios" target="_blank" rel="noreferrer" className="link-u">LinkedIn</a>
                <a href="https://facebook.com/morphemestudios" target="_blank" rel="noreferrer" className="link-u">Facebook</a>
              </div>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  )
}

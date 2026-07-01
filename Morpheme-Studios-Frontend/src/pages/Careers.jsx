import { useRef, useState } from 'react'
import { useGSAP } from '@gsap/react'
import { gsap } from '../lib/gsap.js'
import Reveal from '../components/Reveal.jsx'
import Parallax from '../components/Parallax.jsx'
import Seo from '../components/Seo.jsx'
import { api, ApiError } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'

const CAREERS_IMG = '/assets/architecture.jpg'   // static brand asset (not DB content)

const EMPTY = {
  first_name: '', last_name: '', gender: '', date_of_birth: '', nationality: '',
  country_of_residence: '', email: '', phone: '', home_address: '',
  field_of_expertise: '', applying_for: '', education: '', experience_range: '',
}

export default function Careers() {
  const headerRef = useRef(null)
  const { data: roles } = useApi(() => api.openings(), [], { fallback: [] })
  const [form, setForm] = useState(EMPTY)
  const [files, setFiles] = useState({ cv: null, portfolio: null, cover_letter: null })
  const [terms, setTerms] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState(null)
  const [fieldErrors, setFieldErrors] = useState({})

  const update = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const updateFile = (k) => (e) => setFiles((f) => ({ ...f, [k]: e.target.files[0] || null }))
  const errOf = (k) => fieldErrors[k]?.[0]

  // Clicking a role card pre-selects that role and scrolls to the form
  const selectRole = (title) => {
    setForm((f) => ({ ...f, applying_for: title }))
    const applySection = document.getElementById('apply-section')
    if (applySection) {
      applySection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setFieldErrors({})
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => v !== '' && fd.append(k, v))
      fd.append('terms_accepted', terms ? 'true' : 'false')
      if (files.cv) fd.append('cv', files.cv)
      if (files.portfolio) fd.append('portfolio', files.portfolio)
      if (files.cover_letter) fd.append('cover_letter', files.cover_letter)
      await api.createApplication(fd)
      setSent(true)
    } catch (err) {
      if (err instanceof ApiError && err.fields) {
        setFieldErrors(err.fields)
        setError('Please review the highlighted fields.')
      } else {
        setError(err?.message || 'Submission failed. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  useGSAP(() => {
    if (!headerRef.current) return
    const tl = gsap.timeline()
    tl.from('.page-title', {
      yPercent: 110,
      duration: 1.2,
      ease: 'power4.out',
      stagger: 0.08,
    })
      .from('.page-head .label, .page-head-sub', {
        y: 20,
        autoAlpha: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out'
      }, '-=0.8')
      .from('.careers-image-wrap', {
        scale: 1.1,
        autoAlpha: 0,
        duration: 1.5,
        ease: 'power2.out'
      }, '-=1.2')
  }, { scope: headerRef })

  return (
    <div className="page" ref={headerRef}>
      <Seo title="Careers — Morpheme Studios" description="Join an international, creative architecture & design studio in London, Dubai and Karachi." />
      <header className="page-head wrap">
        <Reveal><p className="label">Careers</p></Reveal>
        <Reveal variant="fade"><h1 className="display page-title">Careers</h1></Reveal>
        <Reveal variant="fade" delay={0.15}>
          <p className="lead maxw-720 page-head-sub">
            Morpheme Studios is always looking for talented architects, interior architects
            and interns to join our team. You will enjoy working in an international,
            creative and experimental studio in London and Dubai.
          </p>
        </Reveal>
      </header>

      <section className="wrap section-tight careers-image-wrap">
        <Reveal variant="clip">
          <Parallax src={CAREERS_IMG} alt="Studio culture" ratio="ratio-16-9" />
        </Reveal>
      </section>

      {/* Intro text */}
      <section className="section">
        <div className="wrap maxw-900">
          <Reveal>
            <p className="lead body-muted">
              Our teams are inclusive and embrace different backgrounds and expertise.
              We are always looking for creative professionals in the AEC industry.
              Please send your CV, motivation letter and portfolio (not more than 10MB)
              via the form below.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Open roles */}
      <section className="section dark">
        <div className="wrap">
          <Reveal className="section-head">
            <p className="label">Open positions</p>
            <h2 className="h-lg">Current openings</h2>
          </Reveal>
          <ul className="roles">
            {(roles || []).map((r) => (
              <Reveal
                variant="up"
                as="li"
                key={r.slug || r.title}
                className="role-row"
                data-cursor="Apply"
                onClick={() => selectRole(r.title)}
                style={{ cursor: 'pointer' }}
              >
                <h3 className="role-title h-md">{r.title}</h3>
                <span className="role-place body-muted">{r.place}</span>
                <span className="label role-type">{r.employment_type}</span>
                <span className="role-arrow">→</span>
              </Reveal>
            ))}
            {roles && roles.length === 0 && (
              <li className="body-muted">No open positions right now — send a speculative application below.</li>
            )}
          </ul>
        </div>
      </section>

      {/* Application Form */}
      <section id="apply-section" className="section application">
        <div className="wrap">
          <div className="contact-grid">
            <Reveal className="contact-aside">
              <div className="contact-block">
                <p className="label">Join the studio</p>
                <h2 className="h-lg">Submit your application</h2>
                <p className="body-muted mt-s">
                  We are always on the lookout for exceptional talent. If you don't see
                  a role that fits but believe you'd be a great addition to Morpheme
                  Studios, please fill out the form.
                </p>
              </div>
              <div className="contact-block">
                <p className="label">Requirements</p>
                <ul className="footer-list mt-s">
                  <li>CV (PDF format)</li>
                  <li>Portfolio (Max 10MB)</li>
                  <li>Cover Letter</li>
                </ul>
              </div>
            </Reveal>

            <Reveal variant="fade" className="contact-main">
              {sent ? (
                <div className="contact-sent" role="status" aria-live="polite">
                  <h2 className="h-lg">Application received.</h2>
                  <p className="lead body-muted">
                    Thank you — your application is with the studio. We review every
                    submission and will be in touch if there’s a fit.
                  </p>
                  <button className="btn" data-cursor onClick={() => { setSent(false); setForm(EMPTY); setFiles({ cv: null, portfolio: null, cover_letter: null }); setTerms(false) }}>
                    Submit another
                  </button>
                </div>
              ) : (
              <form className="contact-form" onSubmit={submit} noValidate>
                {error && <p className="form-error" role="alert">{error}</p>}
                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-first">First Name*</label>
                    <input id="ca-first" type="text" placeholder="John" required value={form.first_name} onChange={update('first_name')} aria-invalid={!!errOf('first_name')} />
                    {errOf('first_name') && <span className="field-error">{errOf('first_name')}</span>}
                  </div>
                  <div className="field">
                    <label htmlFor="ca-last">Last Name*</label>
                    <input id="ca-last" type="text" placeholder="Doe" required value={form.last_name} onChange={update('last_name')} aria-invalid={!!errOf('last_name')} />
                    {errOf('last_name') && <span className="field-error">{errOf('last_name')}</span>}
                  </div>
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-gender">Gender</label>
                    <select id="ca-gender" className="custom-select" value={form.gender} onChange={update('gender')}>
                      <option value="">Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor="ca-dob">Date of Birth</label>
                    <input id="ca-dob" type="date" value={form.date_of_birth} onChange={update('date_of_birth')} />
                  </div>
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-nat">Nationality</label>
                    <input id="ca-nat" type="text" placeholder="Your Nationality" value={form.nationality} onChange={update('nationality')} />
                  </div>
                  <div className="field">
                    <label htmlFor="ca-res">Country of Residence</label>
                    <input id="ca-res" type="text" placeholder="Current Country" value={form.country_of_residence} onChange={update('country_of_residence')} />
                  </div>
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-email">Email*</label>
                    <input id="ca-email" type="email" placeholder="john@example.com" required value={form.email} onChange={update('email')} aria-invalid={!!errOf('email')} />
                    {errOf('email') && <span className="field-error">{errOf('email')}</span>}
                  </div>
                  <div className="field">
                    <label htmlFor="ca-phone">Phone</label>
                    <input id="ca-phone" type="tel" placeholder="+1 234 567 890" value={form.phone} onChange={update('phone')} />
                  </div>
                </div>

                <div className="field">
                  <label htmlFor="ca-addr">Home Address</label>
                  <textarea id="ca-addr" placeholder="Your permanent address" rows="2" value={form.home_address} onChange={update('home_address')} />
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-field">Field of Expertise</label>
                    <input id="ca-field" type="text" placeholder="e.g. Sustainable Design" value={form.field_of_expertise} onChange={update('field_of_expertise')} />
                  </div>
                  <div className="field">
                    <label htmlFor="ca-applying">Applying for*</label>
                    <select id="ca-applying" required className="custom-select" value={form.applying_for} onChange={update('applying_for')}>
                      <option value="">Select Position</option>
                      <option value="Architect Part II">Architect Part II</option>
                      <option value="Architectural assistant Part I">Architectural assistant Part I</option>
                      <option value="Architectural assistant">Architectural assistant</option>
                      <option value="Internship">Internship</option>
                      <option value="Landscape Architect">Landscape Architect</option>
                      <option value="Visualizer">Visualizer</option>
                      <option value="Architectural Technician">Architectural Technician</option>
                      <option value="Interior Designer">Interior Designer</option>
                      <option value="FF&E Manager">FF&E Manager</option>
                    </select>
                  </div>
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-edu">Education</label>
                    <select id="ca-edu" className="custom-select" value={form.education} onChange={update('education')}>
                      <option value="">Select Education Level</option>
                      <option value="Post Graduate">Post Graduate</option>
                      <option value="Post Doctor">Post Doctor</option>
                      <option value="Diploma">Diploma</option>
                      <option value="Technical Education">Technical Education</option>
                      <option value="Others">Others</option>
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor="ca-exp">Years of Experience</label>
                    <select id="ca-exp" className="custom-select" value={form.experience_range} onChange={update('experience_range')}>
                      <option value="">Select Range</option>
                      <option value="1-3">1 - 3 years</option>
                      <option value="4-7">4 - 7 years</option>
                      <option value="7-12">7 - 12 years</option>
                      <option value="12+">12+ years</option>
                    </select>
                  </div>
                </div>

                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ca-cv">CV (PDF)*</label>
                    <input id="ca-cv" type="file" accept="application/pdf" required onChange={updateFile('cv')} aria-invalid={!!errOf('cv')} />
                    {errOf('cv') && <span className="field-error">{errOf('cv')}</span>}
                  </div>
                  <div className="field">
                    <label htmlFor="ca-portfolio">Portfolio (PDF, max 10MB)</label>
                    <input id="ca-portfolio" type="file" accept="application/pdf" onChange={updateFile('portfolio')} />
                  </div>
                </div>

                <div className="field">
                  <label htmlFor="ca-cover">Cover Letter (PDF)</label>
                  <input id="ca-cover" type="file" accept="application/pdf" onChange={updateFile('cover_letter')} />
                </div>

                <div className="field-checkbox">
                  <input type="checkbox" id="terms" required className="checkbox" checked={terms} onChange={(e) => setTerms(e.target.checked)} aria-invalid={!!errOf('terms_accepted')} />
                  <label htmlFor="terms" className="label-ink" style={{ letterSpacing: '0.05em', textTransform: 'none' }}>
                    I agree to the Terms of Use*
                  </label>
                </div>
                {errOf('terms_accepted') && <span className="field-error">{errOf('terms_accepted')}</span>}

                <button type="submit" className="btn btn-fill mt-m" data-cursor disabled={submitting}>
                  {submitting ? 'Submitting…' : <>Submit Application <span className="arrow">→</span></>}
                </button>
              </form>
              )}
            </Reveal>
          </div>
        </div>
      </section>
    </div>
  )
}

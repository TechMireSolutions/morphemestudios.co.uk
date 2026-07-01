import { Link } from 'react-router-dom'
import Newsletter from './Newsletter.jsx'
import { api } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizeOffice } from '../lib/normalize.js'

export default function Footer() {
  const { data: offices } = useApi(
    () => api.offices().then((rows) => rows.map(normalizeOffice)), [], { fallback: [] })
  return (
    <footer className="footer dark">
      <div className="wrap">
        <div className="footer-grid">
          <div className="footer-col footer-brand">
            <Link to="/" className="footer-logo">
              <img src="/morpheme2.0-1.png" alt="Morpheme Studios" className="footer-logo-img" />
            </Link>
            <p className="body-muted footer-tag">
              An architecture &amp; design practice creating clear, inspirational
              and personal spaces across cultural, corporate and residential
              sectors.
            </p>
            <a href="mailto:connect@morphemestudios.com" className="link-u footer-email">
              connect@morphemestudios.com
            </a>
          </div>

          <div className="footer-col">
            <p className="label">Menu</p>
            <ul className="footer-list">
              <li><Link to="/projects" className="link-u">Projects</Link></li>
              <li><Link to="/studio" className="link-u">Studio</Link></li>
              <li><Link to="/blog" className="link-u">Blog</Link></li>
              <li><Link to="/careers" className="link-u">Careers</Link></li>
              <li><Link to="/contact" className="link-u">Contact</Link></li>
            </ul>
          </div>

          <div className="footer-col">
            <p className="label">Offices</p>
            <ul className="footer-list footer-offices">
              {offices.map((o) => (
                <li key={o.city}>
                  <strong>{o.city}</strong>
                  <span className="body-muted">{o.lines.join(', ')}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="footer-col">
            <p className="label">Follow</p>
            <ul className="footer-list">
              <li><a href="https://instagram.com/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">Instagram</a></li>
              <li><a href="https://linkedin.com/company/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">LinkedIn</a></li>
              <li><a href="https://facebook.com/morphemestudios" target="_blank" rel="noopener noreferrer" className="link-u">Facebook</a></li>
            </ul>
          </div>

          <Newsletter />
        </div>

        <div className="divider" />

        <div className="footer-bottom">
          <span className="body-muted">© {new Date().getFullYear()} Morpheme Studios. All rights reserved.</span>
          <div className="footer-legal">
            <Link to="/terms" className="body-muted link-u">Terms of Use</Link>
            <a href="https://www.legislation.gov.uk/ukpga/2018/12/contents/enacted" target="_blank" rel="noopener noreferrer" className="body-muted link-u">Data Protection Act</a>
          </div>
        </div>
      </div>
    </footer>
  )
}

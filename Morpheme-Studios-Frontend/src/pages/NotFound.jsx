import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="page notfound">
      <div className="wrap notfound-inner">
        <p className="label">Error 404</p>
        <p className="lead body-muted">This page doesn’t exist — or has been redesigned away.</p>
        <Link to="/" className="btn" data-cursor>Back home <span className="arrow">→</span></Link>
      </div>
    </div>
  )
}

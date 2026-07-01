import { Link } from 'react-router-dom'

export default function ProjectCard({ project, index, ratio = 'ratio-4-3' }) {
  return (
    <Link
      to={`/projects/${project.slug}`}
      className="pcard"
      data-cursor="View"
    >
      <div className={`media zoom ${ratio}`}>
        <img src={project.cover} alt={project.title} loading="lazy" />
        {index != null && <span className="pcard-index">{String(index + 1).padStart(2, '0')}</span>}
      </div>
      <div className="pcard-meta">
        <div className="pcard-row">
          <h3 className="h-md">{project.title}</h3>
          <span className="pcard-year">{project.year}</span>
        </div>
        <div className="pcard-row">
          <span className="body-muted">{project.location}</span>
          <span className="label">{project.type}</span>
        </div>
      </div>
    </Link>
  )
}

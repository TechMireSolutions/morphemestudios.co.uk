import { useParams, Link, Navigate } from 'react-router-dom'
import Reveal from '../components/Reveal.jsx'
import Seo from '../components/Seo.jsx'
import { api } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { normalizePost } from '../lib/normalize.js'

export default function BlogDetail() {
  const { slug } = useParams()
  const { data: post, loading } = useApi(
    () => api.post(slug).then(normalizePost),
    [slug],
    { fallback: null }
  )

  if (loading && !post) return <div className="page-loader" />
  if (!post) return <Navigate to="/blog" replace />

  return (
    <article className="page page-article">
      <Seo title={`${post.title} — Morpheme Studios`} description={post.excerpt} image={post.cover} />
      <header className="page-head wrap maxw-900">
        <Reveal>
          <div className="jcard-top">
            <span className="label">{post.category}</span>
            {post.date && <span className="body-muted jcard-date">{post.date}</span>}
          </div>
        </Reveal>
        <Reveal variant="fade" delay={0.1}>
          <h1 className="h-xl">{post.title}</h1>
        </Reveal>
        {post.author && (
          <Reveal variant="fade" delay={0.15}>
            <p className="body-muted">
              By {post.author}{post.readingMinutes ? ` · ${post.readingMinutes} min read` : ''}
            </p>
          </Reveal>
        )}
      </header>

      {post.cover && (
        <section className="wrap section-tight">
          <Reveal variant="clip">
            <div className="media ratio-16-9">
              <img src={post.cover} alt={post.title} />
            </div>
          </Reveal>
        </section>
      )}

      <section className="section">
        <div className="wrap maxw-720 article-body">
          {post.excerpt && <p className="lead">{post.excerpt}</p>}
          {post.body ? (
            // Body is sanitised server-side (nh3) before storage.
            <div className="rich-text" dangerouslySetInnerHTML={{ __html: post.body }} />
          ) : (
            <p className="body-muted">Full article coming soon.</p>
          )}
          <p className="mt-l">
            <Link to="/blog" className="link-u">← Back to all articles</Link>
          </p>
        </div>
      </section>
    </article>
  )
}

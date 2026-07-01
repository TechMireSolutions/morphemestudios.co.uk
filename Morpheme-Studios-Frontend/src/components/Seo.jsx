import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { api } from '../lib/api.js'

// Lightweight document-head manager. Sets title/description/canonical/OG/Twitter
// and injects JSON-LD, using static props as immediate defaults and the backend
// /seo/meta endpoint as the editor-controlled source of truth.
//
// NOTE: this runs client-side. For crawler-grade SEO the build should adopt
// `vite-react-ssg` prerendering (plan §9/§10) so this <head> is baked into the
// static HTML; the same data source is reused at that point.

function setMeta(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setLink(rel, href) {
  if (!href) return
  let el = document.head.querySelector(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

function setJsonLd(data) {
  const id = 'ld-route'
  document.getElementById(id)?.remove()
  if (!data) return
  const s = document.createElement('script')
  s.type = 'application/ld+json'
  s.id = id
  s.textContent = JSON.stringify(data)
  document.head.appendChild(s)
}

export default function Seo({ title, description, image }) {
  const { pathname } = useLocation()

  // Apply static defaults immediately.
  useEffect(() => {
    if (title) document.title = title
    setMeta('name', 'description', description)
    setMeta('property', 'og:title', title)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:type', 'website')
    setMeta('name', 'twitter:card', 'summary_large_image')
    if (image) {
      setMeta('property', 'og:image', image)
      setMeta('name', 'twitter:image', image)
    }
  }, [title, description, image])

  // Override from the API (editor-managed meta + JSON-LD) per route.
  useEffect(() => {
    let alive = true
    api
      .seoMeta(pathname)
      .then((m) => {
        if (!alive || !m) return
        if (m.title) document.title = m.title
        setMeta('name', 'description', m.description)
        setLink('canonical', m.canonical)
        setMeta('name', 'robots', m.robots)
        setMeta('property', 'og:title', m.og?.title)
        setMeta('property', 'og:description', m.og?.description)
        if (m.og?.image) setMeta('property', 'og:image', m.og.image)
        if (m.twitter_card) setMeta('name', 'twitter:card', m.twitter_card)
        setJsonLd(m.jsonld)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [pathname])

  return null
}

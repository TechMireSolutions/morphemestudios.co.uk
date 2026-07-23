// Map backend (DRF) payloads onto the shape the existing components already
// consume, so wiring the API needs no component rewrites.
import { absMedia } from './api.js'

const PLACEHOLDER = '/placeholder.svg'

export function normalizeProject(p) {
  if (!p) return null
  const gallery = Array.isArray(p.gallery)
    ? p.gallery
        .map((g) => {
          if (typeof g === 'string') return { src: absMedia(g), caption: '' }
          const src = absMedia(g?.media?.file || g?.src || g?.file)
          return src ? { src, caption: g?.caption || '' } : null
        })
        .filter(Boolean)
    : []
  const cover = absMedia(p.cover?.file) || PLACEHOLDER
  return {
    slug: p.slug,
    title: p.title,
    location: p.location || '',
    year: p.year ?? '',
    category: p.category || 'all',
    type: p.type || '',
    status: p.status_label || '',
    excerpt: p.excerpt || '',
    description: p.description || '',
    services: Array.isArray(p.services) ? p.services : [],
    cover,
    gallery: gallery.length ? gallery : [{ src: cover, caption: '' }],
  }
}

export function normalizePost(p) {
  if (!p) return null
  const cover = absMedia(p.cover?.file) || PLACEHOLDER
  return {
    slug: p.slug,
    title: p.title,
    excerpt: p.excerpt || '',
    body: p.body || '',
    category: p.category || '',
    tags: p.tags || [],
    author: p.author || '',
    cover,
    image: cover,
    date: p.published_at ? new Date(p.published_at).toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' }) : '',
    readingMinutes: p.reading_minutes ?? null,
  }
}

export function normalizeOffice(o) {
  if (!o) return null
  return {
    city: o.city,
    country: o.country || '',
    lines: o.address_lines || [],   // backend field is address_lines; FE uses `lines`
    phone: o.phone || '',
    email: o.email || '',
  }
}

export function normalizeTeamMember(m) {
  if (!m) return null
  return {
    name: m.name,
    role: m.role || '',
    note: m.bio || '',
    image: absMedia(m.photo?.file) || '/assets/team-placeholder.svg',
  }
}

// Central API client for the Morpheme Studios backend (Django + DRF).
// Base URL is required via the VITE_API_URL environment variable.
// Set it in .env (local dev) or in your deployment environment (production).

if (!import.meta.env.VITE_API_URL) {
  console.error('[api] VITE_API_URL is not set. Create a .env file with VITE_API_URL=http://localhost:8000')
}

export const API_ORIGIN = import.meta.env.VITE_API_URL
const BASE = API_ORIGIN + '/api/v1'

// Absolutize a possibly-relative /media/ path (settings images bypass the serializer).
export const absMedia = (u) => (u && u.startsWith('/') ? API_ORIGIN + u : u)

export class ApiError extends Error {
  constructor(message, { status, fields } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fields = fields || null
  }
}

async function parse(res) {
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    const err = data?.error || {}
    throw new ApiError(err.message || `Request failed (${res.status})`, {
      status: res.status,
      fields: err.fields,
    })
  }
  return data
}

// JSON GET/POST
export async function get(path, params) {
  const url = new URL(BASE + path)
  if (params) Object.entries(params).forEach(([k, v]) => v != null && v !== '' && url.searchParams.set(k, v))
  return parse(await fetch(url, { headers: { Accept: 'application/json' } }))
}

export async function postJSON(path, body) {
  return parse(
    await fetch(BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
    })
  )
}

// multipart POST (file uploads) — do NOT set Content-Type; the browser sets the boundary.
export async function postForm(path, formData) {
  return parse(await fetch(BASE + path, { method: 'POST', body: formData }))
}

// --- Typed endpoint helpers ---
export const api = {
  projects: (params) => get('/projects', params),
  project: (slug) => get(`/projects/${slug}`),
  projectCategories: () => get('/projects/categories'),
  blog: (params) => get('/blog', params),
  post: (slug) => get(`/blog/${slug}`),
  team: () => get('/team'),
  testimonials: () => get('/testimonials'),
  openings: () => get('/careers/openings'),
  offices: () => get('/offices'),
  settings: () => get('/settings'),
  seoMeta: (path) => get('/seo/meta', { path }),
  createLead: (body) => postJSON('/leads', body),
  subscribe: (body) => postJSON('/newsletter/subscribe', body),
  createApplication: (formData) => postForm('/careers/applications', formData),
}

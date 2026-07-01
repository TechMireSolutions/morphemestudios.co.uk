import { useEffect, useState } from 'react'

// Generic data hook: useApi(() => api.projects(), [deps]).
// Returns { data, loading, error }. `fallback` keeps the UI populated if the
// API is unreachable (e.g. local dev without the backend running).
export function useApi(fetcher, deps = [], { fallback = null } = {}) {
  const [state, setState] = useState({ data: fallback, loading: true, error: null })

  useEffect(() => {
    let alive = true
    setState((s) => ({ ...s, loading: true, error: null }))
    Promise.resolve()
      .then(fetcher)
      .then((data) => alive && setState({ data, loading: false, error: null }))
      .catch((error) => alive && setState({ data: fallback, loading: false, error }))
    return () => {
      alive = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}

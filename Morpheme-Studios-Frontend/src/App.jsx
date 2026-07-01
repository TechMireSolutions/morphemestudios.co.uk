import { useEffect, useState, lazy, Suspense } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import Navbar from './components/Navbar.jsx'
import Footer from './components/Footer.jsx'
import Cursor from './components/Cursor.jsx'
import Loader from './components/Loader.jsx'
import ScrollToTop from './components/ScrollToTop.jsx'

// Critical View
import Home from './pages/Home.jsx'

// Non-critical Views (Lazy Loaded)
const Studio = lazy(() => import('./pages/Studio.jsx'))
const Projects = lazy(() => import('./pages/Projects.jsx'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail.jsx'))
const Blog = lazy(() => import('./pages/Blog.jsx'))
const BlogDetail = lazy(() => import('./pages/BlogDetail.jsx'))
const Careers = lazy(() => import('./pages/Careers.jsx'))
const Contact = lazy(() => import('./pages/Contact.jsx'))
const Terms = lazy(() => import('./pages/Terms.jsx'))
const NotFound = lazy(() => import('./pages/NotFound.jsx'))

export function Layout() {
  const location = useLocation()
  const [intro, setIntro] = useState(true)

  // Safety fallback to hide loader even if GSAP fails
  useEffect(() => {
    const t = setTimeout(() => setIntro(false), 5000)
    return () => clearTimeout(t)
  }, [])

  return (
    <>
      {intro && <Loader onDone={() => setIntro(false)} />}
      <a href="#main" className="skip-link">Skip to content</a>
      <Cursor />
      <ScrollToTop />
      <Navbar />
      <main id="main" tabIndex={-1}>
        <Suspense fallback={<div className="page-loader" />}>
          <Outlet key={location.pathname} />
        </Suspense>
      </main>
      <Footer hideCTA={['/blog', '/careers', '/contact', '/terms'].includes(location.pathname)} />
    </>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const routes = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'studio', element: <Studio /> },
      { path: 'projects', element: <Projects /> },
      { path: 'projects/:slug', element: <ProjectDetail /> },
      { path: 'blog', element: <Blog /> },
      { path: 'blog/:slug', element: <BlogDetail /> },
      { path: 'careers', element: <Careers /> },
      { path: 'contact', element: <Contact /> },
      { path: 'terms', element: <Terms /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]


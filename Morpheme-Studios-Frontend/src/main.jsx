import { ViteReactSSG } from 'vite-react-ssg'
import { routes } from './App.jsx'
import './styles/global.css'
import './styles/components.css'
import './styles/pages.css'

export const createRoot = ViteReactSSG(
  { routes, base: '/' }
)

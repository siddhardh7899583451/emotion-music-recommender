import { Routes, Route, NavLink } from 'react-router-dom'
import {
  Home, Camera, Mic, Type, Layers, Music, Search, Heart,
  BarChart3, Info, Settings, LogIn, ListMusic, Sun, Moon
} from 'lucide-react'
import { useAuth } from './context/AuthContext'
import HomePage from './pages/HomePage'
import FacePage from './pages/FacePage'
import AudioPage from './pages/AudioPage'
import TextPage from './pages/TextPage'
import MultimodalPage from './pages/MultimodalPage'
import MusicPage from './pages/MusicPage'
import SearchPage from './pages/SearchPage'
import AnalyticsPage from './pages/AnalyticsPage'
import AboutPage from './pages/AboutPage'
import LoginPage from './pages/LoginPage'
import FavouritesPage from './pages/FavouritesPage'
import PlaylistsPage from './pages/PlaylistsPage'
import SettingsPage from './pages/SettingsPage'

const links = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/face', icon: Camera, label: 'Face Emotion' },
  { to: '/audio', icon: Mic, label: 'Audio Emotion' },
  { to: '/text', icon: Type, label: 'Text Emotion' },
  { to: '/multimodal', icon: Layers, label: 'Multimodal' },
  { to: '/music', icon: Music, label: 'Recommendations' },
  { to: '/search', icon: Search, label: 'Search Music' },
  { to: '/favourites', icon: Heart, label: 'Favourites' },
  { to: '/playlists', icon: ListMusic, label: 'Playlists' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
  { to: '/about', icon: Info, label: 'About' },
]

export default function App() {
  const { isAuth, user, theme, toggleTheme, logout } = useAuth()

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="logo">
          <Music size={22} color="#7c5cfc" />
          EmotionMusic
        </div>
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
        <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          <button className="nav-link" style={{ width: '100%', background: 'transparent', border: 'none' }} onClick={toggleTheme}>
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </button>
          {isAuth ? (
            <button className="nav-link" style={{ width: '100%', background: 'transparent', border: 'none' }} onClick={logout}>
              <LogIn size={18} />
              Logout ({user?.username})
            </button>
          ) : (
            <NavLink to="/login" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
              <LogIn size={18} /> Login
            </NavLink>
          )}
        </div>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/face" element={<FacePage />} />
          <Route path="/audio" element={<AudioPage />} />
          <Route path="/text" element={<TextPage />} />
          <Route path="/multimodal" element={<MultimodalPage />} />
          <Route path="/music" element={<MusicPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/favourites" element={<FavouritesPage />} />
          <Route path="/playlists" element={<PlaylistsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
    </div>
  )
}

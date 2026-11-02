import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('emr_token') || '')
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('emr_user') || 'null') } catch { return null }
  })
  const [theme, setTheme] = useState(() => localStorage.getItem('emr_theme') || 'dark')

  useEffect(() => {
    if (token) {
      api.defaults.headers.common.Authorization = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common.Authorization
    }
  }, [token])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('emr_theme', theme)
  }, [theme])

  const login = (tokenValue, userObj) => {
    setToken(tokenValue)
    setUser(userObj)
    localStorage.setItem('emr_token', tokenValue)
    localStorage.setItem('emr_user', JSON.stringify(userObj))
    api.defaults.headers.common.Authorization = `Bearer ${tokenValue}`
  }

  const logout = () => {
    setToken('')
    setUser(null)
    localStorage.removeItem('emr_token')
    localStorage.removeItem('emr_user')
    delete api.defaults.headers.common.Authorization
  }

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  const value = useMemo(
    () => ({ token, user, isAuth: !!token, login, logout, theme, toggleTheme, setTheme }),
    [token, user, theme]
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

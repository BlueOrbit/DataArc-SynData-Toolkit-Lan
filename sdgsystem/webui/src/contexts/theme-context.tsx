import { ConfigProvider, type ThemeConfig } from 'antd'
import enUS from 'antd/locale/en_US'
import type React from 'react'
import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { darkTheme, lightTheme } from '../config/theme'

type ThemeMode = 'light' | 'dark' | 'auto'

interface ThemeContextValue {
  mode: ThemeMode
  setMode: (mode: ThemeMode) => void
  isDark: boolean
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

const THEME_STORAGE_KEY = 'app-theme-mode'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null
    return stored || 'light'
  })

  const [systemPrefersDark, setSystemPrefersDark] = useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches,
  )

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => setSystemPrefersDark(e.matches)

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  const isDark = mode === 'dark' || (mode === 'auto' && systemPrefersDark)

  const setMode = (newMode: ThemeMode) => {
    setModeState(newMode)
    localStorage.setItem(THEME_STORAGE_KEY, newMode)
  }

  const themeConfig: ThemeConfig = useMemo(() => {
    return isDark ? darkTheme : lightTheme
  }, [isDark])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
    document.documentElement.style.colorScheme = isDark ? 'dark' : 'light'
  }, [isDark])

  const value: ThemeContextValue = {
    mode,
    setMode,
    isDark,
  }

  return (
    <ThemeContext.Provider value={value}>
      <ConfigProvider theme={themeConfig} locale={enUS}>
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

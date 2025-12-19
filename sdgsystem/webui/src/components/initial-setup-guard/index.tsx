import type { ReactNode } from 'react'

interface InitialSetupGuardProps {
  children: ReactNode
}

export default function InitialSetupGuard({ children }: InitialSetupGuardProps) {
  return <>{children}</>
}

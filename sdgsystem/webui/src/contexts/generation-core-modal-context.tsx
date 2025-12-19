import { createContext, type ReactNode, useContext, useState } from 'react'

interface GenerationCoreModalContextType {
  isOpen: boolean
  openModal: () => void
  closeModal: () => void
}

const GenerationCoreModalContext = createContext<GenerationCoreModalContextType | undefined>(
  undefined,
)

export function GenerationCoreModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  const openModal = () => setIsOpen(true)
  const closeModal = () => setIsOpen(false)

  return (
    <GenerationCoreModalContext.Provider value={{ isOpen, openModal, closeModal }}>
      {children}
    </GenerationCoreModalContext.Provider>
  )
}

export function useGenerationCoreModal() {
  const context = useContext(GenerationCoreModalContext)
  if (!context) {
    throw new Error('useGenerationCoreModal must be used within GenerationCoreModalProvider')
  }
  return context
}

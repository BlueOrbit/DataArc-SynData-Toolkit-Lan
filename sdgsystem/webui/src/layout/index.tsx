import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import GenerationCoreModal from '@/components/generation-core-modal'
import {
  GenerationCoreModalProvider,
  useGenerationCoreModal,
} from '@/contexts/generation-core-modal-context'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import Header from './header'

const { Content } = Layout

function MainLayoutContent() {
  const token = useAntdTheme()
  const { isOpen, closeModal } = useGenerationCoreModal()

  return (
    <Layout className="min-h-screen" style={{ background: token.colorBgLayout }}>
      <Header />

      <Content>
        <Outlet />
      </Content>

      <GenerationCoreModal open={isOpen} onCancel={closeModal} />
    </Layout>
  )
}

export default function MainLayout() {
  return (
    <GenerationCoreModalProvider>
      <MainLayoutContent />
    </GenerationCoreModalProvider>
  )
}

import { SettingFilled } from '@ant-design/icons'
import { Button, Layout, Tabs } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import ConfigurationIcon from '@/assets/icon/header-configuration.svg?react'
import GenerateDatasetIcon from '@/assets/icon/header-generate-dataset.svg?react'
import HomeIcon from '@/assets/icon/header-home.svg?react'
import TrainingIcon from '@/assets/icon/header-training.svg?react'
import LogoIcon from '@/assets/icon/logo.svg?react'
import SvgIcon from '@/components/svg-icon'
import { useGenerationCoreModal } from '@/contexts/generation-core-modal-context'
import { useAntdTheme } from '@/hooks/use-antd-theme'

const { Header: AntHeader } = Layout

const NAV_ITEMS = [
  {
    key: '/',
    label: (
      <span className="flex items-center gap-2 px-2">
        <SvgIcon icon={HomeIcon} size={18} />
        Home
      </span>
    ),
  },
  {
    key: '/configuration',
    label: (
      <span className="flex items-center gap-2 px-2">
        <SvgIcon icon={ConfigurationIcon} size={18} />
        Configuration
      </span>
    ),
  },
  {
    key: '/generate',
    label: (
      <span className="flex items-center gap-2 px-2">
        <SvgIcon icon={GenerateDatasetIcon} size={18} />
        Generate Dataset
      </span>
    ),
  },

  {
    key: '/training',
    label: (
      <span className="flex items-center gap-2 px-2">
        <SvgIcon icon={TrainingIcon} size={18} />
        Training
      </span>
    ),
  },
]

export default function Header() {
  const token = useAntdTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const { openModal } = useGenerationCoreModal()

  const activeKey = NAV_ITEMS.find(item => item.key === location.pathname)?.key || '/'

  const handleLogoClick = () => {
    navigate('/')
  }

  const handleNavChange = (key: string) => {
    navigate(key)
  }

  return (
    <AntHeader
      className="flex items-center justify-between border-b px-6"
      style={{
        background: token.colorBgContainer,
        borderColor: token.colorBorderSecondary,
        height: 64,
        paddingInline: 24,
      }}
    >
      <div className="flex h-full items-center gap-8">
        <button
          type="button"
          className="flex cursor-pointer items-center gap-2 border-none bg-transparent p-0 text-left"
          onClick={handleLogoClick}
          onKeyDown={e => e.key === 'Enter' && handleLogoClick()}
        >
          <div className="flex flex-col items-center gap-1 font-bold text-lg leading-tight">
            <SvgIcon icon={LogoIcon} size={128} style={{ height: '26px' }} />
            <div className="text-center font-bold text-[10px]">Synthetic Data Toolkit</div>
          </div>
        </button>

        <div className="ml-4 flex h-full items-center">
          <Tabs
            activeKey={activeKey}
            onChange={handleNavChange}
            items={NAV_ITEMS}
            size="large"
            className="header-button-tabs"
            tabBarStyle={{ marginBottom: 0 }}
          />
        </div>
      </div>

      {location.pathname === '/configuration' && (
        <div>
          <Button
            icon={<SettingFilled />}
            onClick={openModal}
            style={{ paddingBlock: 18, height: 32 }}
          >
            Generation Core
          </Button>
        </div>
      )}
    </AntHeader>
  )
}

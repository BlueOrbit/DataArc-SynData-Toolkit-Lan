import { GithubFilled } from '@ant-design/icons'
import { Button, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'
import GenerateDatasetNowIcon from '@/assets/icon/home-generate-dataset-now.svg?react'
import homePageLogo from '@/assets/icon/hoome-page-logo.svg?react'
import HomeBackgroundImg from '@/assets/images/home-bg.png'
import SvgIcon from '@/components/svg-icon'
import { useAntdTheme } from '@/hooks/use-antd-theme'

const { Paragraph } = Typography

export default function HomePage() {
  const token = useAntdTheme()
  const navigate = useNavigate()

  const handleStartClick = () => {
    navigate('/configuration')
  }

  const handleGithubClick = () => {
    window.open('https://github.com/DataArcTech/DataArc-SynData-Toolkit', '_blank')
  }

  return (
    <div
      className="flex h-[calc(100vh-64px)] flex-col items-center p-8"
      style={{
        background: token.colorBgContainer,
        backgroundImage: `url(${HomeBackgroundImg})`,
        backgroundSize: '960px',
        backgroundPosition: 'center top',
        backgroundRepeat: 'no-repeat',
      }}
    >
      <div className="mb-2 flex items-center justify-center">
        <SvgIcon icon={homePageLogo} size={500} style={{ height: '140px' }} />
      </div>

      <div className="mb-8 text-center">
        <Paragraph
          style={{
            fontSize: 14,
            color: token.colorTextDescription,
            maxWidth: 520,
            margin: '0 auto',
            lineHeight: 1.6,
          }}
        >
          A modular, highly user-friendly synthetic data generation toolkit supporting multi-source,
          multi-language data synthesis.
        </Paragraph>
      </div>

      <div className="flex items-center gap-4">
        <Button
          onClick={handleStartClick}
          variant="outlined"
          color="primary"
          style={{
            height: 40,
            fontSize: 16,
          }}
        >
          Generate Dataset Now
          <SvgIcon icon={GenerateDatasetNowIcon} size={20} />
        </Button>
        <Button
          onClick={handleGithubClick}
          icon={<GithubFilled style={{ fontSize: 16 }} />}
          style={{
            height: 40,
            fontSize: 16,
            paddingInline: 32,
          }}
        >
          Github
        </Button>
      </div>
    </div>
  )
}

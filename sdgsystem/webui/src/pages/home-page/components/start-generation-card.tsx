import { RocketOutlined } from '@ant-design/icons'
import { Typography } from 'antd'
import { useAntdTheme } from '@/hooks/use-antd-theme'

const { Title, Paragraph } = Typography

interface StartGenerationCardProps {
  onStart: () => void
}

export function StartGenerationCard({ onStart }: StartGenerationCardProps) {
  const token = useAntdTheme()

  return (
    <button
      type="button"
      className="group relative cursor-pointer overflow-hidden rounded-lg border p-6 text-center transition-all hover:shadow-md"
      style={{
        borderColor: token.colorBorderSecondary,
        background: token.colorBgContainer,
      }}
      onClick={onStart}
      onKeyDown={e => e.key === 'Enter' && onStart()}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = token.colorPrimary
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = token.colorBorderSecondary
      }}
    >
      <div className="mb-4 text-4xl text-primary transition-transform group-hover:scale-110">
        <RocketOutlined />
      </div>
      <Title level={4}>Start Generation</Title>
      <Paragraph type="secondary">
        Create a new synthetic dataset generation task with customized parameters.
      </Paragraph>
    </button>
  )
}

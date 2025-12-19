import type { CSSProperties } from 'react'

interface SvgIconProps {
  icon: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  size?: number | string
  className?: string
  style?: CSSProperties
  onClick?: () => void
}

export default function SvgIcon({
  icon: Icon,
  size = 24,
  className = '',
  style = {},
  onClick,
}: SvgIconProps) {
  const iconStyle: CSSProperties = {
    width: typeof size === 'number' ? `${size}px` : size,
    height: typeof size === 'number' ? `${size}px` : size,
    display: 'inline-block',
    flexShrink: 0,
    verticalAlign: 'middle',
    lineHeight: 1,
    ...style,
  }

  return <Icon className={className} style={iconStyle} onClick={onClick} />
}

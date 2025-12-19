import 'antd'

declare module 'antd' {
  export interface GlobalToken {
    // 自定义圆角
    borderRadiusCircle?: number

    // 自定义主色背景变体
    colorPrimaryBg?: string
    colorPrimaryBgHover?: string
  }
}

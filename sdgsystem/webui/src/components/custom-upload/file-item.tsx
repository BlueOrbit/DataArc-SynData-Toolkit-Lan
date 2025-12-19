import { CloseCircleFilled, FileTextOutlined, FileWordOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd'
import fileItemErrorIcon from '@/assets/icon/file-item-error.svg?react'
import fileItemLoadingIcon from '@/assets/icon/file-item-loading.svg?react'
import fileItemPdfIcon from '@/assets/icon/file-item-pdf.svg?react'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import SvgIcon from '../svg-icon'

interface FileItemProps {
  file: UploadFile
  onRemove: (file: UploadFile) => void
}

export function FileItem({ file, onRemove }: FileItemProps) {
  const token = useAntdTheme()

  const getFileIcon = () => {
    const fileName = file.name.toLowerCase()

    if (file.status === 'uploading') {
      return (
        <div
          style={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: token.colorPrimaryBg,
            borderRadius: token.borderRadius,
          }}
        >
          <SvgIcon icon={fileItemLoadingIcon} size={36} />
        </div>
      )
    }

    if (file.status === 'error') {
      return (
        <div
          style={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: token.borderRadius,
          }}
        >
          <SvgIcon icon={fileItemErrorIcon} size={36} />
        </div>
      )
    }

    if (fileName.endsWith('.pdf')) {
      return (
        <div
          style={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: token.borderRadius,
          }}
        >
          <SvgIcon icon={fileItemPdfIcon} size={36} />
        </div>
      )
    }
    if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
      return (
        <div
          style={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#e6f4ff',
            borderRadius: token.borderRadius,
          }}
        >
          <FileWordOutlined style={{ fontSize: 24, color: '#2b579a' }} />
        </div>
      )
    }
    return (
      <div
        style={{
          width: 48,
          height: 48,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: token.colorPrimaryBg,
          borderRadius: token.borderRadius,
        }}
      >
        <FileTextOutlined style={{ fontSize: 24, color: token.colorPrimary }} />
      </div>
    )
  }

  const getFileStatus = () => {
    if (file.status === 'uploading') {
      return <span style={{ color: token.colorTextSecondary }}>Uploading...</span>
    }
    if (file.status === 'error') {
      return <span style={{ color: token.colorError }}>Failed</span>
    }
    const size = file.size ? formatFileSize(file.size) : '0KB'
    return <span style={{ color: token.colorTextTertiary }}>{size}</span>
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)}MB`
  }

  return (
    <div
      className="custom-upload-file-item"
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: token.marginSM,
        padding: token.paddingXS,
        border: `1px solid ${token.colorBorderSecondary}`,
        borderRadius: token.borderRadiusLG,
        background: token.colorBgContainer,
        minWidth: 0,
      }}
    >
      <button
        type="button"
        onClick={() => onRemove(file)}
        className="custom-upload-remove-btn"
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          transform: 'translate(50%, -50%)',
          fontSize: 18,
          color: token.colorTextTertiary,
          cursor: 'pointer',
          zIndex: 1,
          border: 'none',
          background: token.colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '50%',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        }}
        aria-label={`Remove ${file.name}`}
      >
        <CloseCircleFilled />
      </button>

      <div style={{ flexShrink: 0 }}>{getFileIcon()}</div>

      <div style={{ flex: 1, minWidth: 0, paddingRight: token.paddingSM }}>
        <div
          style={{
            color: token.colorText,
            fontSize: token.fontSize,
            fontWeight: 500,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {file.name}
        </div>

        <div style={{ fontSize: token.fontSizeSM }}>{getFileStatus()}</div>
      </div>
    </div>
  )
}

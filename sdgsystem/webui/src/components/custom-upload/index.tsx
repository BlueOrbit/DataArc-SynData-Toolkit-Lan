import type { UploadFile, UploadProps } from 'antd'
import { message, Upload } from 'antd'
import { useState } from 'react'
import UploadIcon from '@/assets/icon/upload.svg?react'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import SvgIcon from '../svg-icon'
import { FileItem } from './file-item'

interface CustomUploadProps {
  value?: UploadFile[]
  onChange?: (fileList: UploadFile[]) => void
  maxCount?: number
  accept?: string
  multiple?: boolean
  columns?: number
}

const isFileAccepted = (file: File, accept?: string): boolean => {
  if (!accept) return true

  const fileName = file.name.toLowerCase()
  const fileType = file.type.toLowerCase()

  const acceptList = accept.split(',').map(item => item.trim().toLowerCase())

  return acceptList.some(acceptItem => {
    // 检查文件扩展名 (如 .pdf, .jsonl)
    if (acceptItem.startsWith('.')) {
      return fileName.endsWith(acceptItem)
    }

    // 检查 MIME 类型 (如 image/*, application/pdf)
    if (acceptItem.includes('*')) {
      const [type] = acceptItem.split('/')
      return fileType.startsWith(`${type}/`)
    }

    // 精确匹配 MIME 类型
    return fileType === acceptItem
  })
}

export function CustomUpload({
  value = [],
  onChange,
  maxCount,
  accept,
  multiple = true,
  columns = 2,
}: CustomUploadProps) {
  const token = useAntdTheme()
  const [fileList, setFileList] = useState<UploadFile[]>(value)

  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    const validatedFileList = newFileList.map(file => {
      if (file.status && file.status !== 'uploading') {
        return file
      }

      if (file.originFileObj && !isFileAccepted(file.originFileObj, accept)) {
        const acceptFormats = accept || 'all formats'
        message.error(`"${file.name}" is not an accepted file type. Accepted: ${acceptFormats}`)
        return {
          ...file,
          status: 'error' as const,
          error: new Error(`File type not accepted. Expected: ${acceptFormats}`),
        }
      }

      return {
        ...file,
        status: 'done' as const,
      }
    })

    setFileList(validatedFileList)
    onChange?.(validatedFileList)
  }

  const handleRemove = (file: UploadFile) => {
    const newFileList = fileList.filter(item => item.uid !== file.uid)
    setFileList(newFileList)
    onChange?.(newFileList)
  }

  return (
    <div>
      <Upload
        fileList={fileList}
        onChange={handleChange}
        beforeUpload={() => false}
        maxCount={maxCount}
        accept={accept}
        multiple={multiple}
        showUploadList={false}
        style={{ width: '100%' }}
      >
        <button
          type="button"
          className="custom-upload-dragger"
          style={{
            width: '100%',
            border: `1px dashed ${token.colorPrimary}`,
            borderRadius: token.borderRadiusLG,
            padding: `${token.paddingXL}px`,
            textAlign: 'center',
            cursor: 'pointer',
            background: token.colorBgContainer,
          }}
        >
          <SvgIcon
            icon={UploadIcon}
            size={36}
            style={{
              color: token.colorPrimary,
              marginBottom: token.marginSM,
            }}
          />
          <div style={{ color: token.colorText, fontSize: token.fontSize }}>
            Drag your file(s) or browse
          </div>
        </button>
      </Upload>

      {fileList.length > 0 && (
        <div
          style={{
            marginTop: token.marginLG,
            display: 'grid',
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap: token.margin,
          }}
        >
          {fileList.map(file => (
            <FileItem key={file.uid} file={file} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </div>
  )
}

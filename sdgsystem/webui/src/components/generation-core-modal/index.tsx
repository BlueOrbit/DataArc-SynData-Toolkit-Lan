import { CloseOutlined } from '@ant-design/icons'
import { Button, Modal, message } from 'antd'
import { useEffect, useMemo, useRef, useState } from 'react'
import EvaluationMetricsIcon from '@/assets/icon/evaluation-metrics.svg?react'
import EvaluationMetrics3dIcon from '@/assets/icon/evaluation-metrics-3d.svg?react'
import ExecutionEnvironmentIcon from '@/assets/icon/execution-environment.svg?react'
import ExecutionEnvironment3dIcon from '@/assets/icon/execution-environment-3d.svg?react'
import LLMConfigurationIcon from '@/assets/icon/llm-configuration.svg?react'
import LLMConfiguration3dIcon from '@/assets/icon/llm-configuration-3d.svg?react'

import { useAntdTheme } from '@/hooks/use-antd-theme'
import SvgIcon from '../svg-icon'
import {
  EvaluationMetricsForm,
  type FormRef as EvaluationMetricsFormRef,
} from './evaluation-metrics-form'
import {
  ExecutionEnvironmentForm,
  type FormRef as ExecutionEnvironmentFormRef,
} from './execution-environment-form'
import {
  LLMConfigurationForm,
  type FormRef as LLMConfigurationFormRef,
} from './llm-configuration-form'

interface GenerationCoreModalProps {
  open: boolean
  onCancel: () => void
  initialTab?: TabType
}

type TabType = 'llm-configuration' | 'evaluation-metrics' | 'execution-environment'

export default function GenerationCoreModal({
  open,
  onCancel,
  initialTab = 'llm-configuration',
}: GenerationCoreModalProps) {
  const token = useAntdTheme()
  const [activeTab, setActiveTab] = useState<TabType>(initialTab)

  const llmConfigFormRef = useRef<LLMConfigurationFormRef>(null)
  const evaluationMetricsFormRef = useRef<EvaluationMetricsFormRef>(null)
  const executionEnvironmentFormRef = useRef<ExecutionEnvironmentFormRef>(null)

  useEffect(() => {
    if (open) {
      setActiveTab(initialTab)
    }
  }, [open, initialTab])

  const tabs = useMemo(
    () => [
      {
        key: 'llm-configuration' as TabType,
        label: 'LLM Configuration',
        icon: <SvgIcon icon={LLMConfigurationIcon} size={16} />,
        bigIcon: <SvgIcon icon={LLMConfiguration3dIcon} size={36} />,
      },
      {
        key: 'evaluation-metrics' as TabType,
        label: 'Evaluation Metrics',
        icon: <SvgIcon icon={EvaluationMetricsIcon} size={16} />,
        bigIcon: <SvgIcon icon={EvaluationMetrics3dIcon} size={36} />,
      },
      {
        key: 'execution-environment' as TabType,
        label: 'Execution Environment',
        icon: <SvgIcon icon={ExecutionEnvironmentIcon} size={16} />,
        bigIcon: <SvgIcon icon={ExecutionEnvironment3dIcon} size={36} />,
      },
    ],
    [],
  )

  const getCurrentStepIndex = () => {
    return tabs.findIndex(t => t.key === activeTab)
  }

  const handleSaveStep = async () => {
    try {
      switch (activeTab) {
        case 'llm-configuration':
          await llmConfigFormRef.current?.save()
          break
        case 'evaluation-metrics':
          await evaluationMetricsFormRef.current?.save()
          break
        case 'execution-environment':
          await executionEnvironmentFormRef.current?.save()
          break
      }

      const currentIndex = getCurrentStepIndex()
      if (currentIndex < tabs.length - 1) {
        setActiveTab(tabs[currentIndex + 1].key)
      } else {
        onCancel()
      }
    } catch (_error) {
      message.error('Please fill in all required fields')
    }
  }

  const renderForm = () => {
    switch (activeTab) {
      case 'llm-configuration':
        return <LLMConfigurationForm ref={llmConfigFormRef} open={open} />
      case 'evaluation-metrics':
        return <EvaluationMetricsForm ref={evaluationMetricsFormRef} open={open} />
      case 'execution-environment':
        return <ExecutionEnvironmentForm ref={executionEnvironmentFormRef} open={open} />
      default:
        return null
    }
  }

  const getTabTitle = () => {
    const tab = tabs.find(t => t.key === activeTab)
    return tab?.label || 'Settings'
  }

  return (
    <Modal
      open={open}
      onCancel={onCancel}
      footer={null}
      width={800}
      styles={{
        body: {
          padding: 0,
        },
        container: {
          padding: 0,
          borderRadius: token.borderRadiusLG,
          overflow: 'hidden',
        },
      }}
      closeIcon={null}
    >
      <div className="flex" style={{ minHeight: '600px' }}>
        <div
          className="flex flex-col"
          style={{
            width: '230px',
            background: token.colorPrimaryBg, // 使用主色 5% 透明度的浅色背景
            padding: `${token.paddingLG}px`,
          }}
        >
          <h2
            style={{
              margin: 0,
              marginBottom: token.marginXS,
              fontSize: token.fontSizeHeading5,
              fontWeight: token.fontWeightStrong,
            }}
          >
            Generation Core
          </h2>
          <p
            style={{
              margin: 0,
              fontSize: token.fontSizeSM,
              color: token.colorTextSecondary,
              marginBottom: token.marginLG,
            }}
          >
            Configure Core Services
          </p>

          <div className="mt-4 flex flex-col gap-4">
            {tabs.map(tab => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: token.marginXS,
                  padding: `${token.paddingXS}px ${token.paddingSM}px`,
                  border: activeTab === tab.key ? `1px solid ${token.colorPrimary}` : 'none',
                  background: activeTab === tab.key ? token.colorPrimaryBg : token.colorBgBase,
                  color: activeTab === tab.key ? token.colorPrimary : token.colorText,
                  borderRadius: '9999px', // 圆形圆角
                  fontSize: token.fontSizeSM,
                  fontWeight: activeTab === tab.key ? 600 : 400,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.3s',
                  whiteSpace: 'nowrap',
                }}
                onMouseEnter={e => {
                  if (activeTab !== tab.key) {
                    e.currentTarget.style.background = token.colorPrimaryBgHover
                  }
                }}
                onMouseLeave={e => {
                  if (activeTab !== tab.key) {
                    e.currentTarget.style.background = token.colorBgBase
                  }
                }}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          <div style={{ marginTop: 'auto' }}>
            <button
              type="button"
              onClick={onCancel}
              style={{
                width: '100%',
                padding: `${token.paddingSM}px`,
                border: 'none',
                background: 'transparent',
                fontSize: token.fontSize,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Skip and finish later
            </button>
          </div>
        </div>

        <div className="flex flex-1 flex-col" style={{ position: 'relative' }}>
          <div
            className="flex items-center justify-between"
            style={{
              padding: `${token.paddingLG}px ${token.paddingXL}px`,
              borderBottom: `1px solid ${token.colorFillSecondary}`,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: token.margin }}>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: token.fontSizeHeading5,
                  color: token.colorPrimary,
                }}
              >
                {tabs[getCurrentStepIndex()]?.bigIcon}
              </span>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <span
                  style={{
                    fontSize: token.fontSizeSM,
                    color: token.colorPrimary,
                  }}
                >
                  Step {getCurrentStepIndex() + 1} of {tabs.length}
                </span>
                <h3 style={{ margin: 0, fontSize: token.fontSizeHeading5 }}>{getTabTitle()}</h3>
              </div>
            </div>
            <button
              type="button"
              onClick={onCancel}
              style={{
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                padding: token.paddingXS,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: token.colorTextSecondary,
              }}
              onMouseEnter={e => {
                e.currentTarget.style.color = token.colorText
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color = token.colorTextSecondary
              }}
            >
              <CloseOutlined style={{ fontSize: token.fontSizeLG }} />
            </button>
          </div>

          <div
            className="flex-1"
            style={{
              padding: `${token.paddingLG}px ${token.paddingXL}px`,
              overflowY: 'auto',
            }}
          >
            {renderForm()}
          </div>

          <div
            style={{
              padding: `${token.padding}px ${token.paddingXL}px`,
              borderTop: `1px solid ${token.colorFillSecondary}`,
              display: 'flex',
              justifyContent: 'flex-end',
              gap: token.margin,
            }}
          >
            <Button size="large" onClick={onCancel}>
              Close
            </Button>
            <Button type="primary" size="large" onClick={handleSaveStep}>
              Save Step
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  )
}

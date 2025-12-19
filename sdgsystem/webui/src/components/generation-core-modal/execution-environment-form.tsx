import { Form, Input, InputNumber, message } from 'antd'
import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import { useTaskStore } from '@/store/use-task-store'

export interface FormRef {
  save: () => Promise<void>
}

interface ExecutionEnvironmentFormProps {
  open: boolean
}

export const ExecutionEnvironmentForm = forwardRef<FormRef, ExecutionEnvironmentFormProps>(
  ({ open }, ref) => {
    const [form] = Form.useForm()
    const token = useAntdTheme()
    const { config, setTaskConfig } = useTaskStore()

    useEffect(() => {
      if (open) {
        form.setFieldsValue({
          cudaDevice: config.device,
          parallelProcesses: config.n_workers,
          outputDirectory: config.output_dir,
          batchSize: config.task.batch_size,
        })
      }
    }, [open, config, form])

    const handleValuesChange = (_changedValues: unknown, allValues: Record<string, unknown>) => {
      setTaskConfig({
        device: (allValues.cudaDevice as string) || '',
        n_workers: Number(allValues.parallelProcesses) || 1,
        output_dir: (allValues.outputDirectory as string) || '',
        task: {
          ...config.task,
          batch_size: Number(allValues.batchSize) || 5,
        },
      })
    }

    const handleSave = async () => {
      const values = await form.validateFields()

      setTaskConfig({
        device: values.cudaDevice,
        n_workers: values.parallelProcesses || 1,
        output_dir: values.outputDirectory,
        task: {
          ...config.task,
          batch_size: Number(values.batchSize) || 5,
        },
      })

      message.success('Execution Environment saved successfully')
    }

    useImperativeHandle(ref, () => ({
      save: handleSave,
    }))

    return (
      <div className="flex h-full flex-col">
        <Form
          form={form}
          layout="vertical"
          className="flex-1"
          initialValues={{
            cudaDevice: 'cuda:0',
            parallelProcesses: 1,
            outputDirectory: './output/',
          }}
          onValuesChange={handleValuesChange}
        >
          <Form.Item
            name="cudaDevice"
            label="CUDA Device"
            rules={[{ required: true, message: 'Please enter CUDA Device' }]}
          >
            <Input placeholder="cuda:0" size="large" />
          </Form.Item>

          <Form.Item
            name="parallelProcesses"
            label={
              <>
                Number of Parallel Processes{' '}
                <span style={{ color: token.colorTextTertiary, fontWeight: 'normal' }}>
                  (Optional)
                </span>
              </>
            }
          >
            <Input placeholder="1" size="large" type="number" />
          </Form.Item>

          <Form.Item
            name="outputDirectory"
            label="Output Directory"
            rules={[{ required: true, message: 'Please enter Output Directory' }]}
          >
            <Input placeholder="./output/" size="large" />
          </Form.Item>

          <Form.Item
            name="batchSize"
            label="Batch Size"
            rules={[{ required: true, message: 'Please enter Batch Size' }]}
          >
            <InputNumber placeholder="5" min={1} max={100} size="large" style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </div>
    )
  },
)

ExecutionEnvironmentForm.displayName = 'ExecutionEnvironmentForm'

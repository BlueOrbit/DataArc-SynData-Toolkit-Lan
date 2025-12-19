import { Form, Input, InputNumber, Modal, message, Select } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useTaskStore } from '@/store/use-task-store'

interface TaskConfigModalProps {
  open: boolean
  onCancel: () => void
}

export function TaskConfigModal({ open, onCancel }: TaskConfigModalProps) {
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const { config, setTaskConfig, setIsGenerating } = useTaskStore()

  const handleCreateTask = async () => {
    try {
      const values = await form.validateFields()

      setTaskConfig({
        task: {
          ...config.task,
          name: values.taskName,
          task_instruction: values.taskDescription,
          num_samples: values.dataCount,
        },
        llm: {
          ...config.llm,
          model: values.model,
        },
      })

      setIsGenerating(true)

      onCancel()
      message.success('Configuration saved. Starting generation task...')
      navigate('/generate')
    } catch (_error) {
      // Validation failed, form will show error messages
    }
  }

  return (
    <Modal
      title="Create New Generation Task"
      open={open}
      onOk={handleCreateTask}
      onCancel={onCancel}
      okText="Start Generating"
      cancelText="Cancel"
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        className="mt-6"
        initialValues={{
          dataCount: 10,
          model: 'gpt-4o',
        }}
      >
        <Form.Item
          name="taskName"
          label="Task Name"
          rules={[{ required: true, message: 'Please enter a task name' }]}
        >
          <Input placeholder="e.g., E-commerce Product Reviews" />
        </Form.Item>

        <Form.Item
          name="taskDescription"
          label="Description (Prompt Context)"
          rules={[{ required: true, message: 'Please enter a description for the dataset' }]}
        >
          <Input.TextArea
            rows={4}
            placeholder="Describe the dataset you want to generate. For example: Generate 100 realistic product reviews for a smartphone, including positive and negative sentiment."
          />
        </Form.Item>

        <div className="grid grid-cols-2 gap-4">
          <Form.Item
            name="dataCount"
            label="Sample Count"
            rules={[{ required: true, message: 'Please specify the number of samples' }]}
          >
            <InputNumber min={1} max={1000} className="w-full" />
          </Form.Item>

          <Form.Item
            name="model"
            label="LLM Model"
            rules={[{ required: true, message: 'Please select a model' }]}
          >
            <Select>
              <Select.Option value="gpt-4o">GPT-4o</Select.Option>
              <Select.Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Select.Option>
              <Select.Option value="claude-3-opus">Claude 3 Opus</Select.Option>
            </Select>
          </Form.Item>
        </div>
      </Form>
    </Modal>
  )
}

import { Form, Input, message, Select } from 'antd'
import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { type TaskConfig, useTaskStore } from '@/store/use-task-store'

const MAJORITY_VOTING_OPTIONS = [
  { value: 'exact_match', label: 'Exact Match' },
  { value: 'llm_judge', label: 'LLM Judge' },
  { value: 'semantic_clustering', label: 'Semantic Clustering' },
]

const ANSWER_COMPARISON_OPTIONS = [
  { value: 'exact_match', label: 'Exact Match' },
  { value: 'semantic', label: 'Semantic' },
  { value: 'llm_judge', label: 'LLM Judge' },
]

export interface FormRef {
  save: () => Promise<void>
}

interface EvaluationMetricsFormProps {
  open: boolean
}

export const EvaluationMetricsForm = forwardRef<FormRef, EvaluationMetricsFormProps>(
  ({ open }, ref) => {
    const [form] = Form.useForm()
    const { config, setTaskConfig } = useTaskStore()

    const majorityVotingMethod = Form.useWatch('majorityVotingMethod', form)
    const answerComparisonMethod = Form.useWatch('answerComparisonMethod', form)

    useEffect(() => {
      if (open) {
        form.setFieldsValue({
          majorityVotingMethod: config.postprocess.majority_voting.method,
          answerComparisonMethod: config.evaluation.answer_comparison.method,
          baseModelPath: config.base_model.path || '',
          majorityVotingSemanticModelPath:
            config.postprocess.majority_voting.semantic_clustering?.model_path || '',
          answerComparisonSemanticModelPath:
            config.evaluation.answer_comparison.semantic?.model_path || '',
        })
      }
    }, [open, config, form])

    const handleValuesChange = (_changedValues: unknown, allValues: Record<string, unknown>) => {
      const updates: Partial<TaskConfig> = {}

      if (allValues.majorityVotingMethod !== undefined) {
        updates.postprocess = {
          ...config.postprocess,
          majority_voting: {
            ...config.postprocess.majority_voting,
            method: allValues.majorityVotingMethod as string,
          },
        }
      }

      if (allValues.majorityVotingSemanticModelPath !== undefined) {
        updates.postprocess = {
          ...(updates.postprocess || config.postprocess),
          majority_voting: {
            ...(updates.postprocess?.majority_voting || config.postprocess.majority_voting),
            semantic_clustering: {
              model_path: allValues.majorityVotingSemanticModelPath as string,
            },
          },
        }
      }

      if (allValues.answerComparisonMethod !== undefined) {
        updates.evaluation = {
          ...(updates.evaluation || config.evaluation),
          answer_comparison: {
            ...(updates.evaluation?.answer_comparison || config.evaluation.answer_comparison),
            method: allValues.answerComparisonMethod as string,
          },
        }
      }

      if (allValues.answerComparisonSemanticModelPath !== undefined) {
        updates.evaluation = {
          ...(updates.evaluation || config.evaluation),
          answer_comparison: {
            ...(updates.evaluation?.answer_comparison || config.evaluation.answer_comparison),
            method: (updates.evaluation?.answer_comparison?.method ||
              config.evaluation.answer_comparison.method) as string,
            semantic: {
              model_path: allValues.answerComparisonSemanticModelPath as string,
            },
          },
        }
      }

      if (allValues.baseModelPath !== undefined) {
        updates.base_model = {
          ...config.base_model,
          path: allValues.baseModelPath as string,
        }
      }

      setTaskConfig(updates)
    }

    const handleSave = async () => {
      const values = await form.validateFields()

      setTaskConfig({
        postprocess: {
          ...config.postprocess,
          majority_voting: {
            ...config.postprocess.majority_voting,
            method: values.majorityVotingMethod,
            semantic_clustering: values.majorityVotingSemanticModelPath
              ? {
                  model_path: values.majorityVotingSemanticModelPath,
                }
              : config.postprocess.majority_voting.semantic_clustering,
          },
        },
        evaluation: {
          ...config.evaluation,
          answer_comparison: {
            method: values.answerComparisonMethod,
            semantic: values.answerComparisonSemanticModelPath
              ? {
                  model_path: values.answerComparisonSemanticModelPath,
                }
              : config.evaluation.answer_comparison.semantic,
          },
        },
        base_model: {
          ...config.base_model,
          path: values.baseModelPath || '',
        },
      })

      message.success('Evaluation Metrics saved successfully')
    }

    useImperativeHandle(ref, () => ({
      save: handleSave,
    }))

    return (
      <div className="flex h-full flex-col">
        <Form form={form} layout="vertical" className="flex-1" onValuesChange={handleValuesChange}>
          <Form.Item
            name="majorityVotingMethod"
            label="Majority Voting Method"
            rules={[{ required: true, message: 'Please select Majority Voting Method' }]}
          >
            <Select placeholder="Select method" options={MAJORITY_VOTING_OPTIONS} size="large" />
          </Form.Item>

          {majorityVotingMethod === 'semantic_clustering' && (
            <Form.Item
              name="majorityVotingSemanticModelPath"
              label="Semantic Clustering Model Path"
              rules={[{ required: true, message: 'Please enter Semantic Clustering Model Path' }]}
            >
              <Input placeholder="BAAI/bge-m3" size="large" />
            </Form.Item>
          )}

          <Form.Item
            name="answerComparisonMethod"
            label="Answer Comparison Method"
            rules={[{ required: true, message: 'Please select Answer Comparison Method' }]}
          >
            <Select placeholder="Select method" options={ANSWER_COMPARISON_OPTIONS} size="large" />
          </Form.Item>

          {answerComparisonMethod === 'semantic' && (
            <Form.Item
              name="answerComparisonSemanticModelPath"
              label="Semantic Model Path"
              rules={[{ required: true, message: 'Please enter Semantic Model Path' }]}
            >
              <Input placeholder="BAAI/bge-m3" size="large" />
            </Form.Item>
          )}

          <Form.Item
            name="baseModelPath"
            label="Base Model Path"
            rules={[{ required: true, message: 'Please enter Base Model Path' }]}
          >
            <Input placeholder="Qwen/Qwen2.5-7B" size="large" />
          </Form.Item>
        </Form>
      </div>
    )
  },
)

EvaluationMetricsForm.displayName = 'EvaluationMetricsForm'

import { message } from 'antd'
import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

interface CustomAxiosRequestConfig extends AxiosRequestConfig {
  silent?: boolean
}

class Request {
  private instance: AxiosInstance
  private abortControllerMap: Map<string, AbortController>

  constructor(config: AxiosRequestConfig) {
    this.instance = axios.create(config)
    this.abortControllerMap = new Map()

    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.set('Authorization', `Bearer ${token}`)
        }

        const controller = new AbortController()
        const url = config.url || ''
        config.signal = controller.signal
        this.abortControllerMap.set(url, controller)

        return config
      },
      error => {
        return Promise.reject(error)
      },
    )

    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        const url = response.config.url || ''
        this.abortControllerMap.delete(url)

        if (response.status !== 200) {
          if (!(response.config as CustomAxiosRequestConfig).silent) {
            message.error('Request error, please check server logs')
          }
          return Promise.reject(new Error('Request error, please check server logs'))
        }

        const { data } = response

        if (data.code !== undefined) {
          if (data.code !== 200) {
            if (!(response.config as CustomAxiosRequestConfig).silent) {
              message.error(data.message || 'Request failed')
            }
            return Promise.reject(new Error(data.message || 'Error'))
          }
          return data.data
        }

        return data
      },
      error => {
        if (axios.isCancel(error)) {
        } else {
          if (!(error.config as CustomAxiosRequestConfig)?.silent) {
            message.error('Request error, please check server logs')
          }
        }
        return Promise.reject(error)
      },
    )
  }

  get<T = any>(url: string, config?: CustomAxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: CustomAxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: CustomAxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  delete<T = any>(url: string, config?: CustomAxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }
}

export const request = new Request({
  baseURL: '/api',
  timeout: 10000,
})

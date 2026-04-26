import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://localhost:8000'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    templates: [],
    loading: false,
  }),

  actions: {
    async fetchTasks(filters = {}) {
      this.loading = true
      try {
        const res = await axios.get(`${API}/api/tasks`, { params: filters })
        this.tasks = res.data
      } finally {
        this.loading = false
      }
    },

    async fetchTemplates() {
      const res = await axios.get(`${API}/api/tasks/templates`)
      this.templates = res.data
    },

    async createTemplate(data) {
      const res = await axios.post(`${API}/api/tasks/templates`, data)
      this.templates.unshift(res.data)
      return res.data
    },

    async deleteTemplate(id) {
      await axios.delete(`${API}/api/tasks/templates/${id}`)
      this.templates = this.templates.filter(t => t.id !== id)
    },

    async createTask(data) {
      const res = await axios.post(`${API}/api/tasks`, data)
      this.tasks.unshift(res.data)
      return res.data
    },

    async completeTask(id, comment = '') {
      const res = await axios.post(`${API}/api/tasks/${id}/complete`, {
        completion_comment: comment || null
      })
      const idx = this.tasks.findIndex(t => t.id === id)
      if (idx !== -1) this.tasks[idx] = res.data
      return res.data
    },

    async reopenTask(id) {
      const res = await axios.post(`${API}/api/tasks/${id}/reopen`)
      const idx = this.tasks.findIndex(t => t.id === id)
      if (idx !== -1) this.tasks[idx] = res.data
      return res.data
    },

    async deleteTask(id) {
      await axios.delete(`${API}/api/tasks/${id}`)
      this.tasks = this.tasks.filter(t => t.id !== id)
    }
  }
})

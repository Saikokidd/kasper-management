import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    users: [],
    loading: false,
  }),

  actions: {
    async fetchUsers() {
      const res = await axios.get(`${API}/api/auth/users`)
      this.users = res.data
    },

    async fetchTasks(filters = {}) {
      this.loading = true
      try {
        const res = await axios.get(`${API}/api/tasks`, { params: filters })
        this.tasks = res.data
      } finally {
        this.loading = false
      }
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
      this._replaceTask(res.data)
      return res.data
    },

    async reopenTask(id) {
      const res = await axios.post(`${API}/api/tasks/${id}/reopen`)
      this._replaceTask(res.data)
      return res.data
    },

    async deleteTask(id) {
      await axios.delete(`${API}/api/tasks/${id}`)
      this.tasks = this.tasks.filter(t => t.id !== id)
    },

    _replaceTask(task) {
      const idx = this.tasks.findIndex(t => t.id === task.id)
      if (idx !== -1) this.tasks[idx] = task
    }
  }
})

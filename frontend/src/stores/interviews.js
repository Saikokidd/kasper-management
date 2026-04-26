import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://localhost:8000'

export const useInterviewsStore = defineStore('interviews', {
  state: () => ({
    interviews: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch() {
      this.loading = true
      try {
        const res = await axios.get(`${API}/api/interviews`)
        this.interviews = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/interviews`, data)
      this.interviews.unshift(res.data)
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/interviews/${id}`, data)
      const idx = this.interviews.findIndex(i => i.id === id)
      if (idx !== -1) this.interviews[idx] = res.data
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/interviews/${id}`)
      this.interviews = this.interviews.filter(i => i.id !== id)
    }
  }
})

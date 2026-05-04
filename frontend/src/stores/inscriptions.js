import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useInscriptionsStore = defineStore('inscriptions', {
  state: () => ({
    inscriptions: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch(search = '') {
      this.loading = true
      try {
        const params = search ? { search } : {}
        const res = await axios.get(`${API}/api/inscriptions`, { params })
        this.inscriptions = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/inscriptions`, data)
      this.inscriptions.unshift(res.data)
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/inscriptions/${id}`, data)
      const idx = this.inscriptions.findIndex(i => i.id === id)
      if (idx !== -1) this.inscriptions[idx] = res.data
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/inscriptions/${id}`)
      this.inscriptions = this.inscriptions.filter(i => i.id !== id)
    }
  }
})

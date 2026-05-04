import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useAdsStore = defineStore('ads', {
  state: () => ({
    ads: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch(platform = null) {
      this.loading = true
      this.error = null
      try {
        const params = platform ? { platform } : {}
        const res = await axios.get(`${API}/api/ads`, { params })
        this.ads = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/ads`, data)
      this.ads.unshift(res.data)
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/ads/${id}`, data)
      const idx = this.ads.findIndex(a => a.id === id)
      if (idx !== -1) this.ads[idx] = res.data
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/ads/${id}`)
      this.ads = this.ads.filter(a => a.id !== id)
    }
  }
})

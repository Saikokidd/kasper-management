import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://10.0.0.2:8000'

export const useTiktokStreamsStore = defineStore('tiktokStreams', {
  state: () => ({
    streams: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch() {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`${API}/api/tiktok-streams`)
        this.streams = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/tiktok-streams`, data)
      this.streams.unshift(res.data)
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/tiktok-streams/${id}`, data)
      const idx = this.streams.findIndex(s => s.id === id)
      if (idx !== -1) this.streams[idx] = res.data
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/tiktok-streams/${id}`)
      this.streams = this.streams.filter(s => s.id !== id)
    }
  }
})

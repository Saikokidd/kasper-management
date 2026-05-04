import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useCandidatesStore = defineStore('candidates', {
  state: () => ({
    candidates: [],
    templates: [],
    loading: false,
  }),

  actions: {
    async fetchTemplates() {
      const res = await axios.get(`${API}/api/templates`)
      this.templates = res.data
    },

    async createTemplate(data) {
      const res = await axios.post(`${API}/api/templates`, data)
      this.templates.unshift(res.data)
      return res.data
    },

    async deleteTemplate(id) {
      await axios.delete(`${API}/api/templates/${id}`)
      this.templates = this.templates.filter(t => t.id !== id)
    },

    async fetchCandidates(search = '', template_id = null) {
      this.loading = true
      try {
        const params = {}
        if (search) params.search = search
        if (template_id) params.template_id = template_id
        const res = await axios.get(`${API}/api/candidates`, { params })
        this.candidates = res.data
      } finally {
        this.loading = false
      }
    },

    async createCandidate(data) {
      const res = await axios.post(`${API}/api/candidates`, data)
      this.candidates.unshift(res.data)
      return res.data
    },

    async updateCandidate(id, data) {
      const res = await axios.patch(`${API}/api/candidates/${id}`, data)
      const idx = this.candidates.findIndex(c => c.id === id)
      if (idx !== -1) this.candidates[idx] = res.data
      return res.data
    },

    async removeCandidate(id) {
      await axios.delete(`${API}/api/candidates/${id}`)
      this.candidates = this.candidates.filter(c => c.id !== id)
    }
  }
})

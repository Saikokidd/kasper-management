import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://10.0.0.2:8000'

export const useJobPostsStore = defineStore('jobPosts', {
  state: () => ({
    posts: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch(platform = null) {
      this.loading = true
      this.error = null
      try {
        const params = platform ? { platform } : {}
        const res = await axios.get(`${API}/api/job-posts`, { params })
        this.posts = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/job-posts`, data)
      this.posts.unshift(res.data)
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/job-posts/${id}`, data)
      const idx = this.posts.findIndex(p => p.id === id)
      if (idx !== -1) this.posts[idx] = res.data
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/job-posts/${id}`)
      this.posts = this.posts.filter(p => p.id !== id)
    }
  }
})

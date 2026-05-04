import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useInterviewsStore = defineStore('interviews', {
  state: () => ({
    scheduled: [],
    completed: [],
    loading: false,
    error: null,
  }),

  getters: {
    // Все записи для календаря
    all: (state) => [...state.scheduled, ...state.completed],
  },

  actions: {
    async fetchScheduled() {
      this.loading = true
      try {
        const res = await axios.get(`${API}/api/interviews`, { params: { status: 'scheduled' } })
        this.scheduled = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async fetchCompleted() {
      this.loading = true
      try {
        const res = await axios.get(`${API}/api/interviews`, { params: { status: 'completed' } })
        this.completed = res.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async fetchAll() {
      this.loading = true
      try {
        const [s, c] = await Promise.all([
          axios.get(`${API}/api/interviews`, { params: { status: 'scheduled' } }),
          axios.get(`${API}/api/interviews`, { params: { status: 'completed' } }),
        ])
        this.scheduled = s.data
        this.completed = c.data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const res = await axios.post(`${API}/api/interviews`, data)
      if (res.data.status === 'scheduled') {
        this.scheduled.unshift(res.data)
      } else {
        this.completed.unshift(res.data)
      }
      return res.data
    },

    async update(id, data) {
      const res = await axios.patch(`${API}/api/interviews/${id}`, data)
      this._replaceInLists(id, res.data)
      return res.data
    },

    async complete(id, result) {
      const params = result ? { result } : {}
      const res = await axios.post(`${API}/api/interviews/${id}/complete`, null, { params })
      // Убираем из scheduled, добавляем в completed
      this.scheduled = this.scheduled.filter(i => i.id !== id)
      this.completed.unshift(res.data)
      return res.data
    },

    async uploadPhoto(id, file) {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post(`${API}/api/interviews/${id}/photo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      this._replaceInLists(id, res.data)
      return res.data
    },

    async remove(id) {
      await axios.delete(`${API}/api/interviews/${id}`)
      this.scheduled = this.scheduled.filter(i => i.id !== id)
      this.completed = this.completed.filter(i => i.id !== id)
    },

    _replaceInLists(id, item) {
      const si = this.scheduled.findIndex(i => i.id === id)
      if (si !== -1) this.scheduled[si] = item
      const ci = this.completed.findIndex(i => i.id === id)
      if (ci !== -1) this.completed[ci] = item
    }
  }
})
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 60000,
})

const token = localStorage.getItem('emr_token')
if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`

export async function register(payload) {
  const { data } = await api.post('/auth/register', payload)
  return data
}

export async function login(payload) {
  const { data } = await api.post('/auth/login', payload)
  return data
}

export async function getMe() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function detectFace(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/emotion/face', form)
  return data
}

export async function detectFaceBase64(b64) {
  const form = new FormData()
  form.append('image_base64', b64)
  const { data } = await api.post('/emotion/face', form)
  return data
}

export async function detectAudio(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/emotion/audio', form)
  return data
}

export async function detectText(text) {
  const { data } = await api.post('/emotion/text', { text })
  return data
}

export async function fuseEmotions(payload) {
  const { data } = await api.post('/emotion/multimodal', payload)
  return data
}

export async function recommendMusic(payload) {
  const { data } = await api.post('/music/recommend', payload)
  return data
}

export async function searchMusic(params) {
  const { data } = await api.get('/music/search', { params })
  return data
}

export async function getFilters() {
  const { data } = await api.get('/music/filters')
  return data
}

export async function saveHistory(payload) {
  const { data } = await api.post('/history', payload)
  return data
}

export async function getHistory(params) {
  const { data } = await api.get('/history', { params })
  return data
}

export async function getAnalytics(days = 7) {
  const { data } = await api.get('/history/analytics', { params: { days } })
  return data
}

export async function listFavourites() {
  const { data } = await api.get('/favourites')
  return data
}

export async function addFavourite(songId) {
  const { data } = await api.post('/favourites', { song_id: songId })
  return data
}

export async function removeFavourite(songId) {
  const { data } = await api.delete(`/favourites/${songId}`)
  return data
}

export async function listPlaylists() {
  const { data } = await api.get('/playlists')
  return data
}

export async function createPlaylist(payload) {
  const { data } = await api.post('/playlists', payload)
  return data
}

export async function addSongToPlaylist(playlistId, songId) {
  const { data } = await api.post(`/playlists/${playlistId}/songs`, { song_id: songId })
  return data
}

export async function deletePlaylist(playlistId) {
  const { data } = await api.delete(`/playlists/${playlistId}`)
  return data
}

export async function submitFeedback(payload) {
  const { data } = await api.post('/feedback', payload)
  return data
}

export async function getSettings() {
  const { data } = await api.get('/settings')
  return data
}

export async function updateSettings(payload) {
  const { data } = await api.put('/settings', payload)
  return data
}

export default api

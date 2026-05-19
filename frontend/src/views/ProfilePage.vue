<template>
  <div class="profile-page">
    <header class="profile-header">
      <router-link to="/" class="brand-title">OnlyFans Ruslana</router-link>
      <button class="theme-btn" type="button" @click="toggleTheme" :title="isDark ? 'Светлая тема' : 'Темная тема'">
        {{ isDark ? '☀' : '☾' }}
      </button>
    </header>

    <main class="profile-shell">
      <section class="profile-card" v-if="!loading">
        <div class="avatar-section">
          <button class="avatar-button" type="button" @click="triggerAvatarInput" :disabled="savingAvatar">
            <img v-if="avatarPreview" :src="avatarPreview" alt="Аватар">
            <span v-else>{{ username.charAt(0).toUpperCase() }}</span>
          </button>
          <input
            ref="avatarInput"
            class="hidden-input"
            type="file"
            accept="image/*"
            @change="handleAvatarSelect"
          >
          <div class="avatar-actions">
            <button class="btn primary" type="button" @click="triggerAvatarInput" :disabled="savingAvatar">
              {{ savingAvatar ? 'Загрузка...' : 'Загрузить аватар' }}
            </button>
            <button v-if="avatarPreview && avatarUrl" class="btn subtle" type="button" @click="removeAvatar" :disabled="savingAvatar">
              Убрать
            </button>
          </div>
          <p v-if="avatarError" class="error-msg">{{ avatarError }}</p>
        </div>

        <div class="profile-content">
          <div class="form-section">
            <label>Имя пользователя</label>
            <div v-if="!isEditingName" class="display-row">
              <span class="value">{{ username }}</span>
              <button @click="startEditName" class="btn-edit">Изменить</button>
            </div>
            <div v-else class="edit-row">
              <input
                v-model.trim="editUsername"
                type="text"
                maxlength="50"
                :disabled="savingName"
                placeholder="Введите новое имя"
              >
              <div class="edit-actions">
                <button @click="cancelEditName" :disabled="savingName">Отмена</button>
                <button
                  @click="saveName"
                  :disabled="!isValidUsername || savingName"
                  class="btn-save"
                >
                  {{ savingName ? 'Сохраняем...' : 'Сохранить' }}
                </button>
              </div>
              <p v-if="nameError" class="error-msg">{{ nameError }}</p>
            </div>
          </div>

          <div class="form-section">
            <label>О себе</label>
            <div v-if="!isEditingDesc" class="display-row">
              <span class="value desc-text">{{ description || 'Добавьте описание...' }}</span>
              <button @click="startEditDesc" class="btn-edit">Изменить</button>
            </div>
            <div v-else class="edit-row">
              <textarea
                v-model="editDescription"
                rows="4"
                maxlength="300"
                :disabled="savingDesc"
                placeholder="Расскажите о себе..."
              ></textarea>
              <div class="edit-actions">
                <small>{{ editDescription.length }}/300</small>
                <button @click="cancelEditDesc" :disabled="savingDesc">Отмена</button>
                <button @click="saveDescription" :disabled="savingDesc" class="btn-save">
                  {{ savingDesc ? 'Сохраняем...' : 'Сохранить' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="successMsg" class="success-banner">{{ successMsg }}</div>

          <button @click="$router.push('/')" class="btn-back">На главную</button>
          <button @click="logout" class="btn-logout">Выйти</button>
        </div>
      </section>

      <div v-else class="loader">Загрузка профиля...</div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { profileApi, uploadApi } from '@/api/endpoints'
import { resolveImageUrl } from '@/utils/image'

const authStore = useAuthStore()

const username = ref('')
const description = ref('')
const avatarUrl = ref('')
const avatarPreview = ref('')
const editUsername = ref('')
const editDescription = ref('')

const isEditingName = ref(false)
const isEditingDesc = ref(false)
const savingName = ref(false)
const savingDesc = ref(false)
const savingAvatar = ref(false)
const nameError = ref('')
const avatarError = ref('')
const successMsg = ref('')
const loading = ref(true)
const avatarInput = ref(null)
const isDark = ref(localStorage.getItem('theme') === 'dark')

const isValidUsername = computed(() => editUsername.value.length >= 3)

const applyTheme = () => {
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const applyProfile = (profile) => {
  username.value = profile.username
  description.value = profile.description || ''
  avatarUrl.value = profile.img_url || profile.image_url || ''
  avatarPreview.value = resolveImageUrl(avatarUrl.value)
  editUsername.value = username.value
  editDescription.value = description.value
  authStore.user = profile
  localStorage.setItem('user_info', JSON.stringify(profile))
}

onMounted(async () => {
  applyTheme()
  try {
    const res = await profileApi.getMe()
    applyProfile(res.data)
  } catch (err) {
    console.warn('Failed to load profile, using defaults')
  } finally {
    loading.value = false
  }
})

const triggerAvatarInput = () => {
  avatarInput.value?.click()
}

const handleAvatarSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    avatarError.value = 'Выберите изображение'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    avatarError.value = 'Файл слишком большой, максимум 10 МБ'
    return
  }

  avatarError.value = ''
  savingAvatar.value = true

  try {
    const uploadResponse = await uploadApi.image(file)
    const profileResponse = await profileApi.updateAvatar(uploadResponse.data.image_url)
    applyProfile(profileResponse.data)
    showSuccess('Аватар обновлен')
  } catch (err) {
    avatarError.value = err.response?.data?.detail || err.message || 'Не удалось загрузить аватар'
  } finally {
    savingAvatar.value = false
    if (avatarInput.value) avatarInput.value.value = ''
  }
}

const removeAvatar = async () => {
  savingAvatar.value = true
  avatarError.value = ''
  try {
    const response = await profileApi.updateAvatar('')
    applyProfile(response.data)
    avatarUrl.value = ''
    avatarPreview.value = ''
    showSuccess('Аватар убран')
  } catch (err) {
    avatarError.value = err.response?.data?.detail || 'Не удалось убрать аватар'
  } finally {
    savingAvatar.value = false
  }
}

const startEditName = () => {
  editUsername.value = username.value
  isEditingName.value = true
  nameError.value = ''
  successMsg.value = ''
}

const cancelEditName = () => {
  editUsername.value = username.value
  isEditingName.value = false
  nameError.value = ''
}

const saveName = async () => {
  savingName.value = true
  nameError.value = ''

  try {
    const response = await profileApi.rename(editUsername.value)
    applyProfile(response.data)
    isEditingName.value = false
    showSuccess('Имя изменено')
  } catch (err) {
    nameError.value = err.response?.data?.detail || 'Ошибка при смене имени'
  } finally {
    savingName.value = false
  }
}

const startEditDesc = () => {
  editDescription.value = description.value
  isEditingDesc.value = true
  successMsg.value = ''
}

const cancelEditDesc = () => {
  editDescription.value = description.value
  isEditingDesc.value = false
}

const saveDescription = async () => {
  savingDesc.value = true

  try {
    const response = await profileApi.updateDescription(editDescription.value)
    applyProfile(response.data)
    isEditingDesc.value = false
    showSuccess('Описание обновлено')
  } catch (err) {
    nameError.value = err.response?.data?.detail || 'Ошибка при обновлении описания'
  } finally {
    savingDesc.value = false
  }
}

const logout = () => {
  authStore.logout()
  localStorage.removeItem('user_info')
  window.location.href = '/login'
}

const showSuccess = (msg) => {
  successMsg.value = msg
  setTimeout(() => { successMsg.value = '' }, 3000)
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--primary) 20%, transparent), transparent 30rem),
    var(--bg);
  color: var(--text);
}

.profile-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 2rem;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--border);
}

.brand-title {
  font-weight: 900;
  font-size: 1.35rem;
  color: var(--primary);
  text-decoration: none;
}

.theme-btn {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
}

.profile-shell {
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
}

.profile-card {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 2rem;
  background: var(--surface);
  width: 100%;
  max-width: 820px;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: var(--shadow);
}

.avatar-section {
  text-align: center;
}

.avatar-button {
  width: 144px;
  height: 144px;
  border-radius: 50%;
  border: 2px solid var(--border);
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 3.2rem;
  font-weight: 900;
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
}

.avatar-button img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hidden-input {
  display: none;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  margin-top: 1rem;
}

.btn.subtle {
  background: var(--surface-soft);
  color: var(--text);
}

.form-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section label {
  display: block;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.display-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.value {
  font-size: 1.05rem;
  color: var(--text);
}

.desc-text {
  color: var(--text-muted);
  white-space: pre-wrap;
  overflow-wrap: break-word;
  max-width: 80%;
}

.btn-edit,
.btn-back,
.edit-actions button {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--text);
  padding: 0.5rem 1rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-edit:hover,
.btn-back:hover,
.edit-actions button:hover:not(:disabled) {
  border-color: var(--primary);
  background: var(--primary-soft);
}

.edit-row {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.edit-row input,
.edit-row textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 1rem;
  font-family: inherit;
  box-sizing: border-box;
  color: var(--text);
  background: var(--surface-raised);
}

.edit-row input:focus,
.edit-row textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
}

.edit-actions small {
  margin-right: auto;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.btn-save {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: #ffffff !important;
}

.btn-save:hover:not(:disabled) {
  background: var(--primary-strong) !important;
}

.btn-save:disabled,
.edit-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-msg {
  color: var(--danger);
  background: color-mix(in srgb, var(--danger) 14%, var(--surface));
  padding: 0.65rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
  margin: 0;
}

.success-banner {
  background: color-mix(in srgb, var(--success) 14%, var(--surface));
  color: var(--success);
  padding: 0.75rem;
  border-radius: var(--radius);
  text-align: center;
  margin: 1rem 0;
  font-weight: 800;
}

.btn-back {
  width: 100%;
  margin-top: 1rem;
}

.btn-logout {
  width: 100%;
  margin-top: 0.75rem;
  border: 1px solid var(--danger);
  border-radius: 999px;
  background: color-mix(in srgb, var(--danger) 10%, var(--surface));
  color: var(--danger);
  padding: 0.75rem;
  font-weight: 800;
  cursor: pointer;
}

.btn-logout:hover {
  background: var(--danger);
  color: #ffffff;
}

.loader {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-size: 1.1rem;
}

@media (max-width: 760px) {
  .profile-header {
    padding: 0.9rem 1rem;
  }

  .profile-card {
    grid-template-columns: 1fr;
    padding: 1.25rem;
  }

  .display-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .desc-text {
    max-width: 100%;
  }
}
</style>

<template>
  <div class="catalog-page">
    <header class="catalog-header">
      <router-link to="/" class="brand-title">OnlyFans Ruslana</router-link>
      <div class="header-actions">
        <button class="icon-btn" type="button" @click="toggleTheme" :title="isDark ? 'Светлая тема' : 'Темная тема'">
          {{ isDark ? '☀' : '☾' }}
        </button>
        <router-link to="/" class="btn outline">Лента</router-link>
        <router-link to="/boards" class="btn outline">Доски</router-link>
        <router-link to="/profile" class="btn outline">Профиль</router-link>
      </div>
    </header>

    <main class="catalog-main">
      <div class="catalog-toolbar">
        <div>
          <p class="eyebrow">Каталог</p>
          <h1>Поиск пинов</h1>
        </div>
        <span v-if="meta && query.trim()" class="counter">{{ meta.total }} найдено</span>
      </div>

      <form class="search-row" @submit.prevent="runSearch(1)">
        <input
          v-model="query"
          type="search"
          placeholder="Введите слово из названия или описания"
          maxlength="100"
        >
        <button class="btn primary" type="submit" :disabled="loading || !query.trim()">Искать</button>
      </form>

      <div v-if="loading" class="state">Загрузка...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <div v-else-if="searched && pins.length === 0" class="empty-state">
        <h2>Ничего не найдено</h2>
        <p>Попробуйте другое слово.</p>
      </div>
      <div v-else-if="!searched" class="empty-state">
        <h2>Введите поисковый запрос</h2>
        <p>Каталог ищет совпадения в названии и описании пинов.</p>
      </div>
      <div v-else class="pins-masonry">
        <PinCard
          v-for="pin in pins"
          :key="pin.id"
          :pin="pin"
          @like="handleLike"
          @click="openPinDetail"
        />
      </div>

      <div class="pagination" v-if="meta && meta.pages > 1">
        <button :disabled="!meta.has_prev || loading" @click="runSearch(meta.page - 1)">← Назад</button>
        <span>Страница {{ meta.page }} из {{ meta.pages }}</span>
        <button :disabled="!meta.has_next || loading" @click="runSearch(meta.page + 1)">Вперед →</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { pinsApi } from '@/api/endpoints'
import PinCard from '@/components/PinCard.vue'

const router = useRouter()
const authStore = useAuthStore()

const query = ref('')
const pins = ref([])
const meta = ref(null)
const loading = ref(false)
const error = ref('')
const searched = ref(false)
const isDark = ref(localStorage.getItem('theme') === 'dark')

const applyTheme = () => {
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const runSearch = async (page = 1) => {
  const q = query.value.trim()
  if (!q) return

  loading.value = true
  error.value = ''
  searched.value = true

  try {
    const response = await pinsApi.search(q, page)
    pins.value = response.data.items
    meta.value = response.data.meta
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось выполнить поиск'
  } finally {
    loading.value = false
  }
}

const handleLike = async (pinId) => {
  try {
    const response = await pinsApi.like(pinId)
    const index = pins.value.findIndex(pin => pin.id === pinId)
    if (index !== -1) {
      pins.value[index] = response.data
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось изменить лайк'
  }
}

const openPinDetail = (pinId) => {
  router.push(`/pin/${pinId}`)
}

onMounted(() => {
  applyTheme()
  if (!authStore.isAuthenticated) {
    router.push('/login')
  }
})
</script>

<style scoped>
.catalog-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--primary) 18%, transparent), transparent 32rem),
    var(--bg);
  color: var(--text);
}

.catalog-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.icon-btn {
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

.catalog-main {
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
}

.catalog-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.catalog-toolbar h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1;
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.counter {
  color: var(--text-muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  font-weight: 700;
}

.search-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.search-row input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--text);
  padding: 0.85rem 1rem;
  font: inherit;
}

.search-row input:focus {
  outline: none;
  border-color: var(--primary);
}

.pins-masonry {
  column-count: 2;
  column-gap: 1rem;
}

.state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.empty-state {
  border: 1px dashed var(--border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--surface) 80%, transparent);
}

.empty-state h2 {
  margin: 0 0 0.5rem;
  color: var(--text);
}

.state.error {
  color: var(--danger);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0 0;
}

.pagination button {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--text);
  padding: 0.55rem 1rem;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (min-width: 768px) {
  .pins-masonry {
    column-count: 3;
  }
}

@media (min-width: 1200px) {
  .pins-masonry {
    column-count: 4;
  }
}

@media (max-width: 720px) {
  .catalog-header,
  .catalog-toolbar,
  .search-row {
    align-items: flex-start;
    grid-template-columns: 1fr;
  }

  .catalog-header {
    flex-direction: column;
  }

  .catalog-header,
  .catalog-main {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .pins-masonry {
    column-count: 1;
  }
}
</style>

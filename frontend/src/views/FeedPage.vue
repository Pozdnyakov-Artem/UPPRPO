<template>
  <div class="feed-page">
    <header class="feed-header">
      <router-link to="/" class="brand-title">OnlyFans Ruslana</router-link>
      <div class="header-actions">
        <button class="icon-btn" type="button" @click="toggleTheme" :title="isDark ? 'Светлая тема' : 'Темная тема'">
          {{ isDark ? '☀' : '☾' }}
        </button>
        <button class="btn outline" @click="showBoardModal = true">
          + Доска
        </button>
        <button class="btn primary" @click="showPinModal = true">
          + Пин
        </button>
        <router-link to="/boards" class="btn outline">Доски</router-link>
        <router-link to="/catalog" class="btn outline">Каталог</router-link>
        <router-link to="/profile" class="btn outline">👤 Профиль</router-link>
      </div>
    </header>

     <!-- 🔥 Модалка создания доски -->
    <CreateBoardModal 
      v-model="showBoardModal"
      @board-created="handleBoardCreated"
    />

    <CreatePinModal 
      v-model="showPinModal"
      :boards-version="boardsVersion"
      @pin-created="handlePinCreated"
      @create-board="showBoardModal = true"
    />

    <main class="feed-main">
      <div class="feed-toolbar">
        <div>
          <p class="eyebrow">Лента</p>
          <h2>Свежие пины</h2>
        </div>
        <span v-if="meta" class="counter">{{ meta.total }} всего</span>
      </div>

      <div class="pins-masonry">
      <PinCard 
        v-for="pin in pins" 
        :key="pin.id" 
        :pin="pin"
        @like="handleLike"
        @click="openPinDetail"
      />
      </div>
    </main>

    <!-- Пагинация -->
    <div class="pagination" v-if="meta">
      <button 
        :disabled="!meta.has_prev" 
        @click="loadPage(meta.page - 1)"
      >← Назад</button>
      
      <span>Страница {{ meta.page }} из {{ meta.pages }}</span>
      
      <button 
        :disabled="!meta.has_next" 
        @click="loadPage(meta.page + 1)"
      >Вперёд →</button>
    </div>

    <!-- Лоадер -->
    <div v-if="loading" class="loader">Загрузка...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'
import PinCard from '@/components/PinCard.vue' // создадим ниже
import CreateBoardModal from '@/components/CreateBoardModal.vue'
import CreatePinModal from '@/components/CreatePinModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const pins = ref([])
const meta = ref(null)
const loading = ref(false)
const currentPage = ref(1)

const showBoardModal = ref(false)
const showPinModal = ref(false)
const boardsVersion = ref(0)
const isDark = ref(localStorage.getItem('theme') === 'dark')

const applyTheme = () => {
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

// Загрузка пинов
const loadPins = async (page = 1, size = 20) => {
  loading.value = true
  pins.value = []
  try {
    const response = await api.get('/pins', {
      params: { page, size,  _t: Date.now() }
    })
    
    pins.value = response.data.items
    meta.value = response.data.meta
    currentPage.value = page
  } catch (err) {
    console.error('Ошибка загрузки пинов:', err)
  } finally {
    loading.value = false
  }
}

const loadPage = (page) => {
  if (page >= 1 && (!meta.value || page <= meta.value.pages)) {
    loadPins(page)
  }
}

const handleLike = async (pinId) => {
  try {
    const response = await api.post(`/pins/${pinId}/like`)
    // Обновляем пин в списке
    const index = pins.value.findIndex(p => p.id === pinId)
    if (index !== -1) {
      pins.value[index] = response.data
    }
  } catch (err) {
    console.error('Ошибка лайка:', err)
  }
}

const openPinDetail = (pinId) => {
  router.push(`/pin/${pinId}`)
}

const handleBoardCreated = (board) => {
  console.log('✅ Доска создана:', board)
  boardsVersion.value += 1
}

const handlePinCreated = (pin) => {
  console.log('✅ Пин создан:', pin)
  // 🔥 Автообновление ленты: перезагружаем первую страницу
  loadPins(1)
}

onMounted(() => {
  applyTheme()
  // Если не авторизован — редирект на логин
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  loadPins()
})
</script>

<style scoped>
.feed-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--primary) 18%, transparent), transparent 32rem),
    var(--bg);
  color: var(--text);
}

.feed-header {
  position: sticky;
  top: 0;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  backdrop-filter: blur(18px);
  padding: 0.85rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  z-index: 100;
}

.header-actions {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn.outline {
  background: var(--surface);
}

.btn.link {
  background: transparent;
  color: var(--text-muted);
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
  transition: border-color 0.18s, transform 0.18s;
}

.icon-btn:hover {
  border-color: var(--primary);
  transform: translateY(-1px);
}

.feed-main {
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.5rem 2rem 0;
}

.feed-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.feed-toolbar h2 {
  margin: 0;
  font-size: clamp(1.7rem, 3vw, 2.8rem);
  line-height: 1;
  letter-spacing: 0;
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-weight: 800;
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

.pins-masonry {
  column-count: 2;
  column-gap: 1rem;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  color: var(--text);
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

.loader {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.brand-title {
  font-weight: 900;
  font-size: 1.35rem;
  color: var(--primary);
  letter-spacing: 0;
  margin: 0;
  line-height: 1;
  user-select: none;
  text-decoration: none;
}

@media (max-width: 720px) {
  .feed-header {
    align-items: flex-start;
    flex-direction: column;
    padding: 0.9rem 1rem;
  }

  .feed-main {
    padding: 1rem;
  }

  .pins-masonry {
    column-count: 1;
  }
}
</style>

<template>
  <div class="boards-page">
    <header class="boards-header">
      <router-link to="/" class="brand-title">OnlyFans Ruslana</router-link>
      <div class="header-actions">
        <button class="theme-btn" type="button" @click="toggleTheme" :title="isDark ? 'Светлая тема' : 'Темная тема'">
          {{ isDark ? '☀' : '☾' }}
        </button>
        <router-link to="/" class="btn outline">Лента</router-link>
        <router-link to="/catalog" class="btn outline">Каталог</router-link>
        <router-link to="/profile" class="btn outline">Профиль</router-link>
      </div>
    </header>

    <main class="boards-shell">
      <section v-if="!selectedBoard" class="boards-list-view">
        <div class="section-head">
          <div>
            <p class="eyebrow">Коллекции</p>
            <h1>Доски</h1>
          </div>
          <button class="btn primary" type="button" @click="showBoardModal = true">+ Доска</button>
        </div>

        <div class="tabs" role="tablist">
          <button :class="{ active: activeTab === 'all' }" type="button" @click="setTab('all')">Все</button>
          <button :class="{ active: activeTab === 'mine' }" type="button" @click="setTab('mine')">Мои</button>
        </div>

        <div v-if="loadingBoards" class="state">Загрузка досок...</div>
        <div v-else-if="boardsError" class="state error">{{ boardsError }}</div>
        <div v-else-if="boards.length === 0" class="empty-state">
          <h2>Досок пока нет</h2>
          <p>Создайте первую доску и сохраните в нее пины.</p>
        </div>
        <div v-else class="boards-grid">
          <button
            v-for="board in boards"
            :key="board.id"
            type="button"
            class="board-card"
            @click="openBoard(board)"
          >
            <div class="board-cover" :class="{ 'has-grid': !board.avatar_url && board.preview_images?.length }">
              <img v-if="board.avatar_url" :src="resolveImageUrl(board.avatar_url)" :alt="board.name">
              <div v-else-if="board.preview_images?.length" class="preview-grid">
                <img
                  v-for="image in board.preview_images"
                  :key="image"
                  :src="resolveImageUrl(image)"
                  :alt="board.name"
                >
              </div>
              <span v-else>{{ board.name[0]?.toUpperCase() }}</span>
            </div>
            <div class="board-meta">
              <div>
                <h2>{{ board.name }}</h2>
                <p>{{ board.description || 'Без описания' }}</p>
              </div>
              <span class="owner">
                {{ board.owner?.username || 'Пользователь' }}
                <span v-if="board.is_private" title="Скрытая доска"> · private</span>
              </span>
            </div>
          </button>
        </div>
      </section>

      <section v-else class="board-detail-view">
        <div class="detail-top">
          <button class="back-link" type="button" @click="closeBoard">← Все доски</button>
          <div class="board-title-row">
            <div>
              <p class="eyebrow">Доска</p>
              <h1>{{ selectedBoard.name }}</h1>
              <p v-if="selectedBoard.description" class="board-description">{{ selectedBoard.description }}</p>
            </div>
            <span class="owner-pill">
              {{ selectedBoard.owner?.username }}
              <span v-if="selectedBoard.is_private"> · private</span>
            </span>
          </div>
        </div>

        <div v-if="loadingPins" class="state">Загрузка пинов...</div>
        <div v-else-if="pinsError" class="state error">{{ pinsError }}</div>
        <div v-else-if="pins.length === 0" class="empty-state">
          <h2>В этой доске нет пинов</h2>
          <p>Добавьте пин и выберите эту доску при сохранении.</p>
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
          <button :disabled="!meta.has_prev" @click="loadBoardPins(selectedBoard, meta.page - 1)">← Назад</button>
          <span>Страница {{ meta.page }} из {{ meta.pages }}</span>
          <button :disabled="!meta.has_next" @click="loadBoardPins(selectedBoard, meta.page + 1)">Вперед →</button>
        </div>
      </section>
    </main>

    <CreateBoardModal
      v-model="showBoardModal"
      @board-created="handleBoardCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { boardsApi, pinsApi } from '@/api/endpoints'
import { resolveImageUrl } from '@/utils/image'
import PinCard from '@/components/PinCard.vue'
import CreateBoardModal from '@/components/CreateBoardModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('all')
const boards = ref([])
const pins = ref([])
const meta = ref(null)
const selectedBoard = ref(null)
const loadingBoards = ref(false)
const loadingPins = ref(false)
const boardsError = ref('')
const pinsError = ref('')
const showBoardModal = ref(false)
const isDark = ref(localStorage.getItem('theme') === 'dark')

const applyTheme = () => {
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const setTab = async (tab) => {
  activeTab.value = tab
  await loadBoards()
}

const loadBoards = async () => {
  loadingBoards.value = true
  boardsError.value = ''
  try {
    const response = activeTab.value === 'mine'
      ? await boardsApi.getAll()
      : await boardsApi.getVisible()
    boards.value = response.data
  } catch (err) {
    boardsError.value = err.response?.data?.detail || 'Не удалось загрузить доски'
  } finally {
    loadingBoards.value = false
  }
}

const openBoard = async (board) => {
  selectedBoard.value = board
  await loadBoardPins(board, 1)
}

const closeBoard = () => {
  selectedBoard.value = null
  pins.value = []
  meta.value = null
}

const loadBoardPins = async (board, page = 1) => {
  loadingPins.value = true
  pinsError.value = ''
  try {
    const response = await boardsApi.getPins(board.id, page)
    pins.value = response.data.items
    meta.value = response.data.meta
  } catch (err) {
    pinsError.value = err.response?.data?.detail || 'Не удалось загрузить пины доски'
  } finally {
    loadingPins.value = false
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
    pinsError.value = err.response?.data?.detail || 'Не удалось изменить лайк'
  }
}

const openPinDetail = (pinId) => {
  router.push(`/pin/${pinId}`)
}

const handleBoardCreated = async (board) => {
  showBoardModal.value = false
  activeTab.value = 'mine'
  await loadBoards()
  await openBoard(board)
}

onMounted(async () => {
  applyTheme()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await loadBoards()
})
</script>

<style scoped>
.boards-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--primary) 18%, transparent), transparent 32rem),
    var(--bg);
  color: var(--text);
}

.boards-header {
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

.boards-shell {
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
}

.section-head,
.board-title-row {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.section-head h1,
.board-title-row h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1;
  letter-spacing: 0;
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.tabs {
  display: inline-flex;
  gap: 0.35rem;
  padding: 0.3rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
}

.tabs button {
  border: 0;
  border-radius: 999px;
  padding: 0.55rem 1rem;
  color: var(--text-muted);
  background: transparent;
  font-weight: 800;
  cursor: pointer;
}

.tabs button.active {
  color: #ffffff;
  background: var(--primary);
}

.boards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.board-card {
  display: grid;
  grid-template-rows: 150px 1fr;
  padding: 0;
  text-align: left;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
  color: var(--text);
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
  transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
}

.board-card:hover {
  transform: translateY(-3px);
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.board-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--primary) 85%, #ffffff), color-mix(in srgb, var(--accent) 72%, #ffffff));
  color: #ffffff;
  font-size: 4rem;
  font-weight: 900;
  overflow: hidden;
}

.board-cover > img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.board-cover.has-grid {
  background: var(--surface-raised);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 2px;
  width: 100%;
  height: 100%;
}

.preview-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.preview-grid img:first-child:nth-last-child(1) {
  grid-column: 1 / -1;
  grid-row: 1 / -1;
}

.preview-grid img:first-child:nth-last-child(2),
.preview-grid img:first-child:nth-last-child(2) ~ img {
  grid-row: 1 / -1;
}

.board-meta {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
}

.board-meta h2 {
  margin: 0 0 0.35rem;
  font-size: 1.15rem;
}

.board-meta p,
.board-description {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.owner,
.owner-pill {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 800;
}

.owner-pill {
  flex-shrink: 0;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.5rem 0.8rem;
  background: var(--surface);
}

.back-link {
  border: 0;
  background: transparent;
  color: var(--primary);
  font-weight: 900;
  cursor: pointer;
  padding: 0 0 1rem;
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
  .boards-header,
  .section-head,
  .board-title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .boards-header,
  .boards-shell {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .pins-masonry {
    column-count: 1;
  }
}
</style>

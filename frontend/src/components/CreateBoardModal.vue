<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="emit('update:modelValue', false)">
      <div class="modal-card">
        <!-- Хедер модалки -->
        <div class="modal-header">
          <h3>Создать новую доску</h3>
          <button class="close-btn" @click="emit('update:modelValue', false)">&times;</button>
        </div>

        <!-- Форма -->
        <form @submit.prevent="submit" class="modal-form">
          <div class="form-group">
            <label for="board-name">Название доски *</label>
            <input
              id="board-name"
              v-model="form.name"
              type="text"
              placeholder="Например: Вдохновение, Рецепты..."
              :disabled="isLoading"
              maxlength="100"
              required
            >
            <small>{{ form.name.length }}/100</small>
          </div>

          <div class="form-group">
            <label for="board-desc">Описание (необязательно)</label>
            <textarea
              id="board-desc"
              v-model="form.description"
              placeholder="О чём эта доска?"
              :disabled="isLoading"
              rows="3"
              maxlength="500"
            ></textarea>
            <small>{{ form.description?.length || 0 }}/500</small>
          </div>

          <div class="form-group checkbox">
            <label>
              <input
                type="checkbox"
                v-model="form.is_private"
                :disabled="isLoading"
              >
              <span>Скрытая доска (видна только вам)</span>
            </label>
          </div>

          <!-- Ошибки -->
          <div v-if="error" class="alert error">{{ error }}</div>

          <!-- Кнопки -->
          <div class="modal-actions">
            <button 
              type="button" 
              class="btn secondary" 
              @click="emit('update:modelValue', false)"
              :disabled="isLoading"
            >
              Отмена
            </button>
            <button 
              type="submit" 
              class="btn primary" 
              :disabled="!isValid || isLoading"
            >
              {{ isLoading ? 'Создаём...' : 'Создать доску' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { boardsApi } from '@/api/endpoints'

defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'board-created'])

const form = ref({
  name: '',
  description: '',
  is_private: false
})

const isLoading = ref(false)
const error = ref('')

const isValid = computed(() => form.value.name.trim().length >= 1)

const submit = async () => {
  if (!isValid.value) return
  
  error.value = ''
  isLoading.value = true
  
  const payload = {
    name: form.value.name.trim(),
    description: form.value.description?.trim() || null,
    is_private: form.value.is_private
  }
  
  try {
    const response = await boardsApi.create(payload)
    
    emit('board-created', response.data)
    emit('update:modelValue', false)
    form.value = { name: '', description: '', is_private: false }
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка создания доски'
    console.error('Create board error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(7, 10, 20, 0.62);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text);
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 1rem;
  font-family: inherit;
  color: var(--text);
  background: var(--surface-raised);
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.form-group small {
  display: block;
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-top: 0.25rem;
  text-align: right;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-weight: normal;
  cursor: pointer;
}

.form-group.checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.alert {
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.alert.error {
  background: color-mix(in srgb, var(--danger) 14%, var(--surface));
  color: var(--danger);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--border);
  border-radius: 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, background 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.primary {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: var(--primary-strong);
  border-color: var(--primary-strong);
}

.btn.secondary {
  background: var(--surface-soft);
  color: var(--text);
}

.btn.secondary:hover:not(:disabled) {
  background: var(--primary-soft);
}
</style>

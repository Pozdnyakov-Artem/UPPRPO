<template>
  <div class="pin-card" @click="emit('click', pin.id)">
    <div class="image-wrapper">
      <img 
        :src="resolvedImageUrl" 
        :alt="pin.title" 
        loading="lazy" 
        @error="onImageError"
      >
      <button class="like-btn" @click.stop="emit('like', pin.id)">
        {{ pin.is_liked ? '❤️' : '🤍' }} {{ pin.likes_count }}
      </button>
    </div>
    <div class="pin-info">
      <h4>{{ pin.title }}</h4>
      <p v-if="pin.description" class="description">{{ pin.description }}</p>
      <div class="author">
        <img v-if="authorAvatar" class="avatar-img" :src="authorAvatar" :alt="pin.author.username">
        <span v-else class="avatar">{{ getInitials(pin.author.username) }}</span>
        <span>{{ pin.author.username }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'
import { resolveImageUrl } from '@/utils/image'

const props = defineProps({
  pin: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['like', 'click'])
const resolvedImageUrl = computed(() => resolveImageUrl(props.pin?.image_url))
const authorAvatar = computed(() => resolveImageUrl(props.pin?.author?.img_url || props.pin?.author?.image_url))

// const onImageError = (e) => {
//   e.target.src = 'https://via.placeholder.com/400x600?text=No+Image'
// }

const getInitials = (username) => {
  return username?.[0]?.toUpperCase() || '?'
}

// 🔥 Заглушка при ошибке загрузки
const onImageError = (e) => {
  const placeholder = `data:image/svg+xml,${encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
      <rect width="400" height="600" fill="#f0f0f0"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
            font-family="system-ui, sans-serif" font-size="14" fill="#888">
        No Image
      </text>
    </svg>
  `)}`
  e.target.src = placeholder
  e.target.style.objectFit = 'contain'
  e.target.style.background = '#f9f9f9'
}
</script>

<style scoped>
/* ... стили без изменений ... */
.pin-card {
  break-inside: avoid;
  margin-bottom: 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.pin-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}
.image-wrapper { position: relative; }
.image-wrapper img {
  width: 100%;
  display: block;
  border-bottom: 1px solid var(--border);
  min-height: 200px;
  object-fit: cover;
  background: var(--surface-soft);
}
.like-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
}
.like-btn:hover { background: var(--primary-soft); }
.pin-info { padding: 0.75rem; }
.pin-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: var(--text);
  font-weight: 800;
}
.description {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 700;
}
.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.avatar-img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid var(--border);
}
</style>

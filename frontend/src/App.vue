<template>
  <!-- 🔥 Это "окошко", куда Vue Router будет подставлять страницы -->
  <router-view />
</template>

<script setup>
// Скрипт тут пока не нужен. Вся логика живёт в роутере и страницах.
</script>

<style>
* {
  box-sizing: border-box;
}

html {
  background: var(--bg);
}

body {
  margin: 0;
}

#app {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text);
  margin-top: 0;
  min-height: 100vh;
  background: var(--bg);
}
</style>

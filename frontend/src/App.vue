<script setup lang="ts">
import { RouterView } from 'vue-router'
import { NConfigProvider, NMessageProvider } from 'naive-ui'
</script>

<template>
  <n-config-provider>
    <n-message-provider />
    <RouterView />
  </n-config-provider>
</template>

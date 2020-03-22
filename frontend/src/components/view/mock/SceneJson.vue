<template>
  <div class="editor">
    <MonacoEditor
      height="400"
      theme="vs-dark"
      :language="language"
      :options="{value: json}"
      @change="onChange"
    ></MonacoEditor>
  </div>
</template>

<script>
import MonacoEditor from 'monaco-editor-vue'

export default {
  name: 'SceneJson',
  components: { MonacoEditor },
  props: ['json'],
  data () {
    return {
      language: 'json'
    }
  },
  methods: {
    onChange (value) {
      // 保存当前修改的代码，如果修改后数据类型会变成string
      // this.json = value
      this.$emit('sendJson', value)
    }
  }
}
</script>

<style lang="less" scoped>
</style>

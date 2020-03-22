<template>
  <div class="editor">
    <MonacoEditor
      height="400"
      theme="vs-dark"
      :language="language"
      :options="{value: JSON.stringify(json, null, 4)}"
      @change="onChange"
    ></MonacoEditor>
  </div>
</template>

<script>
import MonacoEditor from 'monaco-editor-vue'

export default {
  name: 'editor',
  components: { MonacoEditor },
  data () {
    return {
      language: 'json'
    }
  },
  methods: {
    onChange (value) {
      // 保存当前修改的代码，如果修改后数据类型会变成string
      this.json = value
    }
  },
  computed: {
    json: {
      get () {
        // 对象类型
        return this.$store.state.json
      },
      set (value) {
        this.$store.commit('setJson', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

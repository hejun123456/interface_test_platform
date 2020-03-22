<template>
  <div id="editor">
    <MonacoEditor
      height="800"
      theme="vs-dark"
      :language="language"
      :options="options"
      @change="onChange"
    ></MonacoEditor>
    <br />
    <Row>
      <Col :style="{textAlign: 'right'}">
        <Button @click="cancelEdit">返回</Button>
        <Button type="primary" @click="edit">提交</Button>
      </Col>
    </Row>
  </div>
</template>

<script>
import MonacoEditor from 'monaco-editor-vue'

// 路由参数传入，动态获取函数方法
let api = require('@/api/index')

export default {
  name: 'editor',
  components: { MonacoEditor },
  data () {
    return {
      // 标记当前编辑内容是否被编辑和提交，false:未编辑过; true:被编辑但未提交
      isChanged: false,
      // 本编辑页为通用编辑页，可通过路由传参控制所编辑的内容
      // 参数：
      // editInfo: 需要编辑的信息对象，必需包括id和编辑内容字段,
      // valueField: 内容字段名,
      // routerName: 编辑入口路由名,
      // editMethod: 提交编辑内容的方法名,
      editInfo: this.$route.params.editInfo,
      valueField: this.$route.params.valueField,
      routerName: this.$route.params.routerName,
      editMethod: this.$route.params.editMethod,
      options: {
        // Monaco Editor Options  用于初始化值
        value: this.$route.params.editInfo[this.$route.params.valueField]
      },
      // 保存原始内容,不做修改，用于对比
      oldValue: this.$route.params.editInfo[this.$route.params.valueField],
      language: 'python'
    }
  },
  methods: {
    onChange (value) {
      this.isChanged = true
      // 保存当前修改的代码
      this.options.value = value
    },
    edit () {
      // 获取更新后内容
      this.editInfo[this.valueField] = this.options.value
      // 获取修改方法
      let Edit = api[this.editMethod]
      // 修改项目信息
      Edit(this.editInfo, this.editInfo.id)
        .then(data => {
          // 提交成功/失败，停留在编辑页,修改标识,更新原始内容
          this.isChanged = false
          this.oldValue = this.options.value
          this.$Message.success(`${this.routerName}修改成功`)
          // 保存成功后直接跳转
          this.$router.replace({ name: this.routerName })
        })
        .catch(error => {
          console.log(error)
          // 如提交失败，需要恢复原内容（非页面显示内容），用于后面的对比
          // this.editInfo[this.valueField] = this.oldValue
          // this.$router.replace({ name: this.routerName })
          this.$Message.error(`${this.routerName}修改失败`)
        })
    },
    cancelEdit () {
      if (this.isChanged && this.options.value !== this.oldValue) {
        // 提示用户继续编辑或直接退出
        this.$Modal.confirm({
          title: '内容已被修改,直接退出将不保存',
          okText: '继续编辑',
          cancelText: '直接退出',
          onOk: () => {
          },
          onCancel: () => {
            this.$router.replace({ name: this.routerName })
          }
        })
      } else {
        this.$router.replace({ name: this.routerName })
      }
    }
  },
  beforeCreate () {
    // 检查有无传入待编辑数据，如无，返回原页面
    if (!this.$route.params.editInfo) {
      this.$router.replace({ name: this.$route.params.routerName })
    }
  }
}
</script>

<style lang="less" scoped>
</style>

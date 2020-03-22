<template>
  <div class="TcExtendStepTree">
    <Collapse>
      <Panel>
        前后置步骤（可选）
        <div slot="content">
          <Button v-if="moduleList.length !== 0" size="small" type="primary" @click="addExtendTC('before')">添加前置步骤</Button>
          <Button v-if="moduleList.length !== 0" size="small" type="primary" @click="addExtendTC('after')">添加后置步骤</Button>
          <Tree :data="moduleList" show-checkbox :load-data="loadTC" ref="extendStepTree"></Tree>
        </div>
      </Panel>
    </Collapse>
  </div>
</template>

<script>
import {
  TestcaseList
} from '@/api/index'

export default {
  name: 'tcextendsteptree',
  props: ['moduleList'],
  data () {
    return {

    }
  },
  methods: {
    loadTC (item, callback) {
      TestcaseList({page: 'None', project: item.project, module: item.id}).then(data => {
        // 用例列表，适配树形控件
        callback(
          data.map(item => {
            item.title = item.name
            return item
          })
        )
      })
    },
    addExtendTC (actionsname) {
      // 只取最后一个树,即当前的请求结果
      let treeEle = this.$refs.extendStepTree
      let checkedNodes = treeEle.getCheckedNodes()
      // 只取末节点
      checkedNodes = checkedNodes.filter(item => {
        return String(item.children) === 'undefined'
      })
      if (checkedNodes.length === 0) {
        this.$Message.warning(`请先勾选需要添加的${actionsname === 'before' ? '前置' : '后置'}步骤`)
        return
      }
      for (let i = 0; i < checkedNodes.length; i++) {
        console.log(checkedNodes[i])
        this[actionsname].push(checkedNodes[i])
      }
    }
  },
  computed: {
    before: {
      get () {
        return this.$store.state.before
      },
      set (value) {
        this.$store.commit('setBefore', value)
      }
    },
    after: {
      get () {
        return this.$store.state.after
      },
      set (value) {
        this.$store.commit('setAfter', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

<template>
  <div class="testcasetree">
    <Collapse>
      <Panel>
        <slot name="header">选择用例</slot>
        <div slot="content">
          <Tree :data="moduleList" show-checkbox :load-data="loadTC" ref="testcasetree" @on-check-change="getSelectedTestCase(isLength=true)"></Tree>
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
  name: 'testcasetree',
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
    getSelectedTestCase (isLength = false) {
      // 选择返回选中的用例数或用例本身
      // 只取最后一个树,即当前的请求结果
      let treeEle = this.$refs.testcasetree
      let checkedNodes = treeEle.getCheckedNodes()
      // 只取末节点
      checkedNodes = checkedNodes.filter(item => {
        return String(item.children) === 'undefined'
      })
      if (isLength) {
        this.caseSum = checkedNodes.length
      } else {
        return checkedNodes
      }
    },
    addTC () {
      this.caselist = this.getSelectedTestCase().map(item => item.id)
    }
  },
  computed: {
    caselist: {
      get () {
        return this.$store.state.caseList
      },
      set (value) {
        this.$store.commit('setCaseList', value)
      }
    },
    caseSum: {
      get () {
        return this.$store.state.caseSum
      },
      set (value) {
        this.$store.commit('setCaseSum', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

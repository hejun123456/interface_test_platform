<template>
  <div class="tcextendsteptree">
    <Collapse>
      <Panel>
        {{actionsname === 'Before' ? '前置' : '后置'}}步骤（选中）
        <div slot="content">
          <CellGroup v-show="this.actions.length > 0">
            <Cell title="拖拽改变步骤执行顺序">
            </Cell>
          </CellGroup>
          <Table
          :columns="columns"
          :data="actions"
          :show-header="false"
          :draggable="true"
          @on-drag-drop="changeSwitch">
            <template slot-scope="{ row, index }" slot="name">
              <Poptip trigger="hover" placement="right-start" :transfer="true" padding="0" @on-popper-show="getStep(row)">
                <div slot="content" v-if="updatePopTip" style="margin: 5px 0;">
                  <template v-for="(steps, sKey) in [['前置', 'before', 'md-log-in'], ['后置', 'after', 'md-log-out']]">
                    <div :key="sKey">
                      <Card :title="steps[0] + '用例'" :icon="steps[2]" :padding="0" shadow style="width: 400px;" >
                        <CellGroup v-if="testcaseSteps[String(row.id)] && JSON.parse(testcaseSteps[String(row.id)][steps[1]]).length > 0">
                          <Cell v-for="(item, key) in JSON.parse(testcaseSteps[String(row.id)][steps[1]])"
                            :key="key" :title="item[1]"/>
                            <!--  extra="编辑" :to="{name: 'EditTestcase', params: {currentCase: item[0]}}"  -->
                        </CellGroup>
                        <CellGroup v-else>
                          <Cell title="暂无"></Cell>
                        </CellGroup>
                      </Card>
                    </div>
                  </template>
                </div>
                <div>{{ row.name }}</div>
              </Poptip>
            </template>
          </Table>
        </div>
      </Panel>
    </Collapse>
  </div>
</template>

<script>
import { GetRefsCase } from '@/api/index'

export default {
  name: 'tcextendsteptree',
  props: ['actionsname', 'testcaseSteps'],
  data () {
    return {
      // testcaseSteps: {}, // 保存用例前后置步骤
      updatePopTip: false, // tip内容一次生成不会更新，所以定义此变量用于获取请求数据后更新tip
      columns: [
        {
          type: 'index',
          width: 60,
          align: 'center'
        },
        {
          title: 'name',
          slot: 'name'
        },
        {
          title: 'Action',
          key: 'action',
          width: 100,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'error',
                  size: 'small',
                  shape: 'circle',
                  icon: 'md-trash'
                },
                domProps: {
                  title: '删除'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => {
                    window.console.log(params.index)
                    this.actions.splice(params.index, 1)
                  }
                }
              })
            ])
          }
        }
      ]
    }
  },
  computed: {
    actions: {
      get () {
        return this.$store.state[this.actionsname.toLocaleLowerCase()]
      },
      set (value) {
        this.$store.commit('set' + this.actionsname, value)
      }
    }
  },
  methods: {
    changeSwitch (index1, index2) {
      // index1：当前拖拽行索引，index2：目标行索引
      // 插入
      this.actions.splice(
        index2,
        0,
        this.actions.splice(index1, 1)[0] // 从原数组中删除当前拖拽的元素，此处返回值是包含当前元素的数组
      )
    },
    async getStep (row) {
      this.updatePopTip = true
      if (!this.testcaseSteps[String(row.id)]) {
        if (!row.hadGetRefs) {
          await GetRefsCase({id: row.id}).then(data => {
            row.hadGetRefs = true // 保证每个用例只请求一次
            this.testcaseSteps[String(row.id)] = data
            this.updatePopTip = false
            this.$nextTick(() => {
              this.updatePopTip = true
            })
          })
        }
      }
    }
  }
}
</script>

<style lang="less" scoped>
.tcextendsteptree {
  margin-bottom: 10px;
}
</style>

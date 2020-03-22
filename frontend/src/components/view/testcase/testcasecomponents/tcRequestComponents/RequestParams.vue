<template>
  <div class="reqParams">
    <div :style="{marginBottom: '5px'}">
        <Button type="info" @click="addParams">添加params</Button>
        <Button type="error" @click="delParams">删除params</Button>
      </div>
      <Table
        :columns="columns"
        :data="reqParams"
        :border="true"
        :stripe="true"
        @on-selection-change="getSelectedRow"
        @on-row-click="editRow"
      ></Table>
  </div>
</template>

<script>
import { delRows } from '@/utils/Common'

export default {
  name: 'reqParams',
  data () {
    return {
      columns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {
          type: 'index',
          width: 60,
          align: 'center'
        },
        {
          title: 'param名',
          key: 'param_name',
          render: (h, params) => {
            if (this.reqParams[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.reqParams[params.index].param_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.reqParams[params.index].param_name = val
                  }
                }
              })
            } else {
              return h('div', this.reqParams[params.index].param_name)
            }
          }
        },
        {
          title: 'param值',
          key: 'param_value',
          render: (h, params) => {
            if (this.reqParams[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.reqParams[params.index].param_value,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据var_type来校验变量值
                    this.reqParams[params.index].param_value = val
                  }
                }
              })
            } else {
              return h('div', this.reqParams[params.index].param_value)
            }
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 150,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              // 根据当前是为编辑状态，切换按钮：编辑状态时，按钮为保存，否则为编辑
              this.reqParams[params.index].editable
                ? h(
                  'Button',
                  {
                    props: {
                      type: 'primary',
                      size: 'small'
                    },
                    style: {
                      marginRight: '5px'
                    },
                    on: {
                      click: e => {
                        // 阻止事件冒泡
                        e.stopPropagation()
                        this.reqParams[params.index].editable = false
                      }
                    }
                  },
                  [h('Icon', { props: { type: 'md-create' } }), '保存']
                )
                : h('div'),
              h(
                'Button',
                {
                  props: {
                    type: 'error',
                    size: 'small',
                    // 在编辑状态下，禁用删除按钮
                    disabled: this.reqParams[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.reqParams.splice(params.index, 1)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash' } }), '删除']
              )
            ])
          }
        }
      ],
      SelectedRow: []
    }
  },
  methods: {
    editRow (row, index) {
      // 被点击的行变为可编辑状态
      this.reqParams[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addParams () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.variables, this.variables.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   var_name: '',
      //   var_value: '',
      //   editable: false
      // })
      // 因为variables是个对象变量，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.reqParams.push({
        id: Math.random().toString(),
        param_name: '',
        param_value: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delParams () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.reqParams, this.SelectedRow)
      this.reqParams = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    reqParams: {
      get () {
        return this.$store.state.params
      },
      set (value) {
        this.$store.commit('setParams', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

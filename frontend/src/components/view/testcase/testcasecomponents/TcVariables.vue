<template>
  <div id="tcvariables">
    <div :style="{marginBottom: '10px'}">
      <Button type="info" @click="addVar">添加变量</Button>
      <Button type="error" @click="delVar">删除变量</Button>
    </div>
    <Table
      :columns="columns"
      :data="variables"
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
  name: 'tcvariables',
  data () {
    return {
      options: ['string', 'int', 'float', 'boolean'],
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
          title: '变量名',
          key: 'var_name',
          render: (h, params) => {
            if (this.variables[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.variables[params.index].var_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.variables[params.index].var_name = val
                  }
                }
              })
            } else {
              return h('div', this.variables[params.index].var_name)
            }
          }
        },
        {
          title: '变量类型',
          key: 'var_type',
          width: 150,
          render: (h, params) => {
            if (this.variables[params.index].editable) {
              return h('Select', {
                props: {
                  value: this.variables[params.index].var_type,
                  size: 'large',
                  transfer: true
                },
                on: {
                  'on-change': val => {
                    this.variables[params.index].var_type = val
                  }
                }
              },
              this.options.map(item => {
                return h('Option', {
                  props: {
                    value: item,
                    label: item
                  }
                })
              }))
            } else {
              return h('div', this.variables[params.index].var_type)
            }
          }
        },
        {
          title: '变量值',
          key: 'var_value',
          render: (h, params) => {
            if (this.variables[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.variables[params.index].var_value,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据var_type来校验变量值
                    this.variables[params.index].var_value = val
                  }
                }
              })
            } else {
              return h('div', this.variables[params.index].var_value)
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
              this.variables[params.index].editable
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
                        this.variables[params.index].editable = false
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
                    disabled: this.variables[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.variables.splice(params.index, 1)
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
      this.variables[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addVar () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.variables, this.variables.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   var_name: '',
      //   var_value: '',
      //   editable: false
      // })
      // 因为variables是个对象变量，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.variables.push({
        id: Math.random().toString(),
        var_name: '',
        var_type: 'string',
        var_value: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delVar () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.variables, this.SelectedRow)
      this.variables = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    variables: {
      get () {
        return this.$store.state.variables
      },
      set (value) {
        this.$store.commit('setVariables', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

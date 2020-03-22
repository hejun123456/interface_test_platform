<template>
  <div class="reqData">
    <div :style="{marginBottom: '5px'}">
        <Button type="info" @click="addData">添加data</Button>
        <Button type="error" @click="delData">删除data</Button>
      </div>
      <Table
        :columns="columns"
        :data="reqData"
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
  name: 'reqData',
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
          title: 'data名',
          key: 'data_name',
          render: (h, params) => {
            if (this.reqData[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.reqData[params.index].data_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.reqData[params.index].data_name = val
                  }
                }
              })
            } else {
              return h('div', this.reqData[params.index].data_name)
            }
          }
        },
        {
          title: '变量类型',
          key: 'data_type',
          width: 150,
          render: (h, params) => {
            if (this.reqData[params.index].editable) {
              return h(
                'Select',
                {
                  props: {
                    value: this.reqData[params.index].data_type,
                    size: 'large',
                    transfer: true
                  },
                  on: {
                    'on-change': val => {
                      this.reqData[params.index].data_type = val
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
                })
              )
            } else {
              return h('div', this.reqData[params.index].data_type)
            }
          }
        },
        {
          title: 'data值',
          key: 'data_value',
          render: (h, params) => {
            if (this.reqData[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.reqData[params.index].data_value,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据var_type来校验变量值
                    this.reqData[params.index].data_value = val
                  }
                }
              })
            } else {
              return h('div', this.reqData[params.index].data_value)
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
              this.reqData[params.index].editable
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
                        this.reqData[params.index].editable = false
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
                    disabled: this.reqData[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.reqData.splice(params.index, 1)
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
      this.reqData[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addData () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.variables, this.variables.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   var_name: '',
      //   var_value: '',
      //   editable: false
      // })
      // 因为variables是个对象变量，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.reqData.push({
        id: Math.random().toString(),
        data_name: '',
        data_type: 'string',
        data_value: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delData () {
      // 元素id不在选择范围内的，会被返回
      // 解构赋值
      let {allRows, selectedRows} = delRows(this.reqData, this.SelectedRow)
      this.reqData = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    reqData: {
      get () {
        return this.$store.state.data
      },
      set (value) {
        this.$store.commit('setData', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

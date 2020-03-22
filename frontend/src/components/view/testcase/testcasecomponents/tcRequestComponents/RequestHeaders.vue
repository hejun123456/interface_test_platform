<template>
  <div class="requestheaders">
    <div :style="{marginBottom: '5px'}">
        <Button type="info" @click="addHeader">添加headers</Button>
        <Button type="error" @click="delHeader">删除headers</Button>
      </div>
      <Table
        :columns="columns"
        :data="headers"
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
  name: 'requestheaders',
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
          title: 'header名',
          key: 'header_name',
          render: (h, params) => {
            if (this.headers[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.headers[params.index].header_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.headers[params.index].header_name = val
                  }
                }
              })
            } else {
              return h('div', this.headers[params.index].header_name)
            }
          }
        },
        {
          title: 'header值',
          key: 'header_value',
          render: (h, params) => {
            if (this.headers[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.headers[params.index].header_value,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据var_type来校验变量值
                    this.headers[params.index].header_value = val
                  }
                }
              })
            } else {
              return h('div', this.headers[params.index].header_value)
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
              this.headers[params.index].editable
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
                        this.headers[params.index].editable = false
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
                    disabled: this.headers[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.headers.splice(params.index, 1)
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
      this.headers[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addHeader () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.variables, this.variables.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   var_name: '',
      //   var_value: '',
      //   editable: false
      // })
      // 因为variables是个对象变量，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.headers.push({
        id: Math.random().toString(),
        header_name: '',
        header_value: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delHeader () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.headers, this.SelectedRow)
      this.headers = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    headers: {
      get () {
        return this.$store.state.headers
      },
      set (value) {
        this.$store.commit('setHeaders', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

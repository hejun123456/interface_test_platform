<template>
  <div class="tchooks">
    <div :style="{marginBottom: '10px'}">
      <Button type="info" @click="addHook">添加{{hookname}}</Button>
      <Button type="error" @click="delHook">删除{{hookname}}</Button>
    </div>
    <Table
      :columns="columns"
      :data="hooks"
      :border="true"
      :stripe="true"
      @on-selection-change="getSelectedRow"
      @on-row-click="editRow"
    ></Table>
  </div>
</template>

<script>
import { GetFuncs } from '@/api/index'
import { delRows } from '@/utils/Common'

export default {
  name: 'tchooks',
  props: ['hookname'],
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
          title: '函数名',
          key: 'hook',
          render: (h, params) => {
            if (this.hooks[params.index].editable) {
              return h(
                'AutoComplete',
                {
                  props: {
                    value: this.hooks[params.index].hook,
                    size: 'large',
                    transfer: true
                  },
                  on: {
                    input: val => {
                      this.hooks[params.index].hook = val
                    }
                  }
                },
                Object.keys(this.hooksList).map(index => {
                  return h(
                    'div',
                    {
                      class: { 'demo-auto-complete-item': true }
                    },
                    [
                      h(
                        'div',
                        {
                          class: { 'demo-auto-complete-group': true }
                        },
                        [h('span', {}, '所属项目：'.concat(index))]
                      )
                    ].concat(
                      this.hooksList[index].map((item, i) => {
                        return h('Option', {
                          props: { value: item, key: item },
                          class: {'demo-option': true}
                        })
                      })
                    )
                  )
                })
              )
            } else {
              return h('div', this.hooks[params.index].hook)
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
              this.hooks[params.index].editable
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
                        this.hooks[params.index].editable = false
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
                    disabled: this.hooks[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.hooks.splice(params.index, 1)
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
      this.hooks[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addHook () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.hooks, this.hooks.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   var_name: '',
      //   var_value: '',
      //   editable: false
      // })
      // 因为hooks是个对象变量，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.hooks.push({
        id: Math.random().toString(),
        hook: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delHook () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.hooks, this.SelectedRow)
      this.hooks = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    hooks: {
      get () {
        return this.$store.state[this.hookname]
      },
      set (value) {
        this.$store.commit('set' + this.hookname, value)
      }
    },
    hooksListReqTime: {
      get () {
        return this.$store.state.hooksListReqTime
      },
      set (value) {
        this.$store.commit('setHooksListReqTime', value)
      }
    },
    hooksList: {
      get () {
        return this.$store.state.hooksList
      },
      set (value) {
        this.$store.commit('setHooksList', value)
      }
    }
  },
  created () {
    if (this.hooksListReqTime === 0) {
      this.hooksListReqTime = 1
      GetFuncs({}).then(data => {
        this.hooksList = data
      })
    }
  }
}
</script>

<style lang="less">
.demo-auto-complete-item {
  padding: 4px 0;
  border-bottom: 1px solid #ececec;
}
.demo-auto-complete-group {
  font-size: 14px;
  padding: 4px 6px;
}
.demo-auto-complete-group span {
  color: #666;
  font-weight: bold;
}
.demo-option {
  font-size: 13px !important;
}
</style>

<template>
  <div id="tcparameters">
    <div :style="{marginBottom: '10px'}">
      <Button type="info" @click="addParam(false)">添加参数</Button>
      <Button type="error" @click="delParam">删除参数</Button>
    </div>
    <Table
      :columns="columns"
      :data="parameters"
      :border="true"
      :stripe="true"
      @on-selection-change="getSelectedRow"
      @on-row-click="editRow"
    ></Table>
  </div>
</template>

<script>
import {
  ParamsFileList
} from '@/api/index'
import { delRows } from '@/utils/Common'

export default {
  name: 'tcparameters',
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
          title: '参数名',
          key: 'param_name',
          width: 500,
          render: (h, params) => {
            if (this.parameters[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.parameters[params.index].param_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.parameters[params.index].param_name = val
                  }
                }
              })
            } else {
              return h('div', this.parameters[params.index].param_name)
            }
          }
        },
        {
          title: '参数值',
          key: 'param_value',
          render: (h, params) => {
            if (this.parameters[params.index].editable) {
              if (this.parameters[params.index].isFile) {
                // 文件则渲染下拉框
                return h('Select', {
                  props: {
                    value: this.trimfn(this.parameters[params.index].param_value),
                    size: 'large',
                    transfer: true
                  },
                  on: {
                    'on-change': val => {
                      this.parameters[params.index].param_value = val
                    }
                  }
                },
                this.paramsFileList.map(item => {
                  return h('Option', {
                    props: {
                      value: this.trimfn(item.file),
                      label: this.trimfn(item.file)
                    }
                  })
                }))
              } else {
                // 非文件则渲染输入框
                return h('Input', {
                  props: {
                    value: this.parameters[params.index].param_value,
                    size: 'large'
                  },
                  on: {
                    input: val => {
                      this.parameters[params.index].param_value = val
                    }
                  }
                })
              }
            } else {
              if (this.parameters[params.index].isFile) {
                return h('div', this.trimfn(this.parameters[params.index].param_value))
              } else {
                return h('div', this.parameters[params.index].param_value)
              }
            }
          }
        },
        {
          title: '切换类型',
          key: 'isFile',
          render: (h, params) => {
            return h(
              // 标签名
              'i-switch',
              // 属性
              {
                props: {
                  value: this.parameters[params.index].isFile,
                  size: 'large'
                },
                on: {
                  'on-change': val => {
                    // false代表当前为参数变量状态，所以要把param_value清空，否则会在输入框显示参数文件路径
                    // if (val === false) { this.parameters[params.index].param_value = '' }
                    this.parameters[params.index].isFile = val
                  }
                },
                scopedSlots: {
                  open: () => h('span', '文件'),
                  close: () => h('span', '变量')
                }
              }
            )
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
              this.parameters[params.index].editable
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
                        this.parameters[params.index].editable = false
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
                    disabled: this.parameters[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.parameters.splice(params.index, 1)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash' } }), '删除']
              )
            ])
          }
        }
      ],
      SelectedRow: [],
      paramsFileList: []
    }
  },
  methods: {
    trimfn (filename) {
      // 去掉文件路径前的两层路径
      let p = /static\/upload\//
      return filename.replace(p, '')
    },
    editRow (row, index) {
      // 被点击的行变为可编辑状态
      this.parameters[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addParam (isFile) {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      // this.$set(this.parameters, this.parameters.length, {
      // 这个方法也可以更新
      //   id: Math.random().toString(),
      //   param_name: '',
      //   param_value: '',
      //   editable: false
      // })
      // 因为variables是个对象参数，传递过来的是引用，此时直接操作对象不会触发set方法。
      this.parameters.push({
        id: Math.random().toString(),
        param_name: '',
        param_value: '',
        editable: false,
        isFile: isFile
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delParam () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.parameters, this.SelectedRow)
      this.parameters = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    parameters: {
      get () {
        return this.$store.state.parameters
      },
      set (value) {
        this.$store.commit('setParameters', value)
      }
    },
    project: {
      get () {
        return this.$store.state.msgObj.project
      },
      set (value) {
        this.$store.commit('setProject', value)
      }
    }
  },
  created () {
    ParamsFileList({page: 'None'}).then(data => {
      this.paramsFileList = data
    })
  }
}
</script>

<style lang="less" scoped>
</style>

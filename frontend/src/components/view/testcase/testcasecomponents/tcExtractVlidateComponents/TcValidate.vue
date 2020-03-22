<template>
  <div id="tcvalidate">
    <div :style="{marginBottom: '10px'}">
      <Button type="info" @click="addValidate">添加validate</Button>
      <Button type="error" @click="delValidate">删除validate</Button>
    </div>
    <Table
      :columns="columns"
      :data="validate"
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
  name: 'tcvalidate',
  data () {
    return {
      options: ['string', 'int', 'float', 'boolean'],
      comparators: [
        'equals',
        'not_equals',
        'contains',
        'startswith',
        'endswith',
        'contained_by',
        'less_than',
        'less_than_or_equals',
        'greater_than',
        'greater_than_or_equals',
        'string_equals',
        'length_equals',
        'length_greater_than',
        'length_greater_than_or_equals',
        'length_less_than',
        'length_less_than_or_equals',
        'type_match',
        'regex_match'
      ],
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
          title: 'Check',
          key: 'check',
          render: (h, params) => {
            if (this.validate[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.validate[params.index].check,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.validate[params.index].check = val
                  }
                }
              })
            } else {
              return h('div', this.validate[params.index].check)
            }
          }
        },
        {
          title: 'Comparator',
          key: 'comparator',
          width: 300,
          render: (h, params) => {
            if (this.validate[params.index].editable) {
              return h(
                'Select',
                {
                  props: {
                    value: this.validate[params.index].comparator,
                    size: 'large',
                    transfer: true
                  },
                  on: {
                    'on-change': val => {
                      this.validate[params.index].comparator = val
                    }
                  }
                },
                this.comparators.map(item => {
                  return h('Option', {
                    props: {
                      value: item,
                      label: item
                    }
                  })
                })
              )
            } else {
              return h('div', this.validate[params.index].comparator)
            }
          }
        },
        {
          title: 'Type',
          key: 'validate_type',
          width: 150,
          render: (h, params) => {
            if (this.validate[params.index].editable) {
              return h(
                'Select',
                {
                  props: {
                    value: this.validate[params.index].validate_type,
                    size: 'large',
                    transfer: true
                  },
                  on: {
                    'on-change': val => {
                      this.validate[params.index].validate_type = val
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
              return h('div', this.validate[params.index].validate_type)
            }
          }
        },
        {
          title: 'Expected',
          key: 'expected',
          render: (h, params) => {
            if (this.validate[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.validate[params.index].expected,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据validate_type来校验变量值
                    this.validate[params.index].expected = val
                  }
                }
              })
            } else {
              return h('div', this.validate[params.index].expected)
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
              this.validate[params.index].editable
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
                        this.validate[params.index].editable = false
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
                    disabled: this.validate[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.validate.splice(params.index, 1)
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
      this.validate[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addValidate () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      this.validate.push({
        id: Math.random().toString(),
        check: '',
        comparator: 'equals',
        validate_type: 'string',
        expected: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delValidate () {
      // 元素id不在选择范围内的，会被返回
      let { allRows, selectedRows } = delRows(this.validate, this.SelectedRow)
      this.validate = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    validate: {
      get () {
        return this.$store.state.validate
      },
      set (value) {
        this.$store.commit('setValidate', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

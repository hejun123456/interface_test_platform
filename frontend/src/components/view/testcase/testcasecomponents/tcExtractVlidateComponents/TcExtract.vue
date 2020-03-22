<template>
  <div id="tcextract">
    <div :style="{marginBottom: '10px'}">
      <Button type="info" @click="addExtract">添加extract</Button>
      <Button type="error" @click="delExtract">删除extract</Button>
    </div>
    <Table
      :columns="columns"
      :data="extract"
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
  name: 'tcextract',
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
          title: '提取名',
          key: 'extract_name',
          render: (h, params) => {
            if (this.extract[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.extract[params.index].extract_name,
                  size: 'large'
                },
                on: {
                  input: val => {
                    this.extract[params.index].extract_name = val
                  }
                }
              })
            } else {
              return h('div', this.extract[params.index].extract_name)
            }
          }
        },
        {
          title: '提取路径',
          key: 'extract_value',
          render: (h, params) => {
            if (this.extract[params.index].editable) {
              return h('Input', {
                props: {
                  value: this.extract[params.index].extract_value,
                  size: 'large'
                },
                on: {
                  input: val => {
                    // 在提交保存或提交debug时才根据extract_type来校验变量值
                    this.extract[params.index].extract_value = val
                  }
                }
              })
            } else {
              return h('div', this.extract[params.index].extract_value)
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
              this.extract[params.index].editable
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
                        this.extract[params.index].editable = false
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
                    disabled: this.extract[params.index].editable,
                    style: {}
                  },
                  on: {
                    click: e => {
                      // 阻止事件冒泡
                      e.stopPropagation()
                      this.extract.splice(params.index, 1)
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
      this.extract[index].editable = true
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    addExtract () {
      // 每行都有一个随机的字串作为id，用于批量删除的识别
      this.extract.push({
        id: Math.random().toString(),
        extract_name: '',
        extract_value: '',
        editable: false
      })
      // 清空selectedrow，添加后原来勾选的会被取消，但此属性中未清空，此时删除会起作用
      this.SelectedRow = []
    },
    delExtract () {
      // 元素id不在选择范围内的，会被返回
      let {allRows, selectedRows} = delRows(this.extract, this.SelectedRow)
      this.extract = allRows
      this.SelectedRow = selectedRows
    }
  },
  computed: {
    extract: {
      get () {
        return this.$store.state.extract
      },
      set (value) {
        this.$store.commit('setExtract', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
</style>

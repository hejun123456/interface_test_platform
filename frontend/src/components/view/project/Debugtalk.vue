<template>
  <div id="debugtalk">
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12" :offset="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
  </div>
</template>

<script>
import { DebugtalkList } from '@/api/index'
import { toLocalDateTime } from '@/utils/Common'

export default {
  inject: ['reload'],
  data () {
    return {
      columns: [
        {
          type: 'index',
          width: 60,
          align: 'center'
        },
        {
          title: '项目名称',
          key: 'project_name'
        },
        {
          title: 'Debugtalk',
          key: 'debugtalk',
          render: (h, params) => {
            return h('p', 'debugtalk.py')
          }
        },
        {
          title: '创建时间',
          key: 'create_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.create_time))
          }
        },
        {
          title: '更新时间',
          key: 'update_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.update_time))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 150,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h(
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
                    click: () => {
                      // 调整为跳转页面，弹窗显示不了
                      // // 打开修改弹窗
                      // this.editDebugtalkModel = true
                      // // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      // this.currentDebugtalkInfo = JSON.parse(
                      //   JSON.stringify(this.data[params.index])
                      // )
                      // // 回填代码到编辑器窗口
                      // this.options.value = this.currentDebugtalkInfo.debugtalk
                      // 跳转editer
                      this.$router.push({
                        name: 'Editor',
                        params: {
                          editInfo: JSON.parse(
                            JSON.stringify(this.data[params.index])
                          ),
                          valueField: 'debugtalk',
                          routerName: 'Debugtalk',
                          editMethod: 'EditDebugtalk'
                        }
                      })
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-create' } }), '编辑']
              )
            ])
          }
        }
      ],
      data: [],
      count: 0
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      DebugtalkList({ page: page }).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    }
  },
  created () {
    // 页面初始化请求分页数据
    this.getData(1)
  }
}
</script>

<style lang="less" scoped>
</style>

<template>
  <div id="envlist">
    <Table :columns="columns" :data="data" :border="true" :stripe="true">
      <template slot-scope="{ row, index }" slot="action">
        <Button type="primary" size="small" style="margin-right: 5px" @click="showDetail(row)">详情</Button>
        <Button type="error" size="small" @click="deleteReport(index)">删除</Button>
      </template>
      <template slot-scope="{ row, index }" slot="result">
        <strong :style="{color: row.result === 'Pass' ? 'green' : 'red'}">{{row.result}}</strong>
      </template>
    </Table>
    <br />
    <Row>
    <!--
      <Col :span="8">
      </Col>
    -->
      <Col :span="24" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
  </div>
</template>

<script>
import { ReportList, DeleteReport, CheckReport } from '@/api/index'
import { toLocalDateTime, second2hms } from '@/utils/Common'

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
          title: '报告名称',
          key: 'report_name'
        },
        {
          title: '简要描述',
          key: 'description'
        },
        {
          title: '用例总数',
          width: 100,
          key: 'case_sum'
        },
        {
          title: '成功用例',
          width: 100,
          key: 'case_pass'
        },
        {
          title: '开始时间',
          width: 200,
          key: 'start_at',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.create_time))
          }
        },
        {
          title: '运行时长',
          width: 100,
          key: 'duration',
          render: (h, params) => {
            return h('div', second2hms(params.row.duration))
          }
        },
        {
          title: '运行结果',
          width: 100,
          slot: 'result'
        },
        {
          title: '操作',
          slot: 'action',
          width: 150,
          align: 'center'
        }
      ],
      data: [],
      count: 0
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      ReportList({ page: page }).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    deleteReport (index) {
      // 删除环境信息
      this.$Modal.confirm({
        title: '确定要删除该报告吗？',
        content: `<span class='auto-break'>报告名：${this.data[index].report_name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteReport(this.data[index].id).then(data => {
            this.$Message.success('报告删除成功')
            this.reload()
          })
        }
      })
    },
    showDetail (row) {
      // 查询运行结果
      CheckReport({task_id: row.task_id}).then(data => {
        if (data.message) {
          // 如果响应中带message字段，说明任务正在运行
          this.$Message.info(data.message)
        } else {
          // 跳转到测试报告页面
          this.$router.push({
            name: 'TestReport',
            params: {
              caseResult: data
            }
          })
        }
      })
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

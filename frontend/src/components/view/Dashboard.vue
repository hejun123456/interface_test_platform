<template>
  <div id="dashboard">
    <!-- 卡片区域 -->
    <Row :gutter="32">
      <Col :span="6">
        <Card :bordered="false" class="card-border-top" style="color: #2d8cf0;">
          <p class="card-title" slot="title">项目数</p>
          <Icon type="md-folder" :size="iconSize" slot="extra"/>
          <div class="card-content">
            {{dashBoard.project_num}} 个
          </div>
        </Card>
      </Col>
      <Col :span="6">
        <Card :bordered="false" class="card-border-top" style="color: #2db7f5;">
          <p class="card-title" slot="title">模块数</p>
          <Icon type="md-apps" :size="iconSize" slot="extra"/>
          <div class="card-content">
            {{dashBoard.module_num}} 个
          </div>
        </Card>
      </Col>
      <Col :span="6">
        <Card :bordered="false" class="card-border-top" style="color: #ff9900;">
          <p class="card-title" slot="title">用例数</p>
          <Icon type="md-bug" :size="iconSize" slot="extra"/>
          <div class="card-content">
            <Row style="margin-bottom: 15px;">
              <Col>
                {{dashBoard.testcase_num}} 条
              </Col>
            </Row>
            <Row>
              <Col>
                <div class="card-sub-content">
                  30天新增用例数
                  <Tag color="warning" class="card-sub-content-tag">
                    {{dashBoard.new_testcase_num}}
                  </Tag>
                </div>
              </Col>
            </Row>
          </div>
        </Card>
      </Col>
      <Col :span="6">
        <Card :bordered="false" class="card-border-top" style="color: #19be6b;">
          <p class="card-title" slot="title" title="测试报告中统计的被执行用例总数">用例累计执行</p>
          <Icon type="md-play" :size="iconSize" slot="extra"/>
          <div class="card-content">
            <Row style="margin-bottom: 15px;">
              <Col>
                {{dashBoard.run_case_sum}} 次
              </Col>
            </Row>
            <Row>
              <Col>
                <div class="card-sub-content">
                  成功率
                  <Tag color="success" class="card-sub-content-tag">
                    {{ isNaN(((dashBoard.run_case_pass * 100)/dashBoard.run_case_sum)) ? 0 : ((dashBoard.run_case_pass * 100)/dashBoard.run_case_sum).toFixed(2) }}%
                  </Tag>
                </div>
              </Col>
            </Row>
          </div>
        </Card>
      </Col>
    </Row>

    <!-- 图表区域 -->
    <Row style="margin-top: 32px;">
      <Col>
        <Card :bordered="false" class="card-border-top">
          <p class="card-title" slot="title">30天用例执行概况</p>
          <ECharts
            :options="options"
            :auto-resize="true"
            style="width: 100%; height: 400px;"
            ref="echart"
          ></ECharts>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<script>
import { GetDashBoardInfo } from '@/api/index'
import ECharts from 'vue-echarts'
// 饼状图
import 'echarts/lib/chart/line'
// 提示
import 'echarts/lib/component/tooltip'
// 图例
import 'echarts/lib/component/legend'
// 标题
// import 'echarts/lib/component/title'

export default {
  name: 'dashboard',
  components: {
    ECharts
  },
  data () {
    return {
      En2Zh: {
        successes: ['成功', '#19be6b'],
        failures: ['失败', '#ff9900'],
        errors: ['错误', '#ed4014'],
        skipped: ['跳过', '#2db7f5']
      },
      // 面板总数据
      dashBoard: {},
      iconSize: 18,
      // 图表配置
      options: {
        tooltip: {
          trigger: 'axis',
          formatter: function (p) {
            let sum = 0
            let str = ''
            for (let i = 0; i < p.length; i++) {
              sum = sum + p[i].value
            }
            for (let i = 0; i < p.length; i++) {
              let rate = sum === 0 ? 0 : (p[i].value / sum * 100).toFixed(2)
              str = str + `${p[i].marker} ${p[i].seriesName}: ${p[i].value} (${rate}%)<br/>`
            }
            return `${p[0].name} (总数:${sum})<br/>` + str
          },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        color: ['#2db7f5', '#ed4014', '#ff9900', '#19be6b'], // 图例颜色配置和文字配置顺序是相反的
        legend: {
          data: ['成功', '失败', '错误', '跳过']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            boundaryGap: false,
            data: []
          }
        ],
        yAxis: [
          {
            type: 'value'
          }
        ],
        series: [
        ]
      }
    }
  },
  methods: {
    resizeEchart () {
      if (this.$refs.echart) {
        // window.onresize是全局的方法，非本组件时窗口调整会也触发，
        // 但此时没有echart组件，rezize方法会报不存在，所以增加一个条件
        this.$refs.echart.resize()
      }
    }
  },
  mounted () {
    window.onresize = () => {
      return (() => {
        this.resizeEchart()
      })()
    }
  },
  created () {
    GetDashBoardInfo().then(data => {
      this.dashBoard = data
      this.options.xAxis[0].data = data.series.date // x坐标日期
      for (let key in data.series) {
        if (this.En2Zh[key]) {
          // 跳过了"日期"字段 // 英文换中文 // 分配颜色
          let obj = {
            name: this.En2Zh[key][0],
            type: 'line',
            stack: '用例执行',
            data: data.series[key],
            areaStyle: {
              normal: {
                color: this.En2Zh[key][1]
              }
            },
            lineStyle: {
              normal: {
                color: this.En2Zh[key][1]
              }
            }
          }
          this.options.series.push(obj) // 数据
        }
      }
    })
  }
}
</script>

<style lang="less" scoped>
.card-border-top {
  border-top: 3px solid rgb(230, 230, 230);
  border-radius: 0px;
}
.card-content {
  min-height: 100px;
  font-size: 40px;
  font-weight: bold;
}
.card-sub-content {
  font-size: 14px;
  color: #808080;
}
.card-sub-content-tag {
  float: right;
  cursor: default;
}
.card-title {
  color: #757575;
}
</style>

<template>
  <div class="testreport">
    <Collapse simple v-model="open">
      <Panel name="open">
        报告汇总
        <Row id="test-summary" :gutter="24" slot="content">
          <Col class="summary-left" :span="12">
            <Card dis-hover>
              <ECharts
                :options="options"
                :auto-resize="true"
                style="width: 480px; height: 370px;"
                ref="echart"
              ></ECharts>
            </Card>
          </Col>
          <Col class="summary-right" :span="12">
            <Card dis-hover>
              <CellGroup style="height: 370px;">
                <Cell>
                  测试环境：
                  <span class="resultData">{{caseResult.base_url}}</span>
                </Cell>
                <Cell style="color: #2d8cf0;">
                  用例总数：
                  <span class="resultData">{{sum}}</span>
                </Cell>
                <Cell style="color: #19be6b;">
                  用例成功：
                  <span class="resultData">{{testcaseStat.successes}}</span>
                </Cell>
                <Cell style="color: #ff9900;">
                  用例失败：
                  <span class="resultData">{{testcaseStat.failures}}</span>
                </Cell>
                <Cell style="color: #ed4014;">
                  用例错误：
                  <span class="resultData">{{testcaseStat.errors}}</span>
                </Cell>
                <Cell style="color: #2db7f5;">
                  用例跳过：
                  <span class="resultData">{{caseResult.stat.skipped}}</span>
                </Cell>
                <Cell>
                  开始时间：
                  <span class="resultData">{{caseResult.time.start_datetime}}</span>
                </Cell>
                <Cell>
                  运行时长：
                  <span class="resultData">{{caseResult.time.duration | timeFilter}}</span>
                </Cell>
                <Cell>
                  用例成功率：
                  <span class="resultData">{{(testcaseStat.successes/sum*100).toFixed(2)}}%</span>
                </Cell>
              </CellGroup>
            </Card>
          </Col>
        </Row>
      </Panel>
      <Panel>
        用例详情
        <Row id="test-details" slot="content" :gutter="8">
          <Col class="test-filter" style="margin: 5px 0;">
            <Dropdown
              trigger="custom"
              :visible="visible"
              style="margin-left: 4px;"
              placement="bottom-start"
              @on-clickoutside="handleClose">
              <a href="javascript:void(0)" @click="handleOpen">
                结果筛选<Icon type="ios-arrow-down"></Icon>
              </a>
              <DropdownMenu slot="list" style="text-align: left;">
                <div style="padding-left: 10px;">
                  <CheckboxGroup v-model="filterLabel">
                    <Checkbox label="true">
                      <strong style="color: green;">Pass</strong>
                    </Checkbox><br>
                    <Checkbox label="false">
                      <strong style="color: red;">Fail</strong>
                    </Checkbox><br>
                  </CheckboxGroup>
                </div>
                <div style="text-align: left; margin: 10px;">
                  <Button type="primary" size="small" @click="reset">重置</Button>
                  <Button type="primary" size="small" @click="handleClose">关闭</Button>
                </div>
              </DropdownMenu>
            </Dropdown>
          </Col>
          <Col class="details-left" :span="8">
            <!-- 用例名列表 -->
            <div>
              <Table
                highlight-row
                :columns="columnsCaseList"
                :data="currentPageData"
                :stripe="false"
                :show-header="false"
                @on-row-click="getOneCaseRusult"
              ></Table>
            </div>
            <div style="text-align: center; margin-top: 10px;">
              <!-- 分页 -->
              <Page :total="total" :page-size="pageSize" simple @on-change="changePage"/>
            </div>
          </Col>
          <Col :span="16">
            <!-- 当前用例结果详情 -->
            <div>
              <Card dis-hover :bordered="false">
                <Row slot="title">
                  <!-- 用例名 -->
                  <Col style="margin-bottom: 10px;">
                    <strong style="font-size: 1.1rem;">{{currentCaseResult.name}}</strong>
                  </Col>
                  <Col :span="12" class="caseSummaryData">
                    <span>
                      成功接口：
                      <strong style="color: #19be6b;">
                        {{currentCaseResult.stat.successes}}
                      </strong>
                    </span>
                    <span>
                      失败接口：
                      <strong style="color: #ff9900;">
                        {{currentCaseResult.stat.failures}}
                      </strong>
                    </span>
                    <span>
                      错误接口：
                      <strong style="color: #ed4014;">
                        {{currentCaseResult.stat.errors}}
                      </strong>
                    </span>
                    <span>
                      跳过接口：
                      <strong style="color: #2db7f5;">
                        {{currentCaseResult.stat.skipped}}
                      </strong>
                    </span>
                  </Col>
                  <Col :span="12" style="text-align: right;" class="caseSummaryData">
                    <span>
                      运行时长：{{currentCaseResult.time.duration | timeFilter}}
                    </span>
                    <span>
                      用例结果：
                      <strong :style="{color: currentCaseResult.success ? 'green' : 'red'}">
                        {{currentCaseResult.success ? 'Pass' : 'Fail'}}
                      </strong>
                    </span>
                  </Col>
                </Row>
                <Collapse>
                  <Panel
                    v-for="(item, index) in currentCaseResult.records"
                    :key="index"
                    :style="{fontSize: '12px'}">
                    接口{{index+1}} : {{item.name}}
                    <span style="float: right;margin-right: 16px;">
                      结果：
                      <strong :style="{color: getColor(item.status)}">{{item.status}}</strong>
                    </span>
                    <div slot="content">
                      <Collapse simple>
                        <Panel>
                          request
                          <div slot="content">
                            <Row class="content-row">
                              <Col :span="4">开始时间</Col>
                              <Col :span="20">{{item.meta_data.request.start_timestamp}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">请求方法</Col>
                              <Col :span="20">{{item.meta_data.request.method}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">url</Col>
                              <Col :span="20">{{item.meta_data.request.url}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">headers</Col>
                              <Col :span="20">{{item.meta_data.request.headers}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">body</Col>
                              <Col :span="20">{{item.meta_data.request.body || 'None'}}</Col>
                            </Row>
                            <Row class="content-row" v-if="item.meta_data.request.params">
                              <Col :span="4">params</Col>
                              <Col :span="20">{{item.meta_data.request.params}}</Col>
                            </Row>
                            <Row class="content-row" v-if="item.meta_data.request.data">
                              <Col :span="4">data</Col>
                              <Col :span="20">{{item.meta_data.request.data}}</Col>
                            </Row>
                            <Row class="content-row" v-if="item.meta_data.request.json">
                              <Col :span="4">json</Col>
                              <Col :span="20">{{item.meta_data.request.json}}</Col>
                            </Row>
                          </div>
                        </Panel>
                        <Panel>
                          response
                          <div slot="content">
                            <Row class="content-row">
                              <Col :span="4">状态码</Col>
                              <Col :span="20">{{item.meta_data.response.status_code}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">reason</Col>
                              <Col :span="20">{{item.meta_data.response.reason}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">响应时间</Col>
                              <Col :span="20">{{item.meta_data.response.response_time_ms}}ms</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">headers</Col>
                              <Col :span="20">{{item.meta_data.response.headers}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">cookies</Col>
                              <Col :span="20">{{item.meta_data.response.cookies}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">ok</Col>
                              <Col :span="20">{{item.meta_data.response.ok}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">响应编码</Col>
                              <Col :span="20">{{item.meta_data.response.encoding || 'None'}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">响应类型</Col>
                              <Col :span="20">{{item.meta_data.response.content_type}}</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">响应大小</Col>
                              <Col :span="20">{{item.meta_data.response.content_size}} bytes</Col>
                            </Row>
                            <Row class="content-row">
                              <Col :span="4">content</Col>
                              <Col :span="20">{{item.meta_data.response.content || 'None'}}</Col>
                            </Row>
                            <Row class="content-row" v-if="item.meta_data.response.text">
                              <Col :span="4">text</Col>
                              <Col :span="20">{{item.meta_data.response.text}}</Col>
                            </Row>
                            <Row class="content-row" v-if="item.meta_data.response.json">
                              <Col :span="4">json</Col>
                              <Col :span="20">{{item.meta_data.response.json}}</Col>
                            </Row>
                          </div>
                        </Panel>
                        <Panel v-if="item.meta_data.validators.length > 0">
                          validators
                          <div slot="content">
                            <Table
                            border
                            :row-class-name="rowClassName"
                            :columns="validatorsColumns"
                            :data="item.meta_data.validators">
                              <template slot-scope="{ row }" slot="expect">
                                <p>{{row.expect}} (期望值|{{typeof row.expect}})</p>
                              </template>
                              <template slot-scope="{ row }" slot="check_value">
                                <p>{{row.check_value}} (实际值|{{typeof row.check_value}})</p>
                              </template>
                            </Table>
                          </div>
                        </Panel>
                        <Panel v-if="item.attachment">
                          TraceBack
                          <div slot="content">
<pre class="not-wrap">{{item.attachment}}</pre>
                          </div>
                        </Panel>
                      </Collapse>
                    </div>
                  </Panel>
                </Collapse>
              </Card>
            </div>
          </Col>
        </Row>
      </Panel>
      <Panel>
        top 10 错误表
        <Row slot="content">
          <Col>
            <Table :columns="errorsColumns" :data="errorsData" :border="true" :stripe="true"></Table>
          </Col>
        </Row>
      </Panel>
    </Collapse>
  </div>
</template>

<script>
import { second2hms } from '@/utils/Common'
import ECharts from 'vue-echarts'
// 饼状图
import 'echarts/lib/chart/pie'
// 柱状图
// import 'echarts/lib/chart/bar'
// 提示
import 'echarts/lib/component/tooltip'
// 图例
import 'echarts/lib/component/legend'
// 标题
import 'echarts/lib/component/title'

export default {
  name: 'testreport',
  data () {
    return {
      // 用例筛选条件
      filterLabel: [],
      // 用例筛选条件下拉菜单控制
      visible: false,
      // 用例总数
      total: '',
      // 当前选中的用例信息，默认先第一个
      currentCaseResult: '',
      validatorsColumns: [
        {
          title: 'check',
          key: 'check'
        },
        {
          title: 'expect',
          slot: 'expect'
        },
        {
          title: 'comparator',
          key: 'comparator'
        },
        {
          title: 'check_value',
          slot: 'check_value'
        },
        {
          title: 'check_result',
          key: 'check_result'
        }
      ],
      columnsCaseList: [
        {
          title: '用例名',
          align: 'left',
          key: 'name',
          render: (h, params) => {
            return h('div', [
              h(
                'span',
                {
                  style: {
                    fontSize: '1rem'
                  }
                },
                params.row.name
              ),
              h('div', [
                h('span', 'base_url：' + params.row.base_url),
                h(
                  'span',
                  {
                    style: {
                      float: 'right',
                      color: params.row.success ? 'green' : 'red'
                    }
                  },
                  params.row.success ? 'Pass' : 'Fail')
              ])
            ])
          }
        }
      ],
      // 报告汇总折叠页默认打开，否则图表会走形
      open: 'open',
      En2Zh: {
        successes: '成功',
        failures: '失败',
        errors: '错误',
        skipped: '跳过'
      },
      // 用例执行结果或者任务id
      caseResult: '',
      filterData: [],
      // 当前页面显示的用例
      currentPageData: [],
      pageSize: 10,
      options: {
        title: {
          text: '用例执行情况',
          x: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          x: 'left',
          data: ['错误', '失败', '跳过', '成功']
        },
        series: [
          {
            name: '执行情况',
            type: 'pie',
            radius: '75%',
            avoidLabelOverlap: true,
            label: {
              normal: {
                show: true,
                formatter: '{b}用例: {c} ({d}%)',
                textStyle: {
                  fontSize: '14'
                }
              },
              emphasis: {
                show: true,
                textStyle: {
                  fontSize: '15'
                }
              }
            },
            // color和data的顺序是相关
            data: [],
            color: ['#ff9900', '#ed4014', '#2db7f5', '#19be6b']
          }
        ]
      },
      // top 10错误表配置
      errorsColumns: [
        {
          type: 'index',
          width: 60,
          align: 'center'
        },
        {
          title: '错误名',
          key: 'err_name'
        },
        {
          title: '用例数',
          width: 100,
          key: 'err_sum'
        },
        {
          title: '错误用例占比',
          width: 120,
          key: 'err_rate'
        },
        {
          title: '错误详情',
          key: 'err_detail'
        }
      ],
      errorsData: []
    }
  },
  components: {
    ECharts
  },
  mounted () {
    window.onresize = () => {
      return (() => {
        this.resizeEchart()
      })()
    }
  },
  methods: {
    changePage (page) {
      // 获取分页数据
      // 增加筛选条件判断 有条件
      let start = (page - 1) * this.pageSize
      let end = page * this.pageSize
      this.currentPageData = this.filterLabel.length === 1 ? this.filterData.slice(start, end) : this.caseResult.details.slice(start, end)
    },
    resizeEchart () {
      if (this.$refs.echart) {
        // window.onresize是全局的方法，非本组件时窗口调整会也触发，
        // 但此时没有echart组件，rezize方法会报不存在，所以增加一个条件
        this.$refs.echart.resize()
      }
    },
    getOneCaseRusult (row, index) {
      // 获取单个用例运行的结果数据
      this.currentCaseResult = row
    },
    getColor (status) {
      // 单个接口根据结果来显示颜色
      let color = null
      switch (status) {
        case 'error':
          color = '#ed4014'
          break
        case 'success':
          color = '#19be6b'
          break
        case 'failure':
          color = '#ff9900'
          break
        default:
          color = '#2db7f5'
          break
      }
      return color
    },
    rowClassName (row, index) {
      if (row.check_result === 'fail') {
        return 'fail-validator'
      }
      return ''
    },
    handleOpen () {
      this.visible = true
    },
    handleClose () {
      // 关闭筛选条件弹窗时触发此函数
      this.visible = false
      if (this.filterLabel.length === 1) {
        // 筛选
        this.filterData = this.caseResult.details.filter(item => {
          return item.success.toString() === this.filterLabel[0]
        })
        this.currentPageData = this.filterData.slice(0, this.pageSize)
        // 用例总数修改
        this.total = this.filterData.length
      } else {
        // 全选
        this.currentPageData = this.caseResult.details.slice(0, this.pageSize)
        // 用例总数修改
        this.total = this.caseResult.details.length
      }
    },
    reset () {
      this.filterLabel = []
    }
  },
  computed: {
    sum () {
      let info = this.$route.params.caseResult || JSON.parse(localStorage.getItem('caseResult'))
      return info.details.length
    },
    testcaseStat () {
      let successes = 0
      let failures = 0
      let errors = 0
      let info = this.$route.params.caseResult || JSON.parse(localStorage.getItem('caseResult'))
      for (let i = 0; i < info.details.length; i++) {
        if (info.details[i].success) {
          successes++
        } else {
          if (info.details[i].stat.errors > 0) {
            // 只要有一个errors的接口，则认为整个用例属于errors
            errors++
          } else {
            failures++
          }
        }
      }
      return {
        successes: successes,
        failures: failures,
        errors: errors,
        skipped: info.stat.skipped // 平台非实现对用例跳过，所以此数据都是0
      }
    }
  },
  filters: {
    timeFilter (value) {
      return second2hms(value)
    }
  },
  created () {
    if (this.$route.params.caseResult) {
      // 由其他页面跳转进来页面初始化，路由参数传入summary
      for (let index in this.$route.params.caseResult.stat) {
        // 获取图表的数据
        if (this.En2Zh[index]) {
          this.options.series[0].data.push({
            name: this.En2Zh[index],
            value: this.testcaseStat[index]
          })
        }
      }
      // 获取全部用例数据
      this.caseResult = this.$route.params.caseResult
      this.errorsData = this.$route.params.caseResult.top10error
      console.log('用例运行结果数据')
      console.log(this.caseResult)
      localStorage.setItem(
        'caseResult',
        JSON.stringify(this.$route.params.caseResult)
      )
    } else {
      // 刷新报告页面时，如果本地有结果数据，则显示，否则跳转回到前一页
      if (localStorage.getItem('caseResult') === null) {
        this.$router.replace({ name: 'ReportManage' })
      } else {
        this.caseResult = JSON.parse(localStorage.getItem('caseResult'))
        for (let index in this.caseResult.stat) {
          if (this.En2Zh[index]) {
            this.options.series[0].data.push({
              name: this.En2Zh[index],
              value: this.testcaseStat[index]
            })
          }
        }
      }
    }
    this.total = this.caseResult.details.length
    this.currentPageData = this.caseResult.details.slice(0, this.pageSize) // 初始化第一页用例结果 start / end
    // 获取第一条用例的数据
    this.currentCaseResult = this.caseResult.details[0]
  }
}
</script>

<style lang="less" scoped>
.ivu-cell-title {
  font-size: 1.1rem !important;
}
.resultData {
  margin-left: 15px;
}
.caseSummaryData {
  font-size: 0.8em;
  & > span {
    margin-right: 5px;
  }
}
.content-row {
  padding: 5px 0;
  border-bottom: 1px solid #d6d6d6;
}
.content-row:hover {
  background-color: #e6eef7;
  cursor: pointer;
}
.not-wrap {
  margin: 0 !important;
  white-space:pre-wrap; /* css3.0 */
  white-space:-moz-pre-wrap; /* Firefox */
  white-space:-pre-wrap; /* Opera 4-6 */
  white-space:-o-pre-wrap; /* Opera 7 */
  word-wrap:break-word; /* Internet Explorer 5.5+ */
}
</style>

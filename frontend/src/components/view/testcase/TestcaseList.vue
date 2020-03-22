<template>
  <div id="testcaselist">
    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>
    <Table :columns="columns" :data="data" :border="true" :stripe="true" @on-selection-change="getSelectedRow">
        <template slot-scope="{ row, index }" slot="name">
          <Poptip trigger="hover" placement="right-start" :transfer="true" padding="0" @on-popper-show="getTestcaseNameLocal(row)">
            <div slot="content">
              <Card title="前置用例" icon="md-log-in" :padding="0" shadow style="width: 400px;">
                <CellGroup v-if="JSON.parse(row.before).length > 0">
                  <Cell v-for="(item, key) in JSON.parse(row.before)"
                    :key="key" :title="item[1]" extra="编辑" :to="{name: 'EditTestcase', params: {currentCase: item[0]}}" />
                </CellGroup>
                <CellGroup v-else>
                  <Cell title="暂无"></Cell>
                </CellGroup>
              </Card>
              <br>
              <br>
              <Card title="后置用例" icon="md-log-out" :padding="0" shadow style="width: 400px;">
                <CellGroup v-if="JSON.parse(row.after).length > 0">
                  <Cell v-for="(item, key) in JSON.parse(row.after)"
                    :key="key" :title="item[1]" extra="编辑" :to="{name: 'EditTestcase', params: {currentCase: item[0]}}" />
                </CellGroup>
                <CellGroup v-else>
                  <Cell title="暂无"></Cell>
                </CellGroup>
              </Card>
            </div>
            <div>{{ row.name }}</div>
          </Poptip>
        </template>
    </Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="goTo('AddTestcase')">
          <Icon type="md-add" />新增
        </Button>
        <Button type="primary" size="small" @click="runCaseByBatch">
          <Icon type="ios-bug" />运行
        </Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <Modal v-model="evnModel" title="选择运行环境" @on-ok="ok" @on-cancel="cancel">
      <Row style="margin-bottom: 15px;">
        <Col :span="5">
          <label style="display: inline-block; line-height: 30px; font-size: 16px; float: right;">
            <span style="display: inline-block; line-height: 30px; font-size: 16px; color: red;">*</span>
            运行环境：
          </label>
        </Col>
        <Col :span="19">
          <Select v-model="base_url">
            <Option v-for="item in evnList" :value="item.id" :key="item.env_name" v-if="item.is_valid">{{ item.env_name }}</Option>
          </Select>
        </Col>
      </Row>
      <template  v-if="this.runningType === 'batch'">
        <Row style="margin-bottom: 15px;">
          <Col :span="5">
            <label style="display: inline-block; line-height: 30px; font-size: 16px; float: right;">
              运行方式：
            </label>
          </Col>
          <Col :span="19">
            <Select v-model="runType">
              <Option value='async'>{{ '异步运行' }}</Option>
              <Option value='sync'>{{ '同步运行' }}</Option>
            </Select>
          </Col>
        </Row>
        <template v-if="this.runType === 'async'">
          <Row style="margin-bottom: 15px;">
            <Col :span="5">
              <label style="display: inline-block; line-height: 30px; font-size: 16px; float: right;">
                报告名称：
              </label>
            </Col>
            <Col :span="19">
              <Input v-model="reportName" placeholder="选填，默认带时间后缀"></Input>
            </Col>
          </Row>
          <Row>
            <Col :span="5">
              <label style="display: inline-block; line-height: 30px; font-size: 16px; float: right;">
                报告描述：
              </label>
            </Col>
            <Col :span="19">
              <Input v-model="reportDescription" placeholder="选填"></Input>
            </Col>
          </Row>
        </template>
      </template>
    </Modal>
    <Modal v-model="runningModel" :closable="false">
      <div style="text-align:center">
          <p style="font-size: 1.4em;">用例运行中，请稍等...</p>
      </div>
      <div slot="footer">
          <Button type="warning" size="large" long @click="cancelWaiting">取消</Button>
      </div>
    </Modal>
    <Modal v-model="copyModal" title="输入新的用例名称" :loading="loading" @on-ok="okCopy" @on-cancel="cancel">
      <Row >
        <Col :span="5">
          <label style="display: inline-block; line-height: 30px; font-size: 16px; float: right;">
            用例名称：
          </label>
        </Col>
        <Col :span="19">
          <Input v-model="copyTestcase.name" placeholder="输入新用例名称"></Input>
        </Col>
      </Row>
    </Modal>
  </div>
</template>

<script>
import { TestcaseList, DeleteTestcase, Test, EnvList, ModuleList, ProjectList, CopyTestcase } from '@/api/index'
import { toLocalDateTime, getTestcaseName, changeLoadingState } from '@/utils/Common'
import SearchBar from '@/components/common/SearchBar'

export default {
  inject: ['reload'],
  components: {
    SearchBar
  },
  data () {
    return {
      loading: true,
      // 复制用例数据
      copyTestcase: {},
      // 测试报告名
      reportName: '',
      // 测试报告描述
      reportDescription: '',
      // 选中的用例id数组
      SelectedRow: [],
      // 用例运行方式：批量（batch）/单用例（single）
      runningType: '',
      runType: 'sync', // 传到后端的参数  async异步  sync同步
      // 当前运行的case
      currentCase: '',
      base_url: '',
      // 选择环境弹窗显示控制
      evnModel: false,
      // 用例运行时显示运行中弹窗
      runningModel: false,
      // 复制弹窗
      copyModal: false,
      jumpFlag: false,
      // 环境列表
      evnList: [],
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
          title: '用例名称',
          slot: 'name'
        },
        {
          title: '项目',
          key: 'project_name'
        },
        {
          title: '模块',
          key: 'module_name'
        },
        {
          title: '测试人员',
          key: 'author'
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
          width: 200,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h(
                'Button',
                {
                  props: {
                    type: 'primary',
                    size: 'small'
                    // shape: 'circle'
                  },
                  domProps: {
                    title: '运行'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.currentCase = params.row
                      // 触发弹窗选择环境
                      this.evnModel = true
                      // 单用例运行
                      this.runningType = 'single'
                      this.runType = 'sync'
                    }
                  }
                },
                [h('Icon', { props: { type: 'ios-bug', size: '18' } })]
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'primary',
                    size: 'small'
                    // shape: 'circle'
                  },
                  domProps: {
                    title: '编辑'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.gotoEditPage(params.row)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-create', size: '18' } })]
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'primary',
                    size: 'small'
                    // shape: 'circle'
                  },
                  domProps: {
                    title: '复制'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.copyModal = true
                      this.copyTestcase = { name: params.row.name, id: params.row.id }
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-copy', size: '18' } })]
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'error',
                    size: 'small'
                    // shape: 'circle'
                  },
                  domProps: {
                    title: '删除'
                  },
                  on: {
                    click: () => {
                      this.deleteTestcase(params.index)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash', size: '18' } })]
              )
            ])
          }
        }
      ],
      data: [],
      count: 0,
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'name',
          searchText: '用例名称'
        },
        {
          searchName: 'project',
          searchText: '项目名称',
          type: 'select',
          choices: []
        },
        {
          searchName: 'module',
          searchText: '模块名称',
          type: 'select',
          choices: []
        },
        {
          searchName: 'author',
          searchText: '测试人员'
        },
        {
          searchName: 'create_time',
          searchText: '创建时间',
          type: 'date'
        },
        {
          searchName: 'update_time',
          searchText: '更新时间',
          type: 'date'
        }
      ]
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      TestcaseList(Object.assign({ page: page }, this.$refs.searchBar.searchConditions)).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    goTo (pagename) {
      // 页面跳转
      this.$router.push({name: pagename})
    },
    deleteTestcase (index) {
      // 删除用例信息
      this.$Modal.confirm({
        title: '确定要删除该用例吗？',
        content: `<span class='auto-break'>用例名：${this.data[index].name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteTestcase(this.data[index].id).then(data => {
            this.$Message.success('用例删除成功')
            this.reload()
          })
        }
      })
    },
    ok () {
      // 运行环境必选
      if (this.base_url === '') {
        this.$Message.warning('请先选择运行环境')
        return
      }
      console.log('运行方式: ')
      console.log(this.runType)
      console.log('运行的用例id: ')
      let caseList = []
      if (this.runningType === 'single') {
        caseList.push(this.currentCase.id)
        // 打开弹窗
        this.runningModel = true
        // 打开跳转标志，即允许跳转
        this.jumpFlag = true
      } else {
        caseList = this.SelectedRow
        if (this.runType === 'sync') {
          // 批量同步运行
          // 打开弹窗
          this.runningModel = true
          // 打开跳转标志，即允许跳转
          this.jumpFlag = true
        }
      }
      console.log(caseList)

      Test({
        case_list: {
          case: caseList
        },
        env: this.base_url,
        report_name: this.reportName.trim(),
        description: this.reportDescription,
        runType: this.runType
      }).then(data => {
        // 关闭弹窗
        this.runningModel = false
        console.log(data)
        if (data.task_id) {
          // 异步，只显示提示语
          this.$Message.info(data.message)
        } else {
          // 跳转到报告页面，传入结果数据
          if (this.jumpFlag) {
            this.$router.push({
              name: 'TestReport',
              params: {
                caseResult: data.summary
              }
            })
          }
        }
      })
    },
    cancel () {
      console.log('取消')
    },
    cancelWaiting () {
      // 关闭弹窗
      this.runningModel = false
      // 关闭跳转标志
      this.jumpFlag = false
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    runCaseByBatch () {
      // 批量运行用例
      // 检查是否有选中的用例
      if (this.SelectedRow.length === 0) {
        this.$Message.warning('请先选择用例')
        return
      }
      // 触发弹窗选择环境
      this.evnModel = true
      this.runningType = 'batch'
    },
    getTestcaseNameLocal (row) {
      getTestcaseName(row)
    },
    gotoEditPage (row) {
      this.$router.push({
        name: 'EditTestcase',
        params: {currentCase: row}
      })
    },
    // 复制用例逻辑
    okCopy () {
      var _this = this
      CopyTestcase(this.copyTestcase).then(data => {
        console.log(data)
        this.$Message.success('用例复制成功')
        this.reload()
        // 重置数据
        this.copyTestcase = {}
      }).catch(() => {
        // 同名变量处理
        changeLoadingState(_this)
      })
    }
  },
  mounted () {
    EnvList({page: 'None'}).then(data => {
      this.evnList = data
    })
    // 页面初始化请求分页数据
    this.getData(1)
  },
  created () {
    // 获取项目和模块的信息，用于搜索栏中相关字段的选项
    ProjectList({page: 'None'}).then(data => {
      data.forEach(item => {
        item.name = item.project_name
      })
      for (let i = 0; i < this.searchDict.length; i++) {
        if (this.searchDict[i].searchName === 'project') {
          this.searchDict[i].choices = data
          break
        }
      }
    })
    ModuleList({page: 'None'}).then(data => {
      data.forEach(item => {
        item.name = item.module_name
      })
      for (let i = 0; i < this.searchDict.length; i++) {
        if (this.searchDict[i].searchName === 'module') {
          this.searchDict[i].choices = data
          break
        }
      }
    })
  }
}
</script>

<style lang="less" scoped>
</style>

<template>
  <div id="PeriodicTask">
    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addPeriodicTaskModel = true">
          <Icon type="md-add" />新增
        </Button>
        <!-- <Button type="primary" size="small">
          <Icon type="ios-bug" />运行
        </Button> -->
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <!-- 新增弹窗 -->
    <Modal v-model="addPeriodicTaskModel" title="新增任务" :loading="loading" ok-text="提交" @on-ok="addPeriodicTask" width="50">
      <Form :model="periodicTaskInfo" label-position="right" ref="periodicTaskInfo" :rules="rules" :label-width="100">
        <FormItem label="任务名称" prop="name">
          <Input v-model="periodicTaskInfo.name" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="periodicTaskInfo.description" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="定时设置">
          <Row>
            <Col :span="6">
              状态：
              <i-switch v-model="periodicTaskInfo.enabled" size="large">
                <span slot="open">启用</span>
                <span slot="close">禁用</span>
              </i-switch>
            </Col>
            <Col :span="18" v-if="periodicTaskInfo.enabled">
              <Input v-model="crontab"><span slot="prepend">计划 (m/h/d/dM/MY)</span></Input>
            </Col>
          </Row>
        </FormItem>
          <FormItem label="运行环境" prop="base_url">
            <Select v-model="periodicTaskInfo.base_url">
              <Option v-for="item in evnList" :value="item.id" :key="item.env_name" v-if="item.is_valid">{{ item.env_name }}</Option>
            </Select>
          </FormItem>
        </FormItem>
          <FormItem label="项目名称" prop="project">
            <Select v-model="periodicTaskInfo.project" @on-change="getModuleByProject">
              <Option
                v-for="project in projectList"
                :value="project.id"
                :key="project.id"
              >{{ project.project_name }}</Option>
            </Select>
          </FormItem>
        <FormItem :label="'已选 ' +  String(selectedTestCaseSum) + ' 用例'">
          <TestcaseTree :moduleList="this.moduleList" ref="testCaseTree"></TestcaseTree>
        </FormItem>
        <FormItem label="邮件列表">
          <Select v-model="receiversList" multiple>
              <Option v-for="item in userList" :value="item.email" :key="item.id">{{ item.username }} [{{ item.email }}]</Option>
          </Select>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal v-model="editPeriodicTaskModel" title="修改任务" :loading="loading" ok-text="修改" @on-ok="editPeriodicTask" width="50">
      <Form :model="currentPeriodicTaskInfo" label-position="right" ref="editPeriodicTaskInfo" :rules="rules" :label-width="100">
        <FormItem label="任务名称" prop="name">
          <Input v-model="currentPeriodicTaskInfo.name" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentPeriodicTaskInfo.description" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="定时设置">
          <Row>
            <Col :span="6">
              状态：
              <i-switch v-model="currentPeriodicTaskInfo.enabled" size="large">
                <span slot="open">启用</span>
                <span slot="close">禁用</span>
              </i-switch>
            </Col>
            <Col :span="18" v-if="currentPeriodicTaskInfo.enabled">
              <Input v-model="currentPeriodicTaskInfo.crontab_time"><span slot="prepend">计划 (m/h/d/dM/MY)</span></Input>
            </Col>
          </Row>
        </FormItem>
          <FormItem label="运行环境" prop="base_url">
            <Select v-model="currentPeriodicTaskInfo.base_url">
              <Option v-for="item in evnList" :value="item.id" :key="item.env_name" v-if="item.is_valid">{{ item.env_name }}</Option>
            </Select>
          </FormItem>
        </FormItem>
          <FormItem label="项目名称" prop="project">
            <Select v-model="currentPeriodicTaskInfo.project" @on-change="getModuleByProject">
              <Option
                v-for="project in projectList"
                :value="project.id"
                :key="project.id"
              >{{ project.project_name }}</Option>
            </Select>
          </FormItem>
        <FormItem :label="'已选 ' +  String(selectedTestCaseSum) + ' 用例'">
          <TestcaseTree :moduleList="this.moduleList" ref="testCaseTree"></TestcaseTree>
        </FormItem>
        <FormItem label="邮件列表">
          <Select v-model="currentPeriodicTaskInfo.receiversList" multiple>
              <Option v-for="item in userList" :value="item.email" :key="item.id">{{ item.username }} [{{ item.email }}]</Option>
          </Select>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  PeriodicTaskList,
  AddPeriodicTask,
  EditPeriodicTask,
  PatchPeriodicTask,
  DeletePeriodicTask,
  RunPeriodicTask,
  ProjectList,
  ModuleList,
  TestcaseList,
  UserList,
  EnvList
} from '@/api/index'
import { toLocalDateTime, changeLoadingState } from '@/utils/Common'
import TestcaseTree from './TestcaseTree'
import SearchBar from '@/components/common/SearchBar'

export default {
  inject: ['reload'],
  components: {
    TestcaseTree, SearchBar
  },
  data () {
    return {
      inputLengthLimit: 100,
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
          title: '任务名称',
          key: 'name'
        },
        {
          title: '创建人',
          key: 'author',
          render: (h, params) => {
            if (params.row.task_extend) {
              return h('div', params.row.task_extend.author)
            } else {
              return h('div', '')
            }
          }
        },
        {
          title: '定时状态',
          key: 'enabled',
          render: (h, params) => {
            return h(
              // 标签名
              'i-switch',
              // 属性
              {
                props: {
                  // loading: false,
                  value: params.row.enabled,
                  size: 'large'
                },
                on: {
                  'on-change': value => {
                    let periodicTask = this.data[params.index]
                    periodicTask.enabled = value
                    let msg = value ? '启用' : '禁用'
                    PatchPeriodicTask({enabled: value}, periodicTask.id)
                      .then(() => {
                        this.$Message.success(`${msg}成功`)
                      })
                      .catch(error => {
                        console.log(error)
                        this.$Message.error(`${msg}失败，稍后再试`)
                        this.$nextTick(() => {
                          periodicTask.enabled = !value
                        })
                      })
                  }
                }
              },
              // 文本或子元素节点
              [
                h('span', { slot: 'open' }, '启用'),
                h('span', { slot: 'close' }, '禁用')
              ]
            )
          }
        },
        {
          title: 'crontab',
          key: 'crontab_time'
        },
        {
          title: '简要描述',
          key: 'description',
          render: (h, params) => {
            return h('div', {domProps: {title: params.row.description}}, params.row.description)
          }
        },
        {
          title: '创建时间',
          key: 'create_time',
          render: (h, params) => {
            if (params.row.task_extend) {
              return h('div', toLocalDateTime(params.row.task_extend.create_time))
            } else {
              return h('div', '')
            }
          }
        },
        {
          title: '更新时间',
          key: 'date_changed',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.date_changed))
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
                    size: 'small',
                    shape: 'circle'
                  },
                  domProps: {
                    title: '运行'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.$Modal.confirm({
                        title: '是否运行此任务？',
                        content: `<span class='auto-break'>任务名：${params.row.name}</span>`,
                        onOk: () => {
                          this.runPeriodicTask(params.index)
                        }
                      })
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
                    size: 'small',
                    shape: 'circle'
                  },
                  domProps: {
                    title: '编辑'
                  },
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      // 打开修改弹窗
                      this.editPeriodicTaskModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentPeriodicTaskInfo = JSON.parse(
                        JSON.stringify(this.data[params.index])
                      )
                      if (this.currentPeriodicTaskInfo.task_extend) {
                        // 系统任务无task_extend
                        let args = JSON.parse(this.currentPeriodicTaskInfo.args)
                        this.currentPeriodicTaskInfo.base_url = args[0].env
                        this.currentPeriodicTaskInfo.receiversList = args[0].receivers
                        this.currentPeriodicTaskInfo.project = this.currentPeriodicTaskInfo.task_extend.project
                        this.currentPeriodicTaskInfo.crontab_time = this.currentPeriodicTaskInfo.crontab_time.replace('(m/h/d/dM/MY)', '').trim()
                        this.getModuleByProject(this.currentPeriodicTaskInfo.task_extend.project)
                        this.$store.commit('setCaseList', args[0].case_list.case)
                        this.$store.commit('setCaseSum', args[0].case_list.case.length)
                      }
                      console.log(this.currentPeriodicTaskInfo)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-create', size: '18' } })]
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'error',
                    size: 'small',
                    shape: 'circle'
                  },
                  domProps: {
                    title: '删除'
                  },
                  on: {
                    click: () => {
                      this.deletePeriodicTask(params.index)
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
      addPeriodicTaskModel: false,
      editPeriodicTaskModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      moduleList: [],
      projectList: [],
      receiversList: [], // 选中的用例邮件列表
      userList: [], // 用户列表
      evnList: [],
      crontab: '* * * * *',
      periodicTaskInfo: {
        name: '',
        args: '[]',
        description: '',
        enabled: true,
        // crontab: { // 根据enabled来添加},
        email_list: '[]',
        author: JSON.parse(localStorage.getItem('user')).username,
        // 下面两值为了做校验才放到此处，提交前删除
        project: '',
        base_url: ''
      },
      rules: {
        name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        project: [
          {
            required: true,
            message: '请选择',
            trigger: 'change',
            type: 'number'
          }
        ],
        base_url: [
          {
            required: true,
            message: '请选择',
            trigger: 'change',
            type: 'number'
          }
        ]
      },
      currentPeriodicTaskInfo: {},
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'name',
          searchText: '任务名称'
        },
        {
          searchName: 'enabled',
          searchText: '启用状态',
          type: 'select',
          choices: [
            {name: '全部', id: ''},
            {name: '启用', id: '1'},
            {name: '禁用', id: '0'}
          ]
        },
        {
          searchName: 'author',
          searchText: '创建人'
        },
        {
          searchName: 'description',
          searchText: '简要描述'
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
      PeriodicTaskList(Object.assign({ page: page }, this.$refs.searchBar.searchConditions)).then(data => {
        // 不显示系统定义的任务
        this.data = data.results.filter(item => item.task_extend)
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addPeriodicTask () {
      var _this = this
      // 添加用例和校验
      this.$refs.testCaseTree.addTC()
      console.log(this.$store.state.caseList)
      if (this.$store.state.caseList.length === 0) {
        this.$Message.error('至少选择一个用例')
        changeLoadingState(_this)
        return
      }
      // 组装task_info
      let taskInfo = {
        case_list: {
          case: this.$store.state.caseList
        },
        env: this.periodicTaskInfo.base_url,
        report_name: this.periodicTaskInfo.name,
        description: this.periodicTaskInfo.description,
        receivers: this.receiversList
      }
      this.periodicTaskInfo.args = '[' + JSON.stringify(taskInfo) + ']'
      this.periodicTaskInfo.email_list = this.receiversList
      // 整理crontab
      // 不管是否启用，都保存crontab（默认值是* * * * *）
      let crontabTime = this.crontab.trim().split(' ')
      if (crontabTime.length !== 5) {
        this.$Message.error('crontab 格式有误')
        changeLoadingState(_this)
        return
      }
      this.periodicTaskInfo.crontab = {
        minute: crontabTime[0],
        hour: crontabTime[1],
        day_of_week: crontabTime[2],
        day_of_month: crontabTime[3],
        month_of_year: crontabTime[4]
      }

      this.$refs.periodicTaskInfo.validate(valid => {
        if (valid) {
          // 后台数据不接收base_url这个属性,所以删除
          let baseUrlTemp = this.periodicTaskInfo.base_url
          delete this.periodicTaskInfo.base_url
          // 新增任务
          AddPeriodicTask(this.periodicTaskInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addPeriodicTaskModel = false
              this.reload()
              this.$Message.success('任务创建成功')
            })
            .catch(() => {
              // 如果失败,则需要补回此属性,否则该选项显示空
              this.periodicTaskInfo.base_url = baseUrlTemp
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editPeriodicTask () {
      var _this = this
      // 添加用例和校验
      this.$refs.testCaseTree.addTC()
      console.log(this.$store.state.caseList)
      if (this.$store.state.caseList.length === 0) {
        this.$Message.error('至少选择一个用例')
        changeLoadingState(_this)
        return
      }
      // 组装task_info
      let taskInfo = {
        case_list: {
          case: this.$store.state.caseList
        },
        env: this.currentPeriodicTaskInfo.base_url,
        report_name: this.currentPeriodicTaskInfo.name,
        description: this.currentPeriodicTaskInfo.description,
        receivers: this.currentPeriodicTaskInfo.receiversList
      }
      this.currentPeriodicTaskInfo.args = '[' + JSON.stringify(taskInfo) + ']'
      // 整理crontab
      let crontabTime = this.currentPeriodicTaskInfo.crontab_time.trim().split(' ')
      this.currentPeriodicTaskInfo.email_list = this.currentPeriodicTaskInfo.receiversList
      if (crontabTime.length !== 5) {
        this.$Message.error('crontab 格式有误')
        changeLoadingState(_this)
        return
      }
      this.currentPeriodicTaskInfo.crontab = {
        minute: crontabTime[0],
        hour: crontabTime[1],
        day_of_week: crontabTime[2],
        day_of_month: crontabTime[3],
        month_of_year: crontabTime[4]
      }
      this.$refs.editPeriodicTaskInfo.validate(valid => {
        if (valid) {
          // 删除下面三个字段，后端不需要保存,如果失败后需要回显示
          let baseUrlTemp = this.currentPeriodicTaskInfo.base_url
          let crontabTimeTemp = this.currentPeriodicTaskInfo.crontab_time
          let receiversListTemp = this.currentPeriodicTaskInfo.receiversList
          delete this.currentPeriodicTaskInfo.base_url
          delete this.currentPeriodicTaskInfo.crontab_time
          delete this.currentPeriodicTaskInfo.receiversList
          // 修改任务信息
          EditPeriodicTask(this.currentPeriodicTaskInfo, this.currentPeriodicTaskInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editPeriodicTaskModel = false
              this.reload()
              this.$Message.success('任务修改成功')
            })
            .catch(() => {
              // 如果失败,则需要补回此属性,否则该选项显示空
              this.currentPeriodicTaskInfo.base_url = baseUrlTemp
              this.currentPeriodicTaskInfo.crontab_time = crontabTimeTemp
              this.currentPeriodicTaskInfo.receiversList = receiversListTemp
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deletePeriodicTask (index) {
      // 删除任务信息
      this.$Modal.confirm({
        title: '确定要删除该任务吗？',
        content: `<span class='auto-break'>任务名：${this.data[index].name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeletePeriodicTask(this.data[index].id).then(data => {
            this.$Message.success('任务删除成功')
            this.reload()
          })
        }
      })
    },
    runPeriodicTask (index) {
      console.log(this.data[index].id)
      // 手动运行任务
      RunPeriodicTask({task_id: this.data[index].id}).then(data => {
        this.$Message.info(data.message)
      })
    },
    getModuleByProject (project) {
      if (!this.addPeriodicTaskModel && !this.editPeriodicTaskModel) {
        // 关闭弹窗重置数据时，不会触发请求
        return
      }
      // 根据所选的项目，返回模块数据
      ModuleList({page: 'None', project: project}).then(data => {
        console.log('模块数据')
        // 模块列表，需要调整数据，以适配树形控件数据要求
        this.moduleList = data.map(item => {
          item.title = item.module_name
          item.loading = false
          item.children = []
          if (this.editPeriodicTaskModel) {
            // 编辑任务弹窗中，需要做用例数据回填，对每个模块做用例请求，勾选已被选中的用例。在新增任务弹窗中则是异步加载，不会走这分支
            TestcaseList({page: 'None', project: item.project, module: item.id}).then(data => {
              // 用例列表，适配树形控件
              item.children = data.map(childTiem => {
                childTiem.title = childTiem.name
                if (JSON.parse(this.currentPeriodicTaskInfo.args)[0].case_list.case.indexOf(childTiem.id) > -1) {
                  // item.expand = true 如果加了这句，打开的树节点开头图标无法正常使用
                  childTiem.checked = true
                }
                return childTiem
              })
            })
          }
          return item
        })
        console.log(this.moduleList)
      })
    }
  },
  watch: {
    addPeriodicTaskModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addPeriodicTaskModel) {
        this.$refs.periodicTaskInfo.resetFields()
        this.$store.commit('setCaseList', [])
        this.$store.commit('setCaseSum', 0)
        // 树组件也要重置
        this.moduleList = []
        this.receiversList = []
      }
    },
    editPeriodicTaskModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editPeriodicTaskModel) {
        this.$refs.editPeriodicTaskInfo.resetFields()
        this.$store.commit('setCaseList', [])
        this.$store.commit('setCaseSum', 0)
        // 树组件也要重置
        this.moduleList = []
        this.receiversList = []
      }
    }
  },
  computed: {
    selectedTestCaseSum () {
      return this.$store.state.caseSum
    }
  },
  mounted () {
    // 页面初始化请求分页数据
    this.getData(1)
    ProjectList({page: 'None'}).then(data => {
      this.projectList = data
    })
    EnvList({page: 'None'}).then(data => {
      this.evnList = data
    })
    UserList().then(data => {
      this.userList = data
    })
  }
}
</script>

<style lang="less" scoped>
.ivu-form-item {
  margin-bottom: 18px !important;
}
</style>

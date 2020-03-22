<template>
  <div id="modulelist">
    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>
    <Table :columns="columns" :data="data" :border="true" :stripe="true" @on-selection-change="getSelectedRow">
      <template slot-scope="{ row, index }" slot="count">
        <p>{{row.testcase_count}}</p>
      </template>
    </Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addModuleModel = true">
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
    <!-- 环境选择弹窗 -->
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
      <Row  style="margin-bottom: 15px;">
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
    </Modal>
    <!-- 新增弹窗 -->
    <Modal v-model="addModuleModel" title="新增模块" :loading="loading" ok-text="提交" @on-ok="addModule">
      <Form :model="moduleInfo" label-position="top" ref="moduleInfo" :rules="rules">
        <FormItem label="模块名称" prop="module_name">
          <Input v-model="moduleInfo.module_name" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="项目名称" prop="project">
          <Select v-model="moduleInfo.project" style="width:200px">
            <Option
              v-for="project in projectList"
              :value="project.id"
              :key="project.id"
            >{{ project.project_name }}</Option>
          </Select>
        </FormItem>
        <FormItem label="测试人员" prop="test_user">
          <Input v-model="moduleInfo.test_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="moduleInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal v-model="editModuleModel" title="修改模块" :loading="loading" ok-text="修改" @on-ok="editModule">
      <Form :model="currentModuleInfo" label-position="top" ref="currentModuleInfo" :rules="rules">
        <FormItem label="模块名称" prop="module_name">
          <Input v-model="currentModuleInfo.module_name" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="项目名称" prop="project">
          <Select v-model="currentModuleInfo.project" style="width:200px">
            <Option
              v-for="project in projectList"
              :value="project.id"
              :key="project.id"
            >{{ project.project_name }}</Option>
          </Select>
        </FormItem>
        <FormItem label="测试人员" prop="test_user">
          <Input v-model="currentModuleInfo.test_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentModuleInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  ModuleList,
  AddModule,
  EditModule,
  DeleteModule,
  ProjectList,
  Test,
  EnvList
} from '@/api/index'
import { toLocalDateTime, changeLoadingState } from '@/utils/Common'
import SearchBar from '@/components/common/SearchBar'

export default {
  inject: ['reload'],
  components: {
    SearchBar
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
          title: '模块名称',
          key: 'module_name'
        },
        {
          title: '所属项目',
          key: 'project_name'
        },
        {
          title: '用例数',
          slot: 'count'
        },
        {
          title: '测试人员',
          key: 'test_user'
        },
        {
          title: '简要描述',
          key: 'description'
        },
        {
          title: '创建时间',
          key: 'create_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.create_time))
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
                      // 打开修改弹窗
                      this.editModuleModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentModuleInfo = JSON.parse(
                        JSON.stringify(this.data[params.index])
                      )
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-create' } }), '编辑']
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'error',
                    size: 'small',
                    style: {}
                  },
                  on: {
                    click: () => {
                      this.deleteModule(params.index)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash' } }), '删除']
              )
            ])
          }
        }
      ],
      data: [],
      count: 0,
      addModuleModel: false,
      editModuleModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      moduleInfo: {
        module_name: '',
        project: '',
        test_user: '',
        description: ''
      },
      rules: {
        module_name: [
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
        ]
      },
      currentModuleInfo: {},
      projectList: [],
      // 选中的模块id数组
      SelectedRow: [],
      // 选择环境弹窗显示控制
      evnModel: false,
      base_url: '',
      // 环境列表
      evnList: [],
      reportName: '',
      reportDescription: '',
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'module_name',
          searchText: '模块名称'
        },
        {
          searchName: 'project',
          searchText: '项目名称',
          type: 'select',
          choices: []
        },
        {
          searchName: 'test_user',
          searchText: '测试人员'
        },
        {
          searchName: 'description',
          searchText: '简要描述'
        },
        {
          searchName: 'create_time',
          searchText: '创建时间',
          type: 'date'
        // },
        // {
        //   searchName: 'update_time',
        //   searchText: '更新时间',
        //   type: 'date'
        }
      ]
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      ModuleList(Object.assign({ page: page }, this.$refs.searchBar.searchConditions)).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addModule () {
      var _this = this
      this.$refs.moduleInfo.validate(valid => {
        if (valid) {
          // 新增模块
          AddModule(this.moduleInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addModuleModel = false
              this.reload()
              this.$Message.success('模块创建成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editModule () {
      var _this = this
      this.$refs.currentModuleInfo.validate(valid => {
        if (valid) {
          // 修改模块信息
          EditModule(this.currentModuleInfo, this.currentModuleInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editModuleModel = false
              this.reload()
              this.$Message.success('模块修改成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteModule (index) {
      // 删除模块信息
      this.$Modal.confirm({
        title: '确定要删除该模块吗？',
        content: `<span class='auto-break'>模块名：${this.data[index].module_name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteModule(this.data[index].id).then(data => {
            this.$Message.success('模块删除成功')
            this.reload()
          })
        }
      })
    },
    getSelectedRow (selection) {
      // 获取选中的行数据,并返回各行的id
      this.SelectedRow = selection.map(item => item.id)
    },
    runCaseByBatch () {
      // 批量运行用例
      // 检查是否有选中的用例
      if (this.SelectedRow.length === 0) {
        this.$Message.warning('请先选择模块')
        return
      }
      // 触发弹窗选择环境
      this.evnModel = true
    },
    ok () {
      console.log('运行的模块id: ')
      console.log(this.SelectedRow)
      // 运行环境必选
      if (this.base_url === '') {
        this.$Message.warning('请先选择运行环境')
        return
      }
      Test({
        case_list: {
          module: this.SelectedRow
        },
        env: this.base_url,
        report_name: this.reportName.trim(),
        description: this.reportDescription
      }).then(data => {
        console.log(data)
        this.$Message.info(data.message)
      })
    },
    cancel () {
      console.log('取消')
    }
  },
  watch: {
    addModuleModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addModuleModel) {
        this.$refs.moduleInfo.resetFields()
      }
    },
    editModuleModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editModuleModel) {
        this.$refs.currentModuleInfo.resetFields()
      }
    }
  },
  mounted () {
    EnvList({page: 'None'}).then(data => {
      this.evnList = data
    })
    // 页面初始化请求分页数据
    this.getData(1)
    // 请求项目信息(项目id和project_name),返回值是全部数据(包括其他字段,数据有冗余,但数据量不会太多,没事), page="None"为返回全部数据
    ProjectList({page: 'None'}).then(data => {
      this.projectList = data
      // 搜索栏的下拉框选项数据需要name属性用于显示选项文本
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
  }
}
</script>

<style lang="less" scoped>
</style>

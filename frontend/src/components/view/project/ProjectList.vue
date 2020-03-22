<template>
  <div id="projectlist">
    <Table :columns="columns" :data="data" :border="true" :stripe="true" @on-selection-change="getSelectedRow">
      <template slot-scope="{ row, index }" slot="count">
        <p>{{row.module_count}} / {{row.testcase_count}}</p>
      </template>
    </Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addProjectModel = true">
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
    <Modal
      v-model="addProjectModel"
      title="新增项目"
      :loading="loading"
      ok-text="提交"
      @on-ok="addProject"
    >
      <Form :model="projectInfo" label-position="top" ref="projectInfo" :rules="rules">
        <FormItem label="项目名称" prop="project_name">
          <Input v-model="projectInfo.project_name" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="负责人" prop="leader">
          <Input v-model="projectInfo.leader" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="测试人员" prop="test_user">
          <Input v-model="projectInfo.test_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="开发人员" prop="dev_user">
          <Input v-model="projectInfo.dev_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="projectInfo.description" :maxlength="inputLengthLimit"></Input>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal
      v-model="editProjectModel"
      title="修改项目"
      :loading="loading"
      ok-text="修改"
      @on-ok="editProject"
    >
      <Form
        :model="currentProjectInfo"
        label-position="top"
        ref="currentProjectInfo"
        :rules="rules"
      >
        <FormItem label="项目名称" prop="project_name">
          <Input v-model="currentProjectInfo.project_name" disabled></Input>
        </FormItem>
        <FormItem label="负责人" prop="leader">
          <Input v-model="currentProjectInfo.leader" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="测试人员">
          <Input v-model="currentProjectInfo.test_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="开发人员">
          <Input v-model="currentProjectInfo.dev_user" :maxlength="inputLengthLimit"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentProjectInfo.description" :maxlength="inputLengthLimit"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  ProjectList,
  AddProject,
  EditProject,
  DeleteProject,
  Test,
  EnvList
} from '@/api/index'
import { toLocalDateTime, changeLoadingState } from '@/utils/Common'

export default {
  inject: ['reload'],
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
          title: '项目名称',
          key: 'project_name'
        },
        {
          title: '模块/用例数',
          slot: 'count'
        },
        {
          title: '负责人',
          key: 'leader'
        },
        {
          title: '测试人员',
          key: 'test_user'
        },
        {
          title: '开发人员',
          key: 'dev_user'
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
                      this.editProjectModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentProjectInfo = JSON.parse(
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
                      this.deleteProject(params.index)
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
      addProjectModel: false,
      editProjectModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      projectInfo: {
        project_name: '',
        leader: '',
        test_user: '',
        dev_user: '',
        description: ''
      },
      rules: {
        project_name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        leader: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ]
      },
      currentProjectInfo: {},
      // 选中的模块id数组
      SelectedRow: [],
      // 选择环境弹窗显示控制
      evnModel: false,
      base_url: '',
      // 环境列表
      evnList: [],
      reportName: '',
      reportDescription: ''
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      ProjectList({ page: page }).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addProject () {
      var _this = this
      this.$refs.projectInfo.validate(valid => {
        if (valid) {
          // 新增项目
          AddProject(this.projectInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addProjectModel = false
              this.reload()
              this.$Message.success('项目创建成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editProject () {
      var _this = this
      this.$refs.currentProjectInfo.validate(valid => {
        if (valid) {
          // 修改项目信息
          EditProject(this.currentProjectInfo, this.currentProjectInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editProjectModel = false
              this.reload()
              this.$Message.success('项目修改成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteProject (index) {
      // 删除项目信息
      this.$Modal.confirm({
        title: '确定要删除该项目吗？',
        content: `<span class='auto-break'>项目名：${this.data[index].project_name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteProject(this.data[index].id).then(data => {
            this.$Message.success('项目删除成功')
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
        this.$Message.warning('请先选择项目')
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
          project: this.SelectedRow
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
    addProjectModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addProjectModel) {
        this.$refs.projectInfo.resetFields()
      }
    },
    editProjectModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editProjectModel) {
        this.$refs.currentProjectInfo.resetFields()
      }
    }
  },
  created () {
    EnvList({page: 'None'}).then(data => {
      this.evnList = data
    })
    // 页面初始化请求分页数据
    this.getData(1)
  }
}
</script>

<style lang="less" scoped>
</style>

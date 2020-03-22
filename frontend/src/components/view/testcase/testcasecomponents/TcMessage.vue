<template>
  <div id="tcmessage">
    <Form
      :model="messageForm"
      label-position="right"
      ref="messageForm"
      :label-width="80"
    >
      <Row :gutter="40">
        <Col :span="12">
          <FormItem label="用例名称" prop="name">
            <Input v-model="name" :maxlength="100"></Input>
          </FormItem>
          <FormItem label="项目名称" prop="project">
            <Select v-model="project" @on-change="getModuleByProject">
              <Option
                v-for="project in projectList"
                :value="project.id"
                :key="project.id"
              >{{ project.project_name }}</Option>
            </Select>
          </FormItem>
          <FormItem label="模块名称" prop="module">
            <Select v-model="module">
              <Option
                v-for="module in moduleList"
                :value="module.id"
                :key="module.id"
              >{{ module.module_name }}</Option>
            </Select>
          </FormItem>
          <!-- 前后置步骤下拉菜单 -->
          <FormItem>
            <TcExtendStepTree :moduleList="this.moduleList"></TcExtendStepTree>
          </FormItem>
        </Col>
        <Col :span="12">
          <div>
            <TcExtendStepTable actionsname="Before" :testcaseSteps="testcaseSteps"></TcExtendStepTable>
            <TcExtendStepTable actionsname="After" :testcaseSteps="testcaseSteps"></TcExtendStepTable>
          </div>
        </Col>
      </Row>
    </Form>
  </div>
</template>

<script>
import {
  ModuleList,
  ProjectList
} from '@/api/index'
import TcExtendStepTree from './tcExtendStepComponents/TcExtendStepTree'
import TcExtendStepTable from './tcExtendStepComponents/TcExtendStepTable'

export default {
  name: 'tcmessage',
  components: {
    TcExtendStepTree,
    TcExtendStepTable
  },
  data () {
    return {
      // 本地表单对象，主要存储本地数据并验证
      messageForm: {
        name: '',
        project: '',
        module: ''
      },
      rules: {
        // 改为由代码逻辑保证字段完整性
        project: [
          {
            required: true,
            message: '请选择所属项目',
            trigger: 'change',
            type: 'number'
          }
        ],
        name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        module: [
          {
            required: true,
            message: '请选择所属模块',
            trigger: 'change',
            type: 'number'
          }
        ]
      },
      projectList: [],
      moduleList: [],
      testcaseSteps: {} // 保存用例前后置步骤，传给子组件作共享数据
    }
  },
  computed: {
    name: {
      get () {
        return this.$store.state.msgObj.name
      },
      set (value) {
        // 给本地表单对象赋值，并提交到vuex
        this.messageForm.name = value
        this.$store.commit('setName', value)
      }
    },
    project: {
      get () {
        return this.$store.state.msgObj.project
      },
      set (value) {
        this.messageForm.project = value
        this.$store.commit('setProject', value)
      }
    },
    module: {
      get () {
        return this.$store.state.msgObj.module
      },
      set (value) {
        this.messageForm.module = value
        this.$store.commit('setModule', value)
      }
    }
  },
  methods: {
    getModuleByProject (project) {
      // 根据所选的项目，返回模块数据
      ModuleList({page: 'None', project: project}).then(data => {
        console.log('模块数据')
        // 模块列表，需要调整数据，以适配树形控件数据要求
        this.moduleList = data.map(item => {
          item.title = item.module_name
          item.loading = false
          item.children = []
          return item
        })
        console.log(this.moduleList)
      })
    }
  },
  created () {
    // 请求项目信息(项目id和project_name),返回值是全部数据(包括其他字段,数据有冗余,但数据量不会太多,没事), page="None"为返回全部数据
    ProjectList({page: 'None'}).then(data => {
      this.projectList = data
    })
  }
}
</script>

<style lang="less" scoped>
</style>

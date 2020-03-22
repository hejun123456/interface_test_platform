<template>
  <div id="edittestcase">
    <Tabs type="card">
      <TabPane label="message">
        <TcMessage ref="tcmsg"></TcMessage>
      </TabPane>
      <TabPane label="variables">
        <TcVariables></TcVariables>
      </TabPane>
      <TabPane label="parameters">
        <TcParameters></TcParameters>
      </TabPane>
      <TabPane label="hooks">
        <TcHooks hookname="SetupHook"></TcHooks>
        <br />
        <TcHooks hookname="TeardownHook"></TcHooks>
      </TabPane>
      <TabPane label="request">
        <TcRequest></TcRequest>
      </TabPane>
      <TabPane label="extract/validate">
        <TcExtractValidate></TcExtractValidate>
      </TabPane>
    </Tabs>
    <br />
    <Row>
      <Col :span="12">
        <Button type="info" @click="debugTC">调试</Button>
        <Button type="success" @click="saveTC">保存</Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Button type="warning" @click="cancelTC">取消</Button>
      </Col>
    </Row>
    <template v-if="showDebug">
      <hr style="margin: 10px 0;" />
      <div style="margin-bottom: 10px;">
        <Button type="info" @click="clearDebug">清空结果</Button>
        <!-- 提取按钮只针对最后一个响应页有效 -->
        <Button type="info" @click="getSelectedData">提取数据</Button>
      </div>
      <Tabs type="card" :value="String(treeData.length-1)">
        <template v-for="(item, index) in treeData">
            <TabPane
              :label="caseMetas[index].flag ? rightLabel(String(index+1), caseMetas[index].name) : wrongLabel(String(index+1), caseMetas[index].name)"
              :key="index" :name="String(index)">
              <!-- 无论对错，均显示断言信息 -->
              <template v-if="true">
                <!-- 报错的响应页，会显示当前响应的分析信息 -->
                <template v-if="!caseMetas[index].flag">
                  <Button type="warning" @click="traceback = !traceback">Traceback</Button>
                </template>
                <Button type="info" @click="validators = !validators">Validators</Button>
                <Row :gutter="32">
                  <Col :span="12">
                    <div v-if="traceback" class="traceback">
                      <pre class="validatorPre">
{{caseMetas[index].attachment}}
                      </pre>
                    </div>
                  </Col>
                  <Col :span="12">
                    <div v-if="validators" class="validators">
                      <Collapse style="border: none;">
                        <template v-for="(validator, vindex) in caseMetas[index].validators">
                          <Panel :name="String(vindex)" :key="vindex" :style="{background: validator.check_result === 'pass' ? '' : 'red'}">
                            {{`第${vindex+1}项 -- ${validator.check}`}}
<pre slot="content" :key="vindex" class="validatorPre">
{{`【变量】:${validator.check}
【检查内容】:${validator.expect}(期望值|${typeof validator.expect}) ${validator.comparator} ${validator.check_value}(实际值|${typeof validator.check_value})
【检查结果】:${validator.check_result}`}}
</pre>
                          </Panel>
                        </template>
                      </Collapse>
                    </div>
                  </Col>
                </Row>
              </template>
              <Tree :data="item" :show-checkbox="caseMetas[index].name === '当前请求'" :ref="caseMetas[index].name === '当前请求' ? 'tree' : ''"></Tree>
            </TabPane>
        </template>
      </Tabs>
    </template>
    <Modal v-model="evnModel" title="选择运行环境" @on-ok="ok" @on-cancel="cancel">
      <Row>
        <Col :span="5">
          <label style="display: inline-block; line-height: 30px; font-size: 16px;">
            <span style="display: inline-block; line-height: 30px; font-size: 16px; color: red;">*</span>
            运行环境：
          </label>
        </Col>
        <Col :span="19">
          <Select v-model="testcaseInfo.base_url">
            <Option v-for="item in evnList" :value="item.base_url" :key="item.env_name" v-if="item.is_valid">{{ item.env_name }}</Option>
          </Select>
        </Col>
      </Row>
    </Modal>
  </div>
</template>

<script>
import TcMessage from './testcasecomponents/TcMessage'
import TcVariables from './testcasecomponents/TcVariables'
import TcParameters from './testcasecomponents/TcParameters'
import TcHooks from './testcasecomponents/TcHooks'
import TcRequest from './testcasecomponents/TcRequest'
import TcExtractValidate from './testcasecomponents/TcExtractValidate'
import { EditTestcase, GetTestcase } from '@/api/index'
import { getDataType, getTestcaseName } from '@/utils/Common'
import TestcaeMixin from './TestcaeMixin'

export default {
  mixins: [TestcaeMixin],
  name: 'edittestcase',
  components: {
    TcMessage,
    TcVariables,
    TcParameters,
    TcHooks,
    TcRequest,
    TcExtractValidate
  },
  data () {
    return {
      caseId: '',
      traceback: false,
      validators: false,
      // 树数据
      treeData: [],
      caseMetas: [],
      // 选择环境弹窗显示控制
      evnModel: false,
      // 环境列表
      evnList: [],
      // 调试页显示控制
      showDebug: false,
      // 用例信息对象
      testcaseInfo: {
        // type：默认为1
        type: 1,
        // 作者
        author: JSON.parse(localStorage.getItem('user')).username,
        // 用例名
        name: '',
        // 前置步骤和配置
        before: '[]',
        // 后置步骤
        after: '[]',
        // 请求信息
        request: {},
        // 参数文件列表
        params_files: '[]',
        // 项目和模块
        project: '',
        module: '',
        base_url: ''
      }
    }
  },
  methods: {
    saveTC () {
      // 组装用例对象  packageTC没有回填id（因为新增用例也调用此方法）
      let tc = this.packageTC()
      // 如果tc等于0，直接返回不发请求
      if (tc === 0) return
      tc.id = this.caseId
      // 发送请求，保存用例
      EditTestcase(tc, this.caseId)
        .then(data => {
          this.$Message.success('用例修改成功')
          this.$router.replace({ name: 'TestcaseList' })
        })
    },
    backfillTC (tc) {
      /**
       * tc 用例对象
       */
      console.log('回填用例数据到vuex')
      console.log(tc)
      let requestInfo = JSON.parse(tc.request)
      let before = JSON.parse(tc.before)
      let after = JSON.parse(tc.after)
      // 用例名
      this.$store.commit('setName', tc.name)
      // 项目和模块
      this.$store.commit('setProject', tc.project)
      this.$store.commit('setModule', tc.module)
      // variables 变量
      if (requestInfo.test.variables) {
        requestInfo.test.variables.forEach(item => {
          for (let k in item) {
            this.variables.push({
              id: Math.random().toString(),
              var_name: k,
              var_type: getDataType(item[k]),
              var_value: item[k],
              editable: false
            })
          }
        })
      }
      // parameters 参数化
      if (requestInfo.test.parameters) {
        requestInfo.test.parameters.forEach(item => {
          for (let k in item) {
            this.parameters.push({
              id: Math.random().toString(),
              param_name: k,
              param_value: item[k].indexOf('${P') > -1 ? tc.project_name + '/' + item[k].replace('${P(', '').replace(')}', '') : JSON.stringify(item[k]),
              editable: false,
              isFile: item[k].indexOf('${P') > -1
            })
          }
        })
      }
      // setup_hooks
      if (requestInfo.test.setup_hooks) {
        requestInfo.test.setup_hooks.forEach(item => {
          this.setupHooks.push({
            id: Math.random().toString(),
            hook: item,
            editable: false
          })
        })
      }
      // teardown_hooks
      if (requestInfo.test.teardown_hooks) {
        requestInfo.test.teardown_hooks.forEach(item => {
          this.tearHooks.push({
            id: Math.random().toString(),
            hook: item,
            editable: false
          })
        })
      }
      // url method data
      this.$store.commit('setUrl', requestInfo.test.request.url)
      this.$store.commit('setMethod', requestInfo.test.request.method)
      if (requestInfo.test.request.json) {
        this.$store.commit('setDataType', 'json')
        this.$store.commit('setJson', requestInfo.test.request.json)
      } else if (requestInfo.test.request.data) {
        // data
        for (let k in requestInfo.test.request.data) {
          this.reqData.push({
            id: Math.random().toString(),
            data_name: k,
            data_type: getDataType(requestInfo.test.request.data[k]),
            data_value: requestInfo.test.request.data[k],
            editable: false
          })
        }
      }
      // headers
      if (requestInfo.test.request.headers) {
        for (let k in requestInfo.test.request.headers) {
          this.headers.push({
            id: Math.random().toString(),
            header_name: k,
            header_value: requestInfo.test.request.headers[k],
            editable: false
          })
        }
      }
      // params
      if (requestInfo.test.request.params) {
        for (let k in requestInfo.test.request.params) {
          this.reqParams.push({
            id: Math.random().toString(),
            param_name: k,
            param_value: requestInfo.test.request.params[k],
            editable: false
          })
        }
      }
      // extract
      if (requestInfo.test.extract) {
        requestInfo.test.extract.forEach(item => {
          for (let k in item) {
            this.extract.push({
              id: Math.random().toString(),
              extract_name: k,
              extract_value: item[k],
              editable: false
            })
          }
        })
      }
      // extract
      if (requestInfo.test.validate) {
        requestInfo.test.validate.forEach(item => {
          this.validate.push({
            id: Math.random().toString(),
            check: item.check,
            comparator: item.comparator,
            validate_type: getDataType(item.expected),
            expected: item.expected,
            editable: false
          })
        })
      }
      // before
      if (before.length > 0) {
        before.forEach(item => {
          this.before.push({
            id: item[0],
            name: item[1]
          })
        })
      }
      // after
      if (after.length > 0) {
        after.forEach(item => {
          this.after.push({
            id: item[0],
            name: item[1]
          })
        })
      }
    },
    async initData () {
      // await把异步函数在async装饰的作用域内变成同步函数/操作
      // 被async装饰的函数在外部调用时是作用异步函数,所以如果需要再次封装成同步操作,同样使用async/await
      // 保证数据更新后再跳转
      // await getTestcaseName(row)
      // 待编辑数据传入vuex
      if (typeof this.$route.params.currentCase === 'object') {
        await getTestcaseName(this.$route.params.currentCase)
        // 从用例表格跳转到编辑页，传入用例数据
        this.caseId = this.$route.params.currentCase.id
        this.backfillTC(this.$route.params.currentCase)
        // created中子组件未挂载，无法调用子组件。
        this.$refs.tcmsg.getModuleByProject(this.$refs.tcmsg.project)
      } else {
        // 前后置步骤的用例跳转编辑页，只传入id，需要请求用例数据
        GetTestcase(this.$route.params.currentCase).then(data => {
          // 需要同步操作,所以设置为自调用异步函数
          (async (data) => {
            await getTestcaseName(data)
            this.backfillTC(data)
            this.caseId = data.id
            this.$refs.tcmsg.getModuleByProject(this.$refs.tcmsg.project)
          })(data)
        })
      }
    }
  },
  mounted () {
    this.initData()
  },
  computed: {
    parameters: {
      get () {
        return this.$store.state.parameters
      },
      set (value) {
        this.$store.commit('setParameters', value)
      }
    },
    variables: {
      get () {
        return this.$store.state.variables
      },
      set (value) {
        this.$store.commit('setVariables', value)
      }
    },
    setupHooks: {
      get () {
        return this.$store.state.SetupHook
      },
      set (value) {
        this.$store.commit('setSetupHook', value)
      }
    },
    tearHooks: {
      get () {
        return this.$store.state.TeardownHook
      },
      set (value) {
        this.$store.commit('setTeardownHook', value)
      }
    },
    reqData: {
      get () {
        return this.$store.state.data
      },
      set (value) {
        this.$store.commit('setData', value)
      }
    },
    headers: {
      get () {
        return this.$store.state.headers
      },
      set (value) {
        this.$store.commit('setHeaders', value)
      }
    },
    reqParams: {
      get () {
        return this.$store.state.params
      },
      set (value) {
        this.$store.commit('setParams', value)
      }
    },
    before: {
      get () {
        return this.$store.state.before
      },
      set (value) {
        this.$store.commit('setBefore', value)
      }
    },
    after: {
      get () {
        return this.$store.state.after
      },
      set (value) {
        this.$store.commit('setAfter', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
.traceback, .validators {
  background: #f7f7f7;
  border: 2px solid #dedede;
  padding: 10px;
  margin: 5px 0;
  border-radius: 5px;
}
.validatorPre {
  margin: 0 !important;
  white-space:pre-wrap; /* css3.0 */
  white-space:-moz-pre-wrap; /* Firefox */
  white-space:-pre-wrap; /* Opera 4-6 */
  white-space:-o-pre-wrap; /* Opera 7 */
  word-wrap:break-word; /* Internet Explorer 5.5+ */
}
.ivu-collapse-header {
  color: #313131 !important;
}
</style>

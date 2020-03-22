<template>
  <div id="addtestcase">
    <Tabs type="card">
      <TabPane label="message">
        <TcMessage></TcMessage>
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
import { AddTestcase } from '@/api/index'
import TestcaeMixin from './TestcaeMixin'

export default {
  mixins: [TestcaeMixin],
  name: 'addtestcase',
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
      // 组装用例对象
      let tc = this.packageTC()
      console.log(tc)
      // 如果tc等于0，直接返回不发请求
      if (tc === 0) return
      // 发送请求，保存用例
      AddTestcase(tc)
        .then(data => {
          this.$Message.success('用例保存成功')
          this.$router.replace({ name: 'TestcaseList' })
        })
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

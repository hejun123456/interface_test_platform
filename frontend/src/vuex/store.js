import Vue from 'vue'
import Vuex from 'vuex'
import actions from './actions'
import getters from './getters'
import mutations from './mutations'

Vue.use(Vuex)

// 应用初始状态
const state = {
  // hasMsg 检查当前是否存在msg提示框
  hasMsg: false,
  // 函数列表及请求数据控制
  hooksListReqTime: 0,
  hooksList: [],
  msgObj: {
    name: '',
    author: '',
    project: '',
    module: ''
  },
  variables: [],
  parameters: [],
  SetupHook: [],
  TeardownHook: [],
  url: '',
  method: 'GET',
  headers: [],
  params: [],
  data: [],
  json: `{"key": "value"}`,
  // dataType: 判断json或data的变量
  dataType: 'data',
  extract: [],
  validate: [],
  // 前后置步骤
  before: [],
  after: [],
  // 定时任务界面选择的用例集
  caseList: [],
  // 记录选中的用例数，实时更新
  caseSum: 0
}

// 创建 store 实例
export default new Vuex.Store({
  actions,
  getters,
  state,
  mutations
})

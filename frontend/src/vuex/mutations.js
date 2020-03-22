// 定义所需的 mutations
export default {
  setMsgObj (state, value) {
    // 此方法主要用于重置此对象，一般不用于对其中属性赋值
    state.msgObj = value
  },
  setName (state, value) {
    state.msgObj.name = value
  },
  setProject (state, value) {
    state.msgObj.project = value
  },
  setModule (state, value) {
    state.msgObj.module = value
  },
  setAuthor (state, value) {
    // 最后在保存用例时，调用。把当前用例保存下来
    state.msgObj.author = value
  },
  setVariables (state, value) {
    state.variables = value
  },
  setParameters (state, value) {
    state.parameters = value
  },
  setSetupHook (state, value) {
    state.SetupHook = value
  },
  setTeardownHook (state, value) {
    state.TeardownHook = value
  },
  setHooksList (state, value) {
    state.hooksList = value
  },
  setHooksListReqTime (state, value) {
    state.hooksListReqTime = value
  },
  //   url: '',
  setUrl (state, value) {
    state.url = value
  },
  // method: '',
  setMethod (state, value) {
    state.method = value
  },
  // headers: [],
  setHeaders (state, value) {
    state.headers = value
  },
  // params: [],
  setParams (state, value) {
    state.params = value
  },
  // data: []
  setData (state, value) {
    state.data = value
  },
  setJson (state, value) {
    state.json = value
  },
  setDataType (state, value) {
    state.dataType = value
  },
  setExtract (state, value) {
    state.extract = value
  },
  setValidate (state, value) {
    state.validate = value
  },
  setBefore (state, value) {
    state.before = value
  },
  setAfter (state, value) {
    state.after = value
  },
  setCaseList (state, value) {
    state.caseList = value
  },
  setCaseSum (state, value) {
    state.caseSum = value
  },
  setHasMsg (state, value) {
    state.hasMsg = value
  }
}

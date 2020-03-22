import { Debug, EnvList } from '@/api/index'

// 新增和编辑用例的通用配置或方法
export default {
  beforeRouteLeave (to, from, next) {
    // 退出此页面后，清空临时保存的数据
    this.$store.commit('setMsgObj', {
      name: '',
      author: '',
      project: '',
      module: ''
    })
    this.$store.commit('setVariables', [])
    this.$store.commit('setParameters', [])
    this.$store.commit('setSetupHook', [])
    this.$store.commit('setTeardownHook', [])
    this.$store.commit('setHooksListReqTime', 0)
    this.$store.commit('setHooksList', [])
    this.$store.commit('setUrl', '')
    this.$store.commit('setMethod', 'GET')
    this.$store.commit('setHeaders', [])
    this.$store.commit('setParams', [])
    this.$store.commit('setData', [])
    this.$store.commit('setJson', { key: 'value' })
    this.$store.commit('setDataType', 'data')
    this.$store.commit('setExtract', [])
    this.$store.commit('setValidate', [])
    this.$store.commit('setBefore', [])
    this.$store.commit('setAfter', [])
    // 正常跳转
    next()
  },
  methods: {
    cancelTC () {
      this.$router.replace({ name: 'TestcaseList' })
    },
    packageTC (isDebug = false) {
      // // 用例名
      if (this.$store.state.msgObj.name === '' || this.$store.state.msgObj.name === undefined) {
        this.$Message.error('用例名不能为空')
        return 0
      } else {
        this.testcaseInfo.name = this.$store.state.msgObj.name
      }
      // // 项目和模块
      if (this.$store.state.msgObj.project === '' || this.$store.state.msgObj.project === undefined) {
        this.$Message.error('项目不能为空')
        return 0
      } else {
        this.testcaseInfo.project = this.$store.state.msgObj.project
      }
      if (this.$store.state.msgObj.module === '' || this.$store.state.msgObj.module === undefined) {
        this.$Message.error('模块不能为空')
        return 0
      } else {
        this.testcaseInfo.module = this.$store.state.msgObj.module
      }
      //   // 前置步骤和配置
      //   before: '[]',
      //   // 后置步骤
      //   after: '[]',
      //   // 请求信息
      //   request: {
      //     'test': {}
      //   },
      let requestInfo = {
        test: {
          name: isDebug ? '当前请求' : this.$store.state.msgObj.name, // debug模式下,用例名为当前请求,否则为实际名
          request: {
            // url可为空
            url: this.$store.state.url,
            // method带默认值
            method: this.$store.state.method
          }
        }
      }
      // headers
      if (this.$store.state.headers.length > 0) {
        // header_name 不为空
        let headers = {}
        let headerNameCheck = false // 用于中止函数的标记
        for (let i = 0; i < this.$store.state.headers.length; i++) {
          if (this.$store.state.headers[i].header_name.trim() !== '') {
            headers[this.$store.state.headers[i].header_name] = this.$store.state.headers[i].header_value
          } else {
            this.$Message.error('header名不能为空')
            headerNameCheck = true
            break
          }
        }
        if (headerNameCheck) return 0
        requestInfo.test.request.headers = headers
      }
      // params
      if (this.$store.state.params.length > 0) {
        // params_name 不为空
        let params = {}
        let paramNameCheck = false // 用于中止函数的标记
        for (let i = 0; i < this.$store.state.params.length; i++) {
          if (this.$store.state.params[i].param_name.trim() !== '') {
            params[this.$store.state.params[i].param_name] = this.$store.state.params[i].param_value
          } else {
            this.$Message.error('param名不能为空')
            paramNameCheck = true
            break
          }
        }
        if (paramNameCheck) return 0
        requestInfo.test.request.params = params
      }
      // json或data
      if (this.$store.state.dataType === 'json') {
        if (typeof this.$store.state.json !== 'string') {
          // 未修改时为对象，修改后为字串，所以统一处理成字串
          this.$store.commit('setJson', JSON.stringify(this.$store.state.json))
        }
        try {
          let jsonObj = JSON.parse(this.$store.state.json)
          requestInfo.test.request.json = jsonObj
        } catch (e) {
          this.$Message.error('json格式不正确')
          return 0
        }
      } else {
        if (this.$store.state.data.length > 0) {
          // data_name 不为空
          let data = {}
          let dataNameCheck = false // 用于中止函数的标记
          for (let i = 0; i < this.$store.state.data.length; i++) {
            if (this.$store.state.data[i].data_name.trim() !== '') {
              let value = null
              // 数据类型转换
              switch (this.$store.state.data[i].data_type) {
                case 'string':
                  value = String(this.$store.state.data[i].data_value)
                  break
                case 'int':
                  value = parseInt(this.$store.state.data[i].data_value)
                  if (isNaN(value)) { value = String(this.$store.state.data[i].data_value) }
                  break
                case 'float':
                  value = parseFloat(this.$store.state.data[i].data_value)
                  if (isNaN(value)) { value = String(this.$store.state.data[i].data_value) }
                  break
                case 'boolean':
                  value = String(this.$store.state.data[i].data_value).toLocaleLowerCase() === 'true'
                  break
              }
              data[this.$store.state.data[i].data_name] = value
            } else {
              this.$Message.error('data名不能为空')
              dataNameCheck = true
              break
            }
          }
          if (dataNameCheck) return 0
          requestInfo.test.request.data = data
        }
      }
      // variables
      if (this.$store.state.variables.length > 0) {
        let variables = [] // 临时保存
        let nameCheck = false
        for (let i = 0; i < this.$store.state.variables.length; i++) {
          if (this.$store.state.variables[i].var_name.trim() !== '') {
            let value = null
            // 数据类型转换
            switch (this.$store.state.variables[i].var_type) {
              case 'string':
                value = String(this.$store.state.variables[i].var_value)
                break
              case 'int':
                value = parseInt(this.$store.state.variables[i].var_value)
                if (isNaN(value)) { value = String(this.$store.state.variables[i].var_value) }
                break
              case 'float':
                value = parseFloat(this.$store.state.variables[i].var_value)
                if (isNaN(value)) { value = String(this.$store.state.variables[i].var_value) }
                break
              case 'boolean':
                value = String(this.$store.state.variables[i].var_value).toLocaleLowerCase() === 'true'
                break
            }
            let obj = {} // 临时对象
            obj[this.$store.state.variables[i].var_name] = value
            variables.push(obj)
          } else {
            this.$Message.error('变量名不能为空')
            nameCheck = true
            break
          }
        }
        if (nameCheck) return 0
        requestInfo.test.variables = variables
      }
      // parameters
      if (this.$store.state.parameters.length > 0) {
        let parameters = [] // 临时保存
        let paramsFiles = []
        let nameCheck = false
        for (let i = 0; i < this.$store.state.parameters.length; i++) {
          if (this.$store.state.parameters[i].param_name.trim() !== '') {
            let value = null
            let obj = {} // 临时对象
            // 判断是否为参数文件
            if (this.$store.state.parameters[i].isFile) {
              // 参数文件，只保留文件名
              value = this.$store.state.parameters[i].param_value.split('/')[1]
              if (paramsFiles.indexOf(value) === -1) { paramsFiles.push(value) } // 保存文件名
              obj[this.$store.state.parameters[i].param_name] = '${P(' + value + ')}' // 保存到params对象中
            } else {
              // 非文件，要求格式是列表
              try {
                // 字串转换列表
                // eslint-disable-next-line no-eval
                value = eval('(' + this.$store.state.parameters[i].param_value + ')')
                if (typeof value !== typeof []) {
                  this.$Message.error('参数值格式必须为列表')
                  nameCheck = true
                  break
                }
                obj[this.$store.state.parameters[i].param_name] = value
              } catch (e) {
                console.log(e)
                this.$Message.error('参数值格式必须为列表')
                nameCheck = true
                break
              }
            }
            parameters.push(obj)
          } else {
            this.$Message.error('参数名不能为空')
            nameCheck = true
            break
          }
        }
        if (nameCheck) return 0
        requestInfo.test.parameters = parameters
        this.testcaseInfo.params_files = JSON.stringify(paramsFiles) // 保存参数文件名列表
      } else {
        this.testcaseInfo.params_files = '[]'
      }
      // setup_hooks
      if (this.$store.state.SetupHook.length > 0) {
        let setupHooks = []
        this.$store.state.SetupHook.map(item => {
          if (item.hook !== '') setupHooks.push(item.hook)
        })
        if (setupHooks.length > 0) requestInfo.test.setup_hooks = setupHooks
      }
      // teardown_hooks
      if (this.$store.state.TeardownHook.length > 0) {
        let teardownHooks = []
        this.$store.state.TeardownHook.map(item => {
          if (item.hook !== '') teardownHooks.push(item.hook)
        })
        if (teardownHooks.length > 0) requestInfo.test.teardown_hooks = teardownHooks
      }
      // extract
      if (this.$store.state.extract.length > 0) {
        // extract_name 不为空
        let extract = []
        let nameCheck = false // 用于中止函数的标记
        for (let i = 0; i < this.$store.state.extract.length; i++) {
          if (this.$store.state.extract[i].extract_name.trim() !== '') {
            let obj = {}
            obj[this.$store.state.extract[i].extract_name] = this.$store.state.extract[i].extract_value
            extract.push(obj)
          } else {
            this.$Message.error('提取变量名不能为空')
            nameCheck = true
            break
          }
        }
        if (nameCheck) return 0
        requestInfo.test.extract = extract
      }
      // validate
      if (this.$store.state.validate.length > 0) {
        // check 不为空
        let validate = []
        let nameCheck = false // 用于中止函数的标记
        for (let i = 0; i < this.$store.state.validate.length; i++) {
          if (this.$store.state.validate[i].check.trim() !== '') {
            let { ...obj } = this.$store.state.validate[i] // 扩展运算符  深拷贝对象
            // 修正期望值的类型
            let value = null
            switch (obj.validate_type) {
              case 'string':
                value = String(obj.expected)
                break
              case 'int':
                value = parseInt(obj.expected)
                if (isNaN(value)) { value = String(obj.expected) }
                break
              case 'float':
                value = parseFloat(obj.expected)
                if (isNaN(value)) { value = String(obj.expected) }
                break
              case 'boolean':
                value = String(obj.expected).toLocaleLowerCase() === 'true'
                break
            }
            obj.expected = value
            // 删除对象中的id、editable、validate_type
            delete obj.id
            delete obj.editable
            delete obj.validate_type
            validate.push(obj)
          } else {
            this.$Message.error('校验的变量名不能为空')
            nameCheck = true
            break
          }
        }
        if (nameCheck) return 0
        requestInfo.test.validate = validate
      }
      // before
      if (this.$store.state.before.length > 0) {
        let beforeList = []
        for (let i = 0; i < this.$store.state.before.length; i++) {
          beforeList.push([this.$store.state.before[i].id, this.$store.state.before[i].name])
        }
        this.testcaseInfo.before = JSON.stringify(beforeList)
      } else {
        this.testcaseInfo.before = '[]'
      }
      // after
      if (this.$store.state.after.length > 0) {
        let afterList = []
        for (let i = 0; i < this.$store.state.after.length; i++) {
          afterList.push([this.$store.state.after[i].id, this.$store.state.after[i].name])
        }
        this.testcaseInfo.after = JSON.stringify(afterList)
      } else {
        // 因为testcaseInfo是本地对象，如果添加前后置用例调试过一次后，步骤就会被添加到本地对象中，
        // 此时再删除前后置步骤，只是删除了共享数据中的前后置步骤，而非本地对象，所以要对共享数据中前后置步骤数检查，为0时，要清空本地对象中的前后置步骤数据
        this.testcaseInfo.after = '[]'
      }
      // 添加请求信息到用例对象中
      this.testcaseInfo.request = JSON.stringify(requestInfo)
      // 返回组装好的用例对象
      return this.testcaseInfo
    },
    ok () {
      // 调试用例
      // 运行环境必选
      if (this.testcaseInfo.base_url === '') {
        this.$Message.warning('请先选择运行环境')
        return
      }
      // 组装用例对象
      let tc = this.packageTC(true)
      // 如果是新增页，则无caseId，而编辑则有caseId
      if (this.caseId !== undefined) {
        tc.id = this.caseId
      }
      console.log(tc)
      // 如果tc等于0，直接返回不发请求
      if (tc === 0) return
      this.$Message.success('调试请求已发送')
      Debug(tc).then(data => {
        console.log(data)
        // 取响应数据，取最后一个
        this.treeData = data.tree
        this.caseMetas = data.case_metas
        // 显示调试结果
        this.showDebug = true
      })
    },
    cancel () {
      console.log('取消debug')
    },
    clearDebug () {
      // 关闭错误信息显示
      this.traceback = false
      this.validators = false
      // 清空已有的调试结果
      this.showDebug = false
    },
    debugTC () {
      this.clearDebug()
      // 触发弹窗选择环境
      this.evnModel = true
    },
    // 定义响应的正确和错误标签
    rightLabel (index, reqName) {
      return (h) => {
        return h('div', {style: {color: 'green'}}, [ // '#19be6b'
          h('Icon', {
            props: {
              type: 'md-checkmark-circle'
            }
          }),
          h('span', `响应${index}:` + reqName)
        ])
      }
    },
    wrongLabel (index, reqName) {
      return (h) => {
        return h('div', {style: {color: 'red'}}, [ // '#ed4014'
          h('Icon', {
            props: {
              type: 'md-close-circle'
            }
          }),
          h('span', `响应${index}:` + reqName)
        ])
      }
    },
    getSelectedData () {
      // 只取当前的请求结果
      let treeEle = this.$refs.tree[0]
      let checkedNodes = treeEle.getCheckedNodes()
      // 只取末节点
      checkedNodes = checkedNodes.filter(item => {
        return String(item.children) === 'undefined'
      })
      if (checkedNodes.length === 0) {
        this.$Message.warning('请先勾选需要提取的数据')
        return
      }
      for (let i = 0; i < checkedNodes.length; i++) {
        let name = checkedNodes[i].name.replace(/[-_]/g, '') // 把减号和下划线去掉  节点名
        // 添加extract
        this.extract.push({
          id: Math.random().toString(),
          extract_name: name,
          extract_value: checkedNodes[i].path.trim(),
          editable: false
        })
        // 数据类型判断
        console.log('提取的节点：')
        console.log(checkedNodes[i])
        let validateType = null
        let expected = checkedNodes[i].expect
        if (typeof expected === 'number') {
          validateType = expected.toString().indexOf('.') > -1 ? 'float' : 'int'
        } else if (typeof expected === 'object') {
          // 平台未支持对象类型数据的校验，所以此处转成字串类型，但是对象类型的比较会失败
          validateType = 'string'
          expected = JSON.stringify(expected)
        } else {
          validateType = typeof expected
        }
        // 添加validate
        this.validate.push({
          id: Math.random().toString(),
          check: '$' + name,
          comparator: 'equals',
          validate_type: validateType,
          expected: expected,
          editable: false
        })
      }
    }
  },
  created () {
    EnvList({page: 'None'}).then(data => {
      this.evnList = data
    })
  },
  computed: {
    extract: {
      get () {
        return this.$store.state.extract
      },
      set (value) {
        this.$store.commit('setExtract', value)
      }
    },
    validate: {
      get () {
        return this.$store.state.validate
      },
      set (value) {
        this.$store.commit('setValidate', value)
      }
    }
  }
}

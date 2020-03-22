<template>
  <div id="sceneMockList">
    <!-- 接口详情 -->
    <Card dis-hover style="margin-bottom: 10px;">
      <p slot="title">接口详情</p>
      <Row :gutter="8">
        <Col :span="7">
          <CellGroup>
            <Cell :title="'接口名： ' + interfaceInfo.name"></Cell>
          </CellGroup>
        </Col>
        <Col :span="7">
          <CellGroup>
            <Cell :title="'uri： ' + interfaceInfo.uri" />
          </CellGroup>
        </Col>
        <Col :span="7">
          <CellGroup>
            <Cell :title="'简要描述： ' + interfaceInfo.description" />
          </CellGroup>
        </Col>
        <Col :span="3">
          <CellGroup>
            <Cell :title="'状态： ' + (interfaceInfo.enabled ? '启用' : '禁用')" />
          </CellGroup>
        </Col>
      </Row>
    </Card>

    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>

    <!-- 场景列表 -->
    <Card dis-hover style="margin-bottom: 10px;">
      <p slot="title">场景列表</p>
      <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
      <br />
      <Row>
        <Col :span="12">
          <Button type="info" size="small" @click="goBack">
            <Icon type="md-arrow-back" />返回
          </Button>
          <Button type="primary" size="small" @click="shwoAdd">
            <Icon type="md-add" />新增
          </Button>
        </Col>
        <Col :span="12" :style="{textAlign: 'right'}">
          <Page :total="count" show-total show-elevator @on-change="changePage" />
        </Col>
      </Row>
    </Card>

    <!-- 新增场景 -->
    <Card dis-hover v-if="addSceneMockModel">
      <p slot="title">新增场景</p>
      <div slot="extra">
        <Button type="info" size="small" @click="addSceneMock">
          保存
        </Button>
        <Button type="error" size="small" @click="addSceneMockModel = false">
          取消
        </Button>
      </div>
      <Row>
        <Col>
          <Form :model="sceneMockInfo" ref="sceneMockInfo" :rules="rules" inline>
            <FormItem prop="name">
              <Input v-model="sceneMockInfo.name" style="width: 35vw;" :maxlength="100"><span slot="prepend">场景名称：</span></Input>
            </FormItem>
            <FormItem>
              <Input v-model="sceneMockInfo.description" style="width: 35vw;"><span slot="prepend">简要描述: </span></Input>
            </FormItem>
          </Form>
        </Col>
      </Row>
      <Row>
        <Col>
          请求数据:
          <SceneJson :json="JSON.stringify(JSON.parse(sceneMockInfo.request), null, 4)" @sendJson="handleRequestJson"></SceneJson>
        </Col>
      </Row>
      <Row style="margin-top: 10px;">
        <Col>
          响应数据:
          <SceneJson :json="JSON.stringify(JSON.parse(sceneMockInfo.response), null, 4)" @sendJson="handleResponseJson"></SceneJson>
        </Col>
      </Row>
    </Card>

    <!-- 修改场景 -->
    <Card dis-hover v-if="editSceneMockModel">
      <p slot="title">修改场景</p>
      <div slot="extra">
        <Button type="info" size="small" @click="editSceneMock">
          修改
        </Button>
        <Button type="error" size="small" @click="editSceneMockModel = false">
          取消
        </Button>
      </div>
      <Row>
        <Col>
          <Form :model="currentSceneMockInfo" ref="currentSceneMockInfo" :rules="rules" inline>
            <FormItem prop="name">
              <Input v-model="currentSceneMockInfo.name" style="width: 35vw;" :maxlength="100"><span slot="prepend">场景名称：</span></Input>
            </FormItem>
            <FormItem>
              <Input v-model="currentSceneMockInfo.description" style="width: 35vw;"><span slot="prepend">简要描述: </span></Input>
            </FormItem>
          </Form>
        </Col>
      </Row>
      <Row>
        <Col>
          请求数据:
          <SceneJson :json="JSON.stringify(JSON.parse(currentSceneMockInfo.request), null, 4)" @sendJson="handleRequestJson"></SceneJson>
        </Col>
      </Row>
      <Row style="margin-top: 10px;">
        <Col>
          响应数据:
          <SceneJson :json="JSON.stringify(JSON.parse(currentSceneMockInfo.response), null, 4)" @sendJson="handleResponseJson"></SceneJson>
        </Col>
      </Row>
    </Card>
  </div>
</template>

<script>
import { SceneMockList, AddSceneMock, EditSceneMock, DeleteSceneMock, PatchSceneMock } from '@/api/index'
import { toLocalDateTime, validateJson } from '@/utils/Common'
import SceneJson from './SceneJson'
import SearchBar from '@/components/common/SearchBar'

export default {
  inject: ['reload'],
  components: {
    SceneJson, SearchBar
  },
  data () {
    return {
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
          title: '场景名称',
          key: 'name'
        },
        {
          title: '简要描述',
          key: 'description'
        },
        {
          title: '状态',
          key: 'enabled',
          render: (h, params) => {
            return h(
              // 标签名
              'i-switch',
              // 属性
              {
                props: {
                  value: params.row.enabled,
                  size: 'large'
                },
                on: {
                  'on-change': value => {
                    let sceneMock = this.data[params.index]
                    sceneMock.enabled = value
                    PatchSceneMock({enabled: sceneMock.enabled}, sceneMock.id)
                      .then(data => {
                        this.$Message.success(data.message)
                      })
                      .catch(error => {
                        console.log(error)
                        this.$nextTick(() => {
                          sceneMock.enabled = !value
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
          title: '创建时间',
          key: 'create_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.create_time))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 210,
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
                      this.shwoEdit()
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentSceneMockInfo = JSON.parse(
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
                  style: {
                    marginRight: '5px'
                  },
                  on: {
                    click: () => {
                      this.deleteSceneMock(params.index)
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
      interfaceInfo: {},
      addSceneMockModel: false,
      editSceneMockModel: false,
      sceneMockInfo: {
        name: '',
        description: '',
        enabled: false,
        request: '{}',
        response: '{}'
        // interface: this.interfaceInfo.id #发请求时再添加
      },
      rules: {
        name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ]
      },
      currentSceneMockInfo: {},
      newRequest: '',
      requestChangeStatus: false,
      newResponse: '',
      responseChangeStatus: false,
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'name',
          searchText: '场景名称'
        },
        {
          searchName: 'description',
          searchText: '简要描述'
        },
        {
          searchName: 'enabled',
          searchText: '启用状态',
          type: 'select',
          choices: [
            {name: '启用', id: '1'},
            {name: '禁用', id: '0'}
          ]
        },
        {
          searchName: 'create_time',
          searchText: '创建时间',
          type: 'date'
        }
      ]
    }
  },
  methods: {
    getData (page, interfaceId) {
      interfaceId = interfaceId || this.$route.params.interfaceInfo.id
      // 获取分页数据封装
      SceneMockList(Object.assign({ page: page, interface: interfaceId }, this.$refs.searchBar.searchConditions)).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    shwoAdd () {
      this.editSceneMockModel = false
      this.$nextTick(() => {
        this.addSceneMockModel = true
      })
    },
    addSceneMock () {
      this.$refs.sceneMockInfo.validate(valid => {
        if (valid) {
          if (!this.checkReqAndResp('request') || !this.checkReqAndResp('response')) {
            // 检查request和response是否为空,且格式是否正确
            return
          }
          this.sceneMockInfo.interface = this.interfaceInfo.id
          this.sceneMockInfo.request = this.newRequest || '{}'
          this.sceneMockInfo.response = this.newResponse || '{}'
          // 新增场景
          AddSceneMock(this.sceneMockInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addSceneMockModel = false
              this.reload()
              this.$Message.success('场景创建成功')
              this.resetData()
            })
        }
      })
    },
    shwoEdit () {
      this.addSceneMockModel = false // 由新增状态直接切换到修改状态
      this.editSceneMockModel = false // 由一个修改状态直接切换到另一个修改状态
      this.$nextTick(() => {
        this.editSceneMockModel = true
      })
    },
    editSceneMock () {
      this.$refs.currentSceneMockInfo.validate(valid => {
        if (valid) {
          if (!this.checkReqAndResp('request') || !this.checkReqAndResp('response')) {
            // 检查request和response是否为空,且格式是否正确
            return
          }
          this.currentSceneMockInfo.request = this.newRequest || this.currentSceneMockInfo.request
          this.currentSceneMockInfo.response = this.newResponse || this.currentSceneMockInfo.response
          // 修改场景信息
          EditSceneMock(this.currentSceneMockInfo, this.currentSceneMockInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editSceneMockModel = false
              this.reload()
              this.$Message.success('场景修改成功')
              this.resetData()
            })
        }
      })
    },
    deleteSceneMock (index) {
      // 删除场景信息
      this.$Modal.confirm({
        title: '确定要删除该场景吗？',
        content: `<span class='auto-break'>场景名：${this.data[index].name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteSceneMock(this.data[index].id).then(data => {
            this.$Message.success('场景删除成功')
            this.reload()
          })
        }
      })
    },
    goBack () {
      this.$router.replace({ name: 'Mock' })
    },
    handleRequestJson (data) {
      this.requestChangeStatus = true
      this.newRequest = data
    },
    handleResponseJson (data) {
      this.responseChangeStatus = true
      this.newResponse = data
    },
    resetData () {
      this.requestChangeStatus = false
      this.responseChangeStatus = false
      this.newRequest = ''
      this.newResponse = ''
    },
    checkReqAndResp (dataFlag) {
      if (this[dataFlag + 'ChangeStatus']) {
        // 数据被修改
        let dataNotEmpty = '数据不能为空'
        let dataError = '数据格式非正确json格式'
        let word = dataFlag === 'request' ? '请求' : '响应'
        let newData = dataFlag === 'request' ? 'newRequest' : 'newResponse'
        let data = this[newData].trim()
        if (data === '') {
          this.$Message.error(word + dataNotEmpty)
          return false
        }
        if (!validateJson(data)) {
          this.$Message.error(word + dataError)
          return false
        }
      }
      return true
    }
  },
  watch: {
    addSceneMockModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addSceneMockModel) {
        this.sceneMockInfo.name = ''
        this.sceneMockInfo.description = ''
        this.resetData()
      }
    },
    editSceneMockModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editSceneMockModel) {
        this.$refs.currentSceneMockInfo.resetFields()
        this.resetData()
      }
    }
  },
  mounted () {
    if (!this.$route.params.interfaceInfo) { this.$router.replace({ name: 'Mock' }) } // 按刷新按钮会返回上一页
    this.interfaceInfo = this.$route.params.interfaceInfo
    // 页面初始化请求分页数据
    this.getData(1, this.interfaceInfo.id)
  }
}
</script>

<style lang="less" scoped>
</style>

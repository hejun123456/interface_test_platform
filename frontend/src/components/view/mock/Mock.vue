<template>
  <div id="interfaceMockList">
    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addInterfaceMockModel = true">
          <Icon type="md-add" />新增
        </Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <!-- 新增弹窗 -->
    <Modal v-model="addInterfaceMockModel" title="新增接口" :loading="loading" ok-text="提交" @on-ok="addInterfaceMock">
      <Form :model="interfaceMockInfo" label-position="top" ref="interfaceMockInfo" :rules="rules">
        <FormItem label="接口名称" prop="name">
          <Input v-model="interfaceMockInfo.name" :maxlength="100"></Input>
        </FormItem>
        <FormItem label="uri" prop="uri">
          <Input v-model="interfaceMockInfo.uri" placeholder="uri不带参数，如：/xxxx/" :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="interfaceMockInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal v-model="editInterfaceMockModel" title="修改接口" :loading="loading" ok-text="修改" @on-ok="editInterfaceMock">
      <Form :model="currentInterfaceMockInfo" label-position="top" ref="currentInterfaceMockInfo" :rules="rules">
        <FormItem label="接口名称" prop="name">
          <Input v-model="currentInterfaceMockInfo.name" :maxlength="100"></Input>
        </FormItem>
        <FormItem label="uri" prop="uri">
          <Input v-model="currentInterfaceMockInfo.uri" placeholder="uri不带参数，如：/xxxx/" :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentInterfaceMockInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import { InterfaceMockList, AddInterfaceMock, EditInterfaceMock, DeleteInterfaceMock, PatchInterfaceMock } from '@/api/index'
import { toLocalDateTime, changeLoadingState } from '@/utils/Common'
import SearchBar from '@/components/common/SearchBar'

export default {
  inject: ['reload'],
  components: {
    SearchBar
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
          title: '接口名称',
          key: 'name'
        },
        {
          title: 'uri',
          key: 'uri'
        },
        {
          title: '简要描述',
          key: 'description'
        },
        {
          title: '场景数',
          key: 'scene_count'
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
                  // loading: false,
                  value: params.row.enabled,
                  size: 'large'
                },
                on: {
                  'on-change': value => {
                    let interfaceMock = this.data[params.index]
                    interfaceMock.enabled = value
                    PatchInterfaceMock({enabled: interfaceMock.enabled}, interfaceMock.id)
                      .then(data => {
                        this.$Message.success(data.message)
                      })
                      .catch(error => {
                        console.log(error)
                        this.$nextTick(() => {
                          interfaceMock.enabled = !value
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
                      this.editInterfaceMockModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentInterfaceMockInfo = JSON.parse(
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
                      this.deleteInterfaceMock(params.index)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash' } }), '删除']
              ),
              h(
                'Button',
                {
                  props: {
                    type: 'info',
                    size: 'small',
                    style: {}
                  },
                  on: {
                    click: () => {
                      this.goToDetail(params.index)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-alert' } }), '详情']
              )
            ])
          }
        }
      ],
      data: [],
      count: 0,
      addInterfaceMockModel: false,
      editInterfaceMockModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      interfaceMockInfo: {
        name: '',
        uri: '',
        description: '',
        enabled: false
      },
      rules: {
        name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        uri: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ]
      },
      currentInterfaceMockInfo: {},
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'name',
          searchText: '接口名称'
        },
        {
          searchName: 'uri',
          searchText: '接口 uri'
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
            {name: '全部', id: ''},
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
    getData (page) {
      // 获取分页数据封装
      InterfaceMockList(Object.assign({ page: page }, this.$refs.searchBar.searchConditions)).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addInterfaceMock () {
      var _this = this
      this.$refs.interfaceMockInfo.validate(valid => {
        if (valid) {
          // 新增接口
          AddInterfaceMock(this.interfaceMockInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addInterfaceMockModel = false
              this.reload()
              this.$Message.success('接口创建成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editInterfaceMock () {
      var _this = this
      this.$refs.currentInterfaceMockInfo.validate(valid => {
        if (valid) {
          // 修改接口信息
          EditInterfaceMock(this.currentInterfaceMockInfo, this.currentInterfaceMockInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editInterfaceMockModel = false
              this.reload()
              this.$Message.success('接口修改成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteInterfaceMock (index) {
      // 删除接口信息
      this.$Modal.confirm({
        title: '确定要删除该接口吗？',
        content: `<span class='auto-break'>接口名：${this.data[index].name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteInterfaceMock(this.data[index].id).then(data => {
            this.$Message.success('接口删除成功')
            this.reload()
          })
        }
      })
    },
    goToDetail (index) {
      this.$router.push({
        name: 'MockDetail',
        params: {
          interfaceInfo: this.data[index]
        }
      })
    }
  },
  watch: {
    addInterfaceMockModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addInterfaceMockModel) {
        this.$refs.interfaceMockInfo.resetFields()
      }
    },
    editInterfaceMockModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editInterfaceMockModel) {
        this.$refs.currentInterfaceMockInfo.resetFields()
      }
    }
  },
  mounted () {
    // 页面初始化请求分页数据
    this.getData(1)
  }
}
</script>

<style lang="less" scoped>
</style>

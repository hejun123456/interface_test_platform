<template>
  <div id="envlist">
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addEnvModel = true">
          <Icon type="md-add" />新增
        </Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <!-- 新增弹窗 -->
    <Modal v-model="addEnvModel" title="新增环境" :loading="loading" ok-text="提交" @on-ok="addEnv">
      <Form :model="envInfo" label-position="top" ref="envInfo" :rules="rules">
        <FormItem label="环境名称" prop="env_name">
          <Input v-model="envInfo.env_name" :maxlength="50"></Input>
        </FormItem>
        <FormItem label="环境地址" prop="base_url">
          <Input v-model="envInfo.base_url" placeholder='http://127.0.0.1:8000/' :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="envInfo.description" :maxlength="100"></Input>
        </FormItem>
        <FormItem label="状态">
          <i-switch v-model="envInfo.is_valid">
            <span slot="open">开</span>
            <span slot="close">关</span>
          </i-switch>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal v-model="editEnvModel" title="修改环境" :loading="loading" ok-text="修改" @on-ok="editEnv">
      <Form :model="currentEnvInfo" label-position="top" ref="currentEnvInfo" :rules="rules">
        <FormItem label="环境名称" prop="env_name">
          <Input v-model="currentEnvInfo.env_name" :maxlength="50"></Input>
        </FormItem>
        <FormItem label="环境地址" prop="base_url">
          <Input v-model="currentEnvInfo.base_url" placeholder='http://127.0.0.1:8000/' :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentEnvInfo.description" :maxlength="100"></Input>
        </FormItem>
        <FormItem label="状态">
          <i-switch v-model="currentEnvInfo.is_valid">
            <span slot="open">开</span>
            <span slot="close">关</span>
          </i-switch>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import { EnvList, AddEnv, EditEnv, DeleteEnv } from '@/api/index'
import { toLocalDateTime, changeLoadingState } from '@/utils/Common'

export default {
  inject: ['reload'],
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
          title: '环境名称',
          key: 'env_name'
        },
        {
          title: '环境地址',
          key: 'base_url'
        },
        {
          title: '简要描述',
          key: 'description'
        },
        {
          title: '状态',
          key: 'is_valid',
          render: (h, params) => {
            return h(
              // 标签名
              'i-switch',
              // 属性
              {
                props: {
                  // loading: false,
                  value: params.row.is_valid,
                  size: 'large'
                },
                on: {
                  'on-change': value => {
                    let env = this.data[params.index]
                    env.is_valid = value
                    let msg = value ? '启用' : '禁用'
                    EditEnv(env, env.id)
                      .then(() => {
                        this.$Message.success(`${msg}成功`)
                      })
                      .catch(error => {
                        console.log(error)
                        this.$Message.error(`${msg}失败,稍后再试`)
                        this.$nextTick(() => {
                          env.is_valid = !value
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
          width: 250,
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
                      // 回填代码到编辑器窗口 跳转editer
                      this.$router.push({
                        name: 'Editor',
                        params: {
                          editInfo: JSON.parse(
                            JSON.stringify(this.data[params.index])
                          ),
                          valueField: 'env_vars',
                          routerName: 'Env',
                          editMethod: 'EditEnv'
                        }
                      })
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-document' } }), '环境信息']
              ),
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
                      this.editEnvModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentEnvInfo = JSON.parse(
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
                      this.deleteEnv(params.index)
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
      addEnvModel: false,
      editEnvModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      envInfo: {
        env_name: '',
        base_url: '',
        description: '',
        is_valid: true
      },
      rules: {
        env_name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        base_url: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ]
      },
      currentEnvInfo: {}
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      EnvList({ page: page }).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addEnv () {
      var _this = this
      this.$refs.envInfo.validate(valid => {
        if (valid) {
          // 新增环境
          AddEnv(this.envInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addEnvModel = false
              this.reload()
              this.$Message.success('环境创建成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editEnv () {
      var _this = this
      this.$refs.currentEnvInfo.validate(valid => {
        if (valid) {
          // 修改环境信息
          EditEnv(this.currentEnvInfo, this.currentEnvInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editEnvModel = false
              this.reload()
              this.$Message.success('环境修改成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteEnv (index) {
      // 删除环境信息
      this.$Modal.confirm({
        title: '确定要删除该环境吗？',
        content: `<span class='auto-break'>环境名：${this.data[index].env_name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteEnv(this.data[index].id).then(data => {
            this.$Message.success('环境删除成功')
            this.reload()
          })
        }
      })
    }
  },
  watch: {
    addEnvModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addEnvModel) {
        this.$refs.envInfo.resetFields()
      }
    },
    editEnvModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editEnvModel) {
        this.$refs.currentEnvInfo.resetFields()
      }
    }
  },
  created () {
    // 页面初始化请求分页数据
    this.getData(1)
  }
}
</script>

<style lang="less" scoped>
</style>

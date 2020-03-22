<template>
  <div id="globalvarlist">
    <!-- 搜索栏 -->
    <SearchBar ref="searchBar" :searchDict="searchDict"></SearchBar>
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addGlobalvarModel = true">
          <Icon type="md-add" />新增
        </Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <!-- 新增弹窗 -->
    <Modal
      v-model="addGlobalvarModel"
      title="新增参数"
      :loading="loading"
      ok-text="提交"
      @on-ok="addGlobalvar"
    >
      <Form :model="globalvarInfo" label-position="top" ref="globalvarInfo" :rules="rules">
        <FormItem label="参数名称" prop="var_name">
          <Input v-model="globalvarInfo.var_name" :maxlength="50"></Input>
        </FormItem>
        <FormItem label="参数值" prop="var_value">
          <Input v-model="globalvarInfo.var_value" :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="globalvarInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
    <!-- 修改弹窗 -->
    <Modal
      v-model="editGlobalvarModel"
      title="修改参数"
      :loading="loading"
      ok-text="修改"
      @on-ok="editGlobalvar"
    >
      <Form :model="currentGlobalvarInfo" label-position="top" ref="currentGlobalvarInfo" :rules="rules">
        <FormItem label="参数名称" prop="var_name">
          <Input v-model="currentGlobalvarInfo.var_name" :maxlength="50"></Input>
        </FormItem>
        <FormItem label="参数值" prop="var_value">
          <Input v-model="currentGlobalvarInfo.var_value" :maxlength="256"></Input>
        </FormItem>
        <FormItem label="简要描述">
          <Input v-model="currentGlobalvarInfo.description"></Input>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  GlobalvarList,
  AddGlobalvar,
  EditGlobalvar,
  DeleteGlobalvar
} from '@/api/index'
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
          title: '参数名称',
          key: 'var_name'
        },
        {
          title: '参数值',
          key: 'var_value'
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
                      this.editGlobalvarModel = true
                      // 回填当前数据  需要复制对象，否则修改但未提交时，会影响本地对象，从而显示错误（修改后但未保存）数据
                      this.currentGlobalvarInfo = JSON.parse(
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
                      this.deleteGlobalvar(params.index)
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
      addGlobalvarModel: false,
      editGlobalvarModel: false,
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      globalvarInfo: {
        var_name: '',
        var_value: '',
        description: ''
      },
      rules: {
        var_name: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ],
        var_value: [
          {
            required: true,
            message: '必填',
            trigger: 'blur'
          }
        ]
      },
      currentGlobalvarInfo: {},
      // 定义搜索栏字段
      searchDict: [
        {
          searchName: 'var_name',
          searchText: '参数名称'
        },
        {
          searchName: 'var_value',
          searchText: '参数值'
        },
        {
          searchName: 'description',
          searchText: '简要描述'
        }
      ]
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      GlobalvarList(Object.assign({ page: page }, this.$refs.searchBar.searchConditions)).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    addGlobalvar () {
      var _this = this
      this.$refs.globalvarInfo.validate(valid => {
        if (valid) {
          // 新增参数
          AddGlobalvar(this.globalvarInfo)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.addGlobalvarModel = false
              this.reload()
              this.$Message.success('变量创建成功')
            })
            .catch(() => {
              // 同名变量处理
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    editGlobalvar () {
      var _this = this
      this.$refs.currentGlobalvarInfo.validate(valid => {
        if (valid) {
          // 修改参数信息
          EditGlobalvar(this.currentGlobalvarInfo, this.currentGlobalvarInfo.id)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.editGlobalvarModel = false
              this.reload()
              this.$Message.success('参数修改成功')
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteGlobalvar (index) {
      // 删除参数信息
      this.$Modal.confirm({
        title: '确定要删除该参数吗？',
        content: `<span class='auto-break'>参数名：${this.data[index].var_name}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteGlobalvar(this.data[index].id).then(data => {
            this.$Message.success('参数删除成功')
            this.reload()
          })
        }
      })
    }
  },
  watch: {
    addGlobalvarModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addGlobalvarModel) {
        this.$refs.globalvarInfo.resetFields()
      }
    },
    editGlobalvarModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.editGlobalvarModel) {
        this.$refs.currentGlobalvarInfo.resetFields()
      }
    }
  },
  mounted () {
    // ----页面初始化请求分页数据
    // created修改为mounted。因为此函数中调用了子组件的属性，如果是created，子组件未加载，则无法获取
    // 改为mounted后等子组件加载完成再执行此函数
    this.getData(1)
  }
}
</script>

<style lang="less" scoped>
</style>

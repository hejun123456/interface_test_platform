<template>
  <div id="debugtalk">
    <Table :columns="columns" :data="data" :border="true" :stripe="true"></Table>
    <br />
    <Row>
      <Col :span="12">
        <Button type="primary" size="small" @click="addParamsFileModel = true">
          <Icon type="md-add" />新增
        </Button>
      </Col>
      <Col :span="12" :style="{textAlign: 'right'}">
        <Page :total="count" show-total show-elevator @on-change="changePage" />
      </Col>
    </Row>
    <!-- 新增弹窗 -->
    <Modal
      v-model="addParamsFileModel"
      title="新增项目"
      :loading="loading"
      ok-text="上传"
      @on-ok="addParamsFile"
    >
      <Form :model="paramsFileInfo" label-position="top" ref="paramsFileInfo" :rules="rules">
        <FormItem label="项目名称" prop="project">
          <Select v-model="paramsFileInfo.project" style="width:100%">
            <Option v-for="project in projectList" :value="project.id" :key="project.id">{{ project.project_name }}</Option>
          </Select>
        </FormItem>
        <FormItem label="上传文件" prop="file">
          <Upload :before-upload="handleUpload" ref="file" action name="file">
            <Button icon="ios-cloud-upload-outline">选择文件</Button>
            <span
              v-if="paramsFileInfo.file !== null"
              :style="{marginLeft: '10px'}"
            >Upload file: {{ paramsFileInfo.file.name }}</span>
          </Upload>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  ParamsFileList,
  AddParamsFile,
  DeleteParamsFile,
  GetParamsFile,
  ProjectList
} from '@/api/index'
import { toLocalDateTime, fileName, changeLoadingState } from '@/utils/Common'

export default {
  inject: ['reload'],
  data () {
    // 自定义验证 判断file对象不为空
    const validateUpload = (rule, value, callback) => {
      if (this.paramsFileInfo.file === null) {
        callback(new Error('请选择文件'))
      } else {
        callback()
      }
    }
    return {
      columns: [
        {
          type: 'index',
          width: 60,
          align: 'center'
        },
        {
          title: '项目名称',
          key: 'project_name'
        },
        {
          title: '文件名称',
          key: 'file',
          render: (h, params) => {
            return h('div', fileName(params.row.file))
          }
        },
        {
          title: '上传人员',
          key: 'author'
        },
        {
          title: '创建时间',
          key: 'create_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.create_time))
          }
        },
        {
          title: '更新时间',
          key: 'update_time',
          render: (h, params) => {
            return h('div', toLocalDateTime(params.row.update_time))
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
                      // 获取文件内容
                      let id = this.data[params.index].id
                      GetParamsFile(id)
                        .then(data => {
                          // 把id加到data中
                          data.id = id
                          this.$router.push({
                            name: 'Editor',
                            params: {
                              editInfo: JSON.parse(JSON.stringify(data)),
                              valueField: 'content',
                              routerName: 'ParamsFile',
                              editMethod: 'EditParamsFile'
                            }
                          })
                        })
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
                      this.deleteParamsFile(params.index)
                    }
                  }
                },
                [h('Icon', { props: { type: 'md-trash' } }), '删除']
              )
            ])
          }
        }
      ],
      data: [], // 保存数据
      count: 0, // 总页数
      addParamsFileModel: false, // 弹窗显示控制
      // 点击提交，在数据校验失败后，对提交按钮的加载状态进行切换
      loading: true,
      // 临时保存用户输入数据
      paramsFileInfo: {
        project: '',
        file: null,
        author: ''
      },
      // 设置验证规则
      rules: {
        project: [{ required: true, message: '请选择', trigger: 'change', type: 'number' }],
        // 上传的规则就是 自定义验证的规则
        file: [{ required: true, validator: validateUpload, trigger: 'change' }]
      },
      projectList: []
    }
  },
  methods: {
    getData (page) {
      // 获取分页数据封装
      ParamsFileList({ page: page }).then(data => {
        this.data = data.results
        this.count = parseInt(data.count)
      })
    },
    changePage (page) {
      // 请求分页数据
      this.getData(page)
    },
    handleUpload (file) {
      // 阻止默认的上传流程 并获取文件对象
      this.paramsFileInfo.file = file
      return false
    },
    addParamsFile () {
      var _this = this
      // 上传提交
      this.$refs.paramsFileInfo.validate(valid => {
        if (valid) {
          // 上传文件，需要使用formData
          let formData = new FormData()
          formData.append('file', this.paramsFileInfo.file)
          formData.append('project', this.paramsFileInfo.project)
          formData.append(
            'author',
            JSON.parse(localStorage.getItem('user')).username
          )
          AddParamsFile(formData)
            .then(data => {
              // 关闭弹窗 并刷新页面
              this.$Message.success('文件上传成功')
              this.addParamsFileModel = false
              this.reload()
            })
            .catch(() => {
              changeLoadingState(_this)
            })
        } else {
          changeLoadingState(_this)
        }
      })
    },
    deleteParamsFile (index) {
      // 删除项目信息
      this.$Modal.confirm({
        title: '确定要删除吗',
        content: `<span class='auto-break'>所属项目：${this.data[index].project_name}</span>
<span class='auto-break'>文件名：${fileName(this.data[index].file)}</span>`,
        onOk: () => {
          // 删除数据 并刷新页面
          DeleteParamsFile(this.data[index].id).then(data => {
            this.$Message.success('文件删除成功')
            this.reload()
          })
        }
      })
    }
  },
  watch: {
    addParamsFileModel: function () {
      // 关闭弹窗后会重置数据
      if (!this.addParamsFileModel) {
        this.$refs.paramsFileInfo.resetFields()
      }
    },
    'paramsFileInfo.file': function (value) {
      if (value !== null) {
        // 只有在非null时才验证，否则验证必然失败，没意义
        // 监听file属性来验证是否已经选择文件，主要作用是解决：在弹提示再上传文件后，提示不消息的问题
        this.$refs.paramsFileInfo.validateField('file')
      }
    }
  },
  created () {
    // 页面初始化请求分页数据
    this.getData(1)
    // 请求项目信息(项目id和project_name)
    ProjectList({page: 'None'}).then(data => {
      this.projectList = data
    })
  }
}
</script>

<style lang="less" scoped>
</style>

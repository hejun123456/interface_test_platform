<template>
  <div id="tcrequest">
    <!-- 第一行 -->
    <Row class="datarow" :gutter="16">
      <Col span="14">
        <Input placeholder="请输入URL" v-model="url">
          <span slot="prepend">URL</span>
        </Input>
      </Col>
      <Col span="5">
        <div class="select-with-preffix ivu-input-wrapper ivu-input-wrapper-default ivu-input-type ivu-input-group ivu-input-group-default ivu-input-group-with-prepend">
          <div class="ivu-input-group-prepend" style="">
            <span>请求方法</span>
          </div>
          <i class="ivu-icon ivu-icon-ios-loading ivu-load-loop ivu-input-icon ivu-input-icon-validate"></i>
          <Select placeholder="请选择请求方法" v-model="method">
            <Option value="GET">GET</Option>
            <Option value="POST">POST</Option>
            <Option value="PUT">PUT</Option>
            <Option value="DELETE">DELETE</Option>
          </Select>
        </div>
      </Col>
      <Col span="5">
        <div class="select-with-preffix ivu-input-wrapper ivu-input-wrapper-default ivu-input-type ivu-input-group ivu-input-group-default ivu-input-group-with-prepend">
          <div class="ivu-input-group-prepend" style="">
            <span>数据格式</span>
          </div>
          <i class="ivu-icon ivu-icon-ios-loading ivu-load-loop ivu-input-icon ivu-input-icon-validate"></i>
          <!-- 默认为data -->
          <Select placeholder="请选择数据类型" v-model="dataType">
            <Option value="data">data</Option>
            <Option value="json">json</Option>
          </Select>
        </div>
      </Col>
    </Row>
    <!-- 第二行：headers表格 -->
    <div class="datarow">
      <RequestHeaders></RequestHeaders>
    </div>
    <!-- 第三行：params表格 -->
    <div class="datarow">
      <RequestParams></RequestParams>
    </div>
    <!-- 第四行：data表格或json -->
    <div class="datarow" v-if="dataType === 'data'">
      <RequestData></RequestData>
    </div>
    <div class="datarow" v-if="dataType === 'json'">
      <!-- json编辑器 -->
      <div>json编辑器</div>
      <RequestJsonEditor></RequestJsonEditor>
    </div>
  </div>
</template>

<script>
import RequestHeaders from './tcRequestComponents/RequestHeaders'
import RequestParams from './tcRequestComponents/RequestParams'
import RequestData from './tcRequestComponents/RequestData'
import RequestJsonEditor from './tcRequestComponents/RequestJsonEditor'

export default {
  name: 'tcrequest',
  components: {
    RequestHeaders,
    RequestParams,
    RequestData,
    RequestJsonEditor
  },
  data () {
    return {
    }
  },
  computed: {
    url: {
      get () {
        return this.$store.state.url
      },
      set (value) {
        this.$store.commit('setUrl', value)
      }
    },
    method: {
      get () {
        return this.$store.state.method
      },
      set (value) {
        this.$store.commit('setMethod', value)
      }
    },
    dataType: {
      get () {
        return this.$store.state.dataType
      },
      set (value) {
        this.$store.commit('setDataType', value)
      }
    }
  }
}
</script>

<style lang="less" scoped>
.datarow {
  margin-bottom: 15px;
}
</style>

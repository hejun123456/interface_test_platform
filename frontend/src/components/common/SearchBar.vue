<template>
  <div class="SearchBar">
    <!-- 搜索栏 -->
    <Row style="margin-bottom: 10px;">
      <Col>
        <Collapse>
          <Panel>
            搜索
            <div slot="content">
              <Row :gutter="16">
                <template v-for="(item, index) in searchDict">
                  <template v-if="item.type === 'input' || item.type === undefined">
                    <!-- 输入框 -->
                    <Col :span="8" style="margin-bottom: 10px;" :key="index">
                      <Input v-model="searchConditions[item.searchName]" :key="index">
                        <span slot="prepend" :key="index">{{item.searchText}}</span>
                      </Input>
                    </Col>
                  </template>
                  <template v-else-if="item.type === 'select'">
                    <!-- 下拉框 -->
                    <Col :span="8" style="margin-bottom: 10px;" :key="index">
                      <div class="select-with-preffix ivu-input-wrapper ivu-input-wrapper-default ivu-input-type ivu-input-group ivu-input-group-default ivu-input-group-with-prepend" :key="index">
                        <div class="ivu-input-group-prepend" style="">
                          <span>{{item.searchText}}</span>
                        </div>
                        <i class="ivu-icon ivu-icon-ios-loading ivu-load-loop ivu-input-icon ivu-input-icon-validate"></i>
                        <Select v-model="searchConditions[item.searchName]" style="" :key="index">
                          <Option v-for="choice in item.choices" :value="choice.id" :key="choice.id">{{choice.name}}</Option>
                        </Select>
                      </div>
                    </Col>
                  </template>
                  <template v-else-if="item.type === 'date'">
                    <!-- 时间框 -->
                    <Col :span="8" style="margin-bottom: 10px;" :key="index">
                      <div class="select-with-preffix ivu-input-wrapper ivu-input-wrapper-default ivu-input-type ivu-input-group ivu-input-group-default ivu-input-group-with-prepend" :key="index">
                        <div class="ivu-input-group-prepend" style="">
                          <span>{{item.searchText}}</span>
                        </div>
                        <i class="ivu-icon ivu-icon-ios-loading ivu-load-loop ivu-input-icon ivu-input-icon-validate"></i>
                        <DatePicker
                          v-model="searchConditions[item.searchName+'_after']"
                          @on-change="searchConditions[item.searchName+'_after']=$event"
                          confirm type="date" format="yyyy-MM-dd" class="search-date-picker"></DatePicker>
                        <span class="search-date-picker-split">-</span>
                        <DatePicker
                          v-model="searchConditions[item.searchName+'_before']"
                          @on-change="searchConditions[item.searchName+'_before']=$event"
                          confirm type="date" format="yyyy-MM-dd" class="search-date-picker"></DatePicker>
                      </div>
                    </Col>
                  </template>
                </template>
              </Row>
              <Row>
                <Col :span="12">
                  <Button type="primary" size="small" icon="ios-refresh" @click="reset">重置</Button>
                  <Button type="primary" size="small" icon="ios-search" @click="search">搜索</Button>
                </Col>
              </Row>
            </div>
          </Panel>
        </Collapse>
      </Col>
    </Row>
  </div>
</template>

<script>
/**
 * 组件说明
 * 1、父组件需要定义查询数据的方式，命名为getData
 * 2、通过this.$refs的方式获取本组件的searchConditions
 * 3、向本组件传入字段列表，格式看下面
 * 4、添加字段的下拉框，声明type类型为select，且添加choice选项对象列表
 */
export default {
  name: 'SearchBar',
  props: {
    /**
     * 搜索字段，如下格式
     * searchName与后台查询字段名一致，searchText自定义
     *searchDict: [
        {
          searchName: 'name',
          searchText: '用例名称'
        },
        {
          // 定义下拉框字段
          searchName: 'project',
          searchText: '项目名',
          type: 'select',
          choices: [{id:1, name:'选项1'}]
        }
      ]
     */
    searchDict: {
      required: true,
      type: Array
    }
  },
  data () {
    return {
      // 查询条件
      searchConditions: {}
    }
  },
  methods: {
    search () {
      console.log(this.searchConditions)
      this.$parent.getData(1)
    },
    reset () {
      // 重置查询条件
      this.searchConditions = {}
      this.$parent.getData(1)
    }
  }
}
</script>

<style lang="less" scoped>
.search-date-picker {
  width: calc(50% - 5px);
}
.search-date-picker-split {
  width: 10px;
  display: inline-block;
  text-align: center;
}
</style>

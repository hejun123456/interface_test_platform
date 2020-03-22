<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.fail-validator td {
  /* 测试报告中validator表格错误行的颜色渲染 */
  background-color: #ed4014;
  color: #000000;
}
.ivu-table-row-highlight > td {
  color:rgb(226, 147, 0) !important;
}
.select-with-preffix .ivu-select-selection {
  /*用于搜索栏中下拉框 */
  border-bottom-left-radius: 0px;
  border-top-left-radius: 0px;
}
html {
  /*背景自适应浏览器大小 */
  background: url(./assets/img/login.jpg) no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
}
body {
  /* 背景透明 */
  background-color: transparent;
}
.auto-break {
  /* 自动换行 */
  word-break:normal;
  width:auto;
  display:block;
  white-space:pre-wrap;
  word-wrap : break-word;
  overflow: hidden;
}
</style>

import { Message } from 'iview'
import store from '../vuex/store'
import { GetRefsCase } from '@/api/index'

export function toLocalDateTime (date) {
  // 时间格式化
  let d = new Date(date)
  return d.toLocaleString()
}

export function fileName (path) {
  // 获取路径中的文件名
  let list = path.split('/')
  return list[list.length - 1]
}

export function delRows (allRows, selectedRows) {
  console.log(allRows)
  console.log(selectedRows)
  // 批量删除表格行
  if (selectedRows.length > 0) {
    allRows = allRows.filter(
      item => selectedRows.indexOf(item.id) === -1
    )
    // 清空selectedrow
    selectedRows = []
  } else {
    Message.error('请选择要删除的行')
  }
  return {allRows, selectedRows}
}

export function getDataType (d) {
  let t = typeof d
  if (t === 'number') {
    return d.toString().indexOf('.') > -1 ? 'float' : 'int'
  }
  return t
}

export function validateJson (data) {
  // 判断是否为json格式的字串
  try {
    JSON.parse(data)
    return true
  } catch (e) {
    return false
  }
}

export function second2hms (value) {
  // 把秒转成时分秒格式
  let second = parseFloat(value)

  let h = parseInt(second / 3600)
  second = second % 3600

  let m = parseInt(second / 60)
  let s = (second % 60).toFixed(2)

  let t = s.toString() + 's'

  if (m !== 0) t = `${m}m ` + t
  if (h !== 0) t = `${h}h ` + t

  return t
}

export function singleMsg (msgType, msg) {
  // 回调函数，解除弹窗占用标记
  const cb = () => {
    store.commit('setHasMsg', false)
  }
  // 默认配置
  let config = {
    content: '',
    onClose: cb
  }
  // 追加用户配置
  if (typeof msg === 'string') {
    config.content = msg
  } else {
    Object.assign(config, msg)
  }

  if (!store.state.hasMsg) {
    // 锁定
    store.commit('setHasMsg', true)
    // 如果不存在已显示的弹窗，则显示当前弹窗
    Message[msgType](config)
  }
}

export function changeLoadingState (_this) {
  // 表单弹窗，提交失败时刷新提交按钮的加载状态
  _this.loading = false
  _this.$nextTick(() => {
    _this.loading = true
  })
}

export async function getTestcaseName (row) {
  // await把异步函数在async装饰的作用域内变成同步函数/操作
  // 被async装饰的函数在外部调用时是作用异步函数,所以如果需要再次封装成同步操作,同样使用async/await
  // 实时更新用例的引用用例名称
  let beforeList = JSON.parse(row.before)
  let afterList = JSON.parse(row.after)
  let refsList = beforeList.concat(afterList)
  if (!row.hadGetRefs && refsList.length > 0) {
    await GetRefsCase({id: row.id}).then(data => {
      row.before = data.before || '[]'
      row.after = data.after || '[]'
      row.hadGetRefs = true // 保证每个用例只请求一次
    })
  }
}

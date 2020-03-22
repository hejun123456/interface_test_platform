import axios from 'axios'
import qs from 'qs'
// import { Message } from 'iview'
import router from '@/router/index'
import {singleMsg} from '@/utils/Common.js'

const IP = '127.0.0.1'
const POST = '9999'
axios.defaults.baseURL = `http://${IP}:${POST}`

// // 路由请求拦截
// // http request 拦截器
axios.interceptors.request.use(
  config => {
    // 判断是否存在token，如果存在的话，则每个http header都加上authorization
    if (localStorage.getItem('authorization')) {
      // 用户每次操作，都将Token取出
      config.headers.common['authorization'] = JSON.parse(localStorage.getItem('authorization'))
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加一个响应拦截器
axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    switch (error.response.status) {
      case 400:
        // 如果后端不返回明确的错误信息，则显示统一提示
        if (error.response.data.message === '' || error.response.data.message === undefined) {
          singleMsg('error', '信息错误,请检查')
        } else {
          singleMsg('error', error.response.data.message)
        }
        break
      case 401:
        if (error.response.config.url.indexOf('login') > -1) {
          singleMsg('error', error.response.data.message)
        } else {
          singleMsg('error', '认证过期,重新登录')
        }
        router.push({name: 'Login'})
        break
      case 403:
        singleMsg('error', '无操作权限')
        break
      case 500:
        if (error.response.data.message === '' || error.response.data.message === undefined) {
          singleMsg('error', '服务错误,稍后重试')
        } else {
          singleMsg('error', error.response.data.message)
        }
        break
    }
    return Promise.reject(error) // 返回接口返回的错误信息
  }
)

// 登录
export const Login = (data) => { return axios.post(`/login/`, qs.stringify(data)).then(res => res.data) }

// 登出
export const Logout = (data) => { return axios.post(`/logout/`, qs.stringify(data)).then(res => res.data) }

// registe
export const Registe = (data) => { return axios.post(`/registe/`, qs.stringify(data)).then(res => res.data) }

// -----------------------------用户------------------------------ //
// 项目列表
export const UserList = () => { return axios.get(`/user/`).then(res => res.data) }

// -----------------------------项目------------------------------ //
// 项目列表
export const ProjectList = (params) => { return axios.get(`/project/`, {params: params}).then(res => res.data) }

// 新增项目
export const AddProject = (data) => { return axios.post(`/project/`, qs.stringify(data)).then(res => res.data) }

// 修改项目
export const EditProject = (data, id) => { return axios.put(`/project/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除项目
export const DeleteProject = (id) => { return axios.delete(`/project/${id}/`).then(res => res.data) }

// -----------------------------debugtalk------------------------------ //
// debugtalk列表
export const DebugtalkList = (params) => { return axios.get(`/debugtalk/`, {params: params}).then(res => res.data) }

// 修改debugtalk
export const EditDebugtalk = (data, id) => { return axios.put(`/debugtalk/${id}/`, qs.stringify(data)).then(res => res.data) }

// -----------------------------参数文件------------------------------ //
// 参数文件列表
export const ParamsFileList = (params) => { return axios.get(`/paramsfile/`, {params: params}).then(res => res.data) }

// 获取参数文件
export const GetParamsFile = (id) => { return axios.get(`/paramsfile/${id}`).then(res => res.data) }

// 新增参数文件
export const AddParamsFile = (data) => { return axios.post(`/paramsfile/`, data, {headers: {'Content-Type': 'multipart/form-data'}}).then(res => res.data) }

// 修改参数文件
export const EditParamsFile = (data, id) => { return axios.put(`/paramsfile/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除参数文件
export const DeleteParamsFile = (id) => { return axios.delete(`/paramsfile/${id}/`).then(res => res.data) }

// -----------------------------模块------------------------------ //
// 模块列表
export const ModuleList = (params) => { return axios.get(`/module/`, {params: params}).then(res => res.data) }

// 新增模块
export const AddModule = (data) => { return axios.post(`/module/`, qs.stringify(data)).then(res => res.data) }

// 修改模块
export const EditModule = (data, id) => { return axios.put(`/module/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除模块
export const DeleteModule = (id) => { return axios.delete(`/module/${id}/`).then(res => res.data) }

// -----------------------------全局变量------------------------------ //
// 全局变量列表
export const GlobalvarList = (params) => { return axios.get(`/globalvar/`, {params: params}).then(res => res.data) }

// 新增全局变量
export const AddGlobalvar = (data) => { return axios.post(`/globalvar/`, qs.stringify(data)).then(res => res.data) }

// 修改全局变量
export const EditGlobalvar = (data, id) => { return axios.put(`/globalvar/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除全局变量
export const DeleteGlobalvar = (id) => { return axios.delete(`/globalvar/${id}/`).then(res => res.data) }

// -----------------------------环境------------------------------ //
// 环境列表
export const EnvList = (params) => { return axios.get(`/env/`, {params: params}).then(res => res.data) }

// 新增环境
export const AddEnv = (data) => { return axios.post(`/env/`, qs.stringify(data)).then(res => res.data) }

// 修改环境
export const EditEnv = (data, id) => { return axios.put(`/env/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除环境
export const DeleteEnv = (id) => { return axios.delete(`/env/${id}/`).then(res => res.data) }

// -----------------------------报告管理------------------------------ //
// 报告列表
export const ReportList = (params) => { return axios.get(`/report/`, {params: params}).then(res => res.data) }

// 删除报告
export const DeleteReport = (id) => { return axios.delete(`/report/${id}/`).then(res => res.data) }

// -----------------------------用例------------------------------ //
// 用例列表
export const TestcaseList = (params) => { return axios.get(`/testcase/`, {params: params}).then(res => res.data) }
export const GetTestcase = (id) => { return axios.get(`/testcase/${id}/`).then(res => res.data) }

// 新增用例
export const AddTestcase = (data) => { return axios.post(`/testcase/`, qs.stringify(data)).then(res => res.data) }

// 修改用例
export const EditTestcase = (data, id) => { return axios.put(`/testcase/${id}/`, qs.stringify(data)).then(res => res.data) }

// 删除用例
export const DeleteTestcase = (id) => { return axios.delete(`/testcase/${id}/`).then(res => res.data) }

// -----------------------------定时任务------------------------------ //
// 任务列表
export const PeriodicTaskList = (params) => { return axios.get(`/task/`, {params: params}).then(res => res.data) }

// 新增任务
export const AddPeriodicTask = (data) => { return axios.post(`/task/`, data).then(res => res.data) }

// 修改任务
export const EditPeriodicTask = (data, id) => { return axios.put(`/task/${id}/`, data).then(res => res.data) }

// patch修改任务，用于在任务列表上直接启用/禁用的修改操作
export const PatchPeriodicTask = (data, id) => { return axios.patch(`/task/${id}/`, data).then(res => res.data) }

// 删除任务
export const DeletePeriodicTask = (id) => { return axios.delete(`/task/${id}/`).then(res => res.data) }

// 手动运行任务
export const RunPeriodicTask = (data) => { return axios.post(`/run-periodictask/`, data).then(res => res.data) }

// -----------------------------接口mock------------------------------ //
// 任务列表
export const InterfaceMockList = (params) => { return axios.get(`/interface/`, {params: params}).then(res => res.data) }

// 新增任务
export const AddInterfaceMock = (data) => { return axios.post(`/interface/`, data).then(res => res.data) }

// 修改任务
export const EditInterfaceMock = (data, id) => { return axios.put(`/interface/${id}/`, data).then(res => res.data) }

// patch修改任务，用于在InterfaceMock列表上直接启用/禁用的修改操作
export const PatchInterfaceMock = (data, id) => { return axios.patch(`/interface/${id}/`, data).then(res => res.data) }

// 删除任务
export const DeleteInterfaceMock = (id) => { return axios.delete(`/interface/${id}/`).then(res => res.data) }

// -----------------------------场景mock------------------------------ //
// 任务列表
export const SceneMockList = (params) => { return axios.get(`/scene/`, {params: params}).then(res => res.data) }

// 新增任务
export const AddSceneMock = (data) => { return axios.post(`/scene/`, data).then(res => res.data) }

// 修改任务
export const EditSceneMock = (data, id) => { return axios.put(`/scene/${id}/`, data).then(res => res.data) }

// patch修改任务，用于在SceneMock列表上直接启用/禁用的修改操作
export const PatchSceneMock = (data, id) => { return axios.patch(`/scene/${id}/`, data).then(res => res.data) }

// 删除任务
export const DeleteSceneMock = (id) => { return axios.delete(`/scene/${id}/`).then(res => res.data) }

// -----------------------------独立------------------------------ //
// 函数列表
export const GetFuncs = (params) => { return axios.get(`/getfuncs/`, {params: params}).then(res => res.data) }

// 调试
export const Debug = (data) => { return axios.post(`/debug/`, data).then(res => res.data) }

// 运行
export const Test = (data) => { return axios.post(`/test/`, data).then(res => res.data) }

// 查看异步运行报告
export const CheckReport = (data) => { return axios.post(`/check/`, qs.stringify(data)).then(res => res.data) }

// 面板数据查询
export const GetDashBoardInfo = () => { return axios.get(`/get_dashboard_info/`).then(res => res.data) }

// 引用用例查询
// export const GetRefsCase = (data) => {
//   return new Promise((resolve, reject) => {
//     axios.post(`/getrefscase/`, qs.stringify(data))
//       .then(res => {
//         resolve(res.data)
//       })
//       .catch(error => {
//         reject(error)
//       })
//   })
// }
export const GetRefsCase = (data) => { return axios.post(`/getrefscase/`, qs.stringify(data)).then(res => res.data) }

// 复制用例 copy-testcase
export const CopyTestcase = (data) => { return axios.post(`/copy-testcase/`, qs.stringify(data)).then(res => res.data) }

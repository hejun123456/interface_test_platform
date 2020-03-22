import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login'
import Index from '@/components/Index'
import ProjectList from '@/components/view/project/ProjectList'
import Debugtalk from '@/components/view/project/Debugtalk'
import ParamsFile from '@/components/view/project/ParamsFile'
import Dashboard from '@/components/view/Dashboard'
import Editor from '@/components/view/project/Editor'
import ModuleList from '@/components/view/module/ModuleList'
import Globalvar from '@/components/view/globalvar/Globalvar'
import Env from '@/components/view/env/Env'
import TestcaseList from '@/components/view/testcase/TestcaseList'
import AddTestcase from '@/components/view/testcase/AddTestcase'
import EditTestcase from '@/components/view/testcase/EditTestcase'
import TestReport from '@/components/view/testreport/TestReport'
import ReportManage from '@/components/view/reportManage/ReportManage'
import PeriodicTask from '@/components/view/periodicTask/PeriodicTask'
import Mock from '@/components/view/mock/Mock'
import MockDetail from '@/components/view/mock/MockDetail'

Vue.use(Router)

// 下面代码是保存使用push同一个路由时，不会报错
const originalPush = Router.prototype.push
Router.prototype.push = function push (location) {
  return originalPush.call(this, location).catch(err => err)
}

// router配置
const router = new Router({
  // mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/',
      name: 'Index',
      meta: {
        bread: '首页'
      },
      component: Index,
      redirect: {name: 'Dashboard'},
      // 页面权限控制
      // meta: {
      //   permissionLevel: 9
      // }
      children: [
        {
          path: '/project',
          name: 'ProjectList',
          meta: {
            bread: '项目管理-项目列表'
          },
          component: ProjectList
        },
        {
          path: '/module',
          name: 'ModuleList',
          meta: {
            bread: '模块管理-模块列表'
          },
          component: ModuleList
        },
        {
          path: '/debugtalk',
          name: 'Debugtalk',
          meta: {
            bread: '项目管理-debugtalk'
          },
          component: Debugtalk
        },
        {
          path: '/paramsfile',
          name: 'ParamsFile',
          meta: {
            bread: '项目管理-参数文件'
          },
          component: ParamsFile
        },
        {
          path: '/globalvar',
          name: 'Globalvar',
          meta: {
            bread: '项目管理-全局变量'
          },
          component: Globalvar
        },
        {
          path: '/env',
          name: 'Env',
          meta: {
            bread: '环境管理-环境列表'
          },
          component: Env
        },
        {
          path: '/testcaselist',
          name: 'TestcaseList',
          meta: {
            bread: '用例管理-用例列表'
          },
          component: TestcaseList
        },
        {
          path: '/addtestcase',
          name: 'AddTestcase',
          meta: {
            bread: '用例管理-新增用例'
          },
          component: AddTestcase
        },
        {
          path: '/edittestcase',
          name: 'EditTestcase',
          meta: {
            bread: '用例管理-编辑用例'
          },
          component: EditTestcase
        },
        {
          path: '/dashboard',
          name: 'Dashboard',
          meta: {
            bread: '首页'
          },
          component: Dashboard
        },
        {
          path: '/editor',
          name: 'Editor',
          meta: {
            bread: '编辑器'
          },
          component: Editor
        },
        {
          path: '/report',
          name: 'TestReport',
          meta: {
            bread: '测试报告'
          },
          component: TestReport
        },
        {
          path: '/reportmanage',
          name: 'ReportManage',
          meta: {
            bread: '报告管理-查看报告'
          },
          component: ReportManage
        },
        {
          path: '/periodictask',
          name: 'PeriodicTask',
          meta: {
            bread: '任务管理-任务列表'
          },
          component: PeriodicTask
        },
        {
          path: '/mock',
          name: 'Mock',
          meta: {
            bread: 'Mock管理-Mock列表'
          },
          component: Mock
        },
        {
          path: '/mockdetail',
          name: 'MockDetail',
          meta: {
            bread: 'Mock管理-Mock详情'
          },
          component: MockDetail
        }
      ]
    },
    {
      path: '*',
      redirect: {name: 'Index'}
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.path === '/login') {
    next()
  } else {
    // 判断是否已登陆
    let authorization = localStorage.getItem('authorization')
    if (authorization) {
      next()
    } else {
      router.push({name: 'Login'})
    }
  }
})

export default router

<template>
  <div class="layout">
    <Sider :style="{position: 'fixed', height: '100%', left: 0, overflow: 'auto'}">
      <div class="logo" >
        <router-link :to="{ name: 'Dashboard' }">
          <img src="../assets/btest-logo.png" width="65%"/>
        </router-link>
      </div>
      <Menu theme="dark" width="auto" @on-select="getPath" :active-name="$route.name">
        <!-- 菜单模板 -->
        <template v-for="(item, index) in menuData">
          <template v-if="item.child && item.child.length>0">
            <Submenu :name="item.name" :key="index">
              <template slot="title">
                <Icon :type="item.icon"></Icon>
                {{item.label}}
              </template>
              <MenuItem
                :name="child.name"
                v-for="(child, cindex) in item.child"
                :key="cindex"
                :to="child.to"
              >
                <Icon :type="child.icon" :key="cindex"></Icon>
                {{child.label}}
              </MenuItem>
            </Submenu>
          </template>
          <template v-else>
            <MenuItem :name="item.name" :key="index" :to="item.to">
              <Icon :type="item.icon" :key="index"></Icon>
              {{item.label}}
            </MenuItem>
          </template>
        </template>
      </Menu>
    </Sider>
    <Layout :style="{height: '100%', overflow: 'hidden', marginLeft: '200px'}">
      <!-- 页面头部 -->
      <div>
        <Row :style="{margin: '14px'}">
          <Col span="12">
            <Breadcrumb>
              <Icon type="md-home" />
              <span>当前位置：</span>
              <BreadcrumbItem v-for="site in currentSite" :key="site">{{site}}</BreadcrumbItem>
            </Breadcrumb>
          </Col>
          <Col span="12">
            <Dropdown
              placement="bottom-end"
              style="float: right;"
              trigger="click"
              :style="{fontSize: '1.2em'}"
            >
              <Icon type="md-contact" size="18"/>
              <a href="javascript:void(0)">
                {{username}}
                <Icon type="ios-arrow-down"></Icon>
              </a>
              <DropdownMenu slot="list">
                <DropdownItem @click.native="modifyPwd()">修改密码</DropdownItem>
                <DropdownItem @click.native="logout()">注销</DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </Col>
        </Row>
      </div>
      <!-- 主视图 -->
      <div class="main">
        <Card dis-hover>
          <router-view v-if="isRouterAlive"></router-view>
        </Card>
      </div>
    </Layout>
  </div>
</template>

<script>
import { Logout } from '@/api/index.js'

export default {
  provide () {
    return {
      reload: this.reload
    }
  },
  data () {
    return {
      isRouterAlive: true,
      username: JSON.parse(localStorage.getItem('user')).username,
      // 配合面包屑，保存当前路径的字串
      currentSiteValue: '',
      // 菜单原始数据
      menuData: [
        {
          name: '测试管理',
          icon: 'md-desktop',
          label: '测试管理',
          child: [
            {
              // name是当前菜单的唯一标识，与路由名一致。菜单根据当前路由来高亮选中的菜单
              name: 'ProjectList',
              icon: 'md-folder',
              // 实际路由,如果有to属性时，name要与路由一致
              to: { name: 'ProjectList' },
              // 显示在页面的菜单文字
              label: '项目列表'
            },
            {
              name: 'Debugtalk',
              icon: 'logo-codepen',
              to: { name: 'Debugtalk' },
              label: 'debugtalk'
            },
            {
              name: 'ModuleList',
              icon: 'md-apps',
              to: { name: 'ModuleList' },
              label: '模块列表'
            },
            {
              name: 'TestcaseList',
              icon: 'md-bug',
              to: { name: 'TestcaseList' },
              label: '用例列表'
            },
            {
              name: 'PeriodicTask',
              icon: 'md-calendar',
              to: { name: 'PeriodicTask' },
              label: '任务列表'
            }
          ]
        },
        {
          name: '数据管理',
          icon: 'logo-buffer',
          label: '数据管理',
          child: [
            {
              name: 'Env',
              icon: 'md-pin',
              to: { name: 'Env' },
              label: '环境列表'
            },
            {
              name: 'ParamsFile',
              icon: 'md-document',
              to: { name: 'ParamsFile' },
              label: '参数文件'
            },
            {
              name: 'Globalvar',
              icon: 'md-globe',
              to: { name: 'Globalvar' },
              label: '全局变量'
            },
            {
              name: 'Mock',
              icon: 'md-sync',
              to: { name: 'Mock' },
              label: 'Mock列表'
            }
          ]
        },
        {
          name: '报告管理',
          icon: 'md-analytics',
          label: '报告管理',
          child: [
            {
              name: 'ReportManage',
              icon: 'md-information-circle',
              to: { name: 'ReportManage' },
              label: '查看报告'
            }
          ]
        }
      ]
    }
  },
  methods: {
    logout () {
      const params = {
        username: JSON.parse(localStorage.getItem('user')).username
      }
      Logout(params).then(data => {
        this.$router.push({ name: 'Login' })
        localStorage.removeItem('user')
        localStorage.removeItem('authorization')
        this.$Message.success(data.message)
      })
    },
    modifyPwd () {
      console.log('修改密码')
    },
    getPath (name) {
      // 点击菜单，获取菜单路径用于面包屑切换
      this.currentSiteValue = this.$route.meta.bread
    },
    reload () {
      this.isRouterAlive = false
      this.$nextTick(() => {
        this.isRouterAlive = true
      })
    }
  },
  watch: {
    '$route' (to, from) {
      this.currentSiteValue = to.meta.bread
    }
  },
  computed: {
    currentSite () {
      return this.currentSiteValue.split('-')
    }
  },
  created () {
    // 页面初始化时获取菜单路径
    this.currentSiteValue = this.$route.meta.bread
  }
}
</script>

<style lang="less" scoped>
.layout {
  border: 1px solid #d7dde4;
  background: #f5f7f9;
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  height: 100vh;
}
.main {
  overflow: auto;
  height: calc(100% - 49px);
  padding: 0 14px 14px;
}
.logo {
  padding: 10px 0 0 24px;
}
</style>

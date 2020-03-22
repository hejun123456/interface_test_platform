<template>
  <div id="loginLayout">
    <h1 style="margin-bottom: 20px;">自动化测试平台</h1>
    <!-- 注册表单 -->
    <Form ref="regForm" :model="loginForm" :rules="regRules" v-show="isRegPage">
      <FormItem prop="username">
        <Input type="text" size="large" v-model="loginForm.username" placeholder="账号">
          <Icon type="md-person" slot="prepend" size="18"/>
        </Input>
      </FormItem>
      <FormItem prop="password">
        <Input type="password" size="large" v-model="loginForm.password" placeholder="密码">
          <Icon type="md-lock" slot="prepend" size="18"/>
        </Input>
      </FormItem>
      <FormItem prop="email">
        <Input size="large" v-model="loginForm.email" placeholder="邮箱">
          <Icon type="md-mail"  slot="prepend" size="18"/>
        </Input>
      </FormItem>
      <FormItem>
        <Checkbox v-model="isRemenber" size="large" class="isRemenber">记住我</Checkbox>
      </FormItem>
      <FormItem>
        <Button type="primary" size="large" @click="handleRegiste('loginForm')">注册</Button>
      </FormItem>
      <a href="javascript:void(0);" @click="changeForm('regForm')">立即去登录</a>
    </Form>
    <!-- 登录表单 -->
    <Form ref="loginForm" :model="loginForm" :rules="rules" v-show="!isRegPage">
      <FormItem prop="username">
        <Input type="text" size="large" v-model="loginForm.username" placeholder="账号">
          <Icon type="md-person" slot="prepend" size="18"/>
        </Input>
      </FormItem>
      <FormItem prop="password">
        <Input type="password" size="large" v-model="loginForm.password" placeholder="密码">
          <Icon type="md-lock" slot="prepend" size="18"/>
        </Input>
      </FormItem>
      <FormItem>
        <Checkbox v-model="isRemenber" size="large" class="isRemenber">记住我</Checkbox>
      </FormItem>
      <FormItem>
        <Button type="primary" size="large" @click="handleLogin('loginForm')">登录</Button>
      </FormItem>
      <a href="javascript:void(0);" @click="changeForm('loginForm')">注册新账号</a>
    </Form>
  </div>
</template>
<script>
import {Login, Registe} from '@/api/index.js'
import {singleMsg} from '@/utils/Common.js'

export default {
  data () {
    return {
      isRemenber: false,
      isRegPage: false,
      loginForm: {},
      rules: {
        username: [
          {
            required: true,
            message: '账号必填',
            trigger: 'blur'
          }
        ],
        password: [
          {
            required: true,
            message: '密码必填',
            trigger: 'blur'
          }
        ]
      },
      regRules: {
        username: [
          {
            required: true,
            message: '账号必填',
            trigger: 'blur'
          }
        ],
        password: [
          {
            required: true,
            message: '密码必填',
            trigger: 'blur'
          }
        ],
        email: [
          { required: true, message: '邮箱必填', trigger: 'blur' },
          { type: 'email', message: '邮箱格式错误', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    changeForm (name) {
      this.$refs[name].resetFields()
      this.loginForm = {}
      this.isRegPage = !this.isRegPage
    },
    handleLogin (name) {
      this.$refs[name].validate((valid) => {
        if (valid) {
          // 处理isRemenber
          if (this.isRemenber) {
            localStorage.setItem('username', JSON.stringify(this.loginForm.username))
            localStorage.setItem('isRemenber', JSON.stringify(this.isRemenber))
          } else {
            localStorage.removeItem('username')
            localStorage.removeItem('isRemenber')
          }
          // 检查表单数据是否有效
          Login(this.loginForm).then((data) => {
            let {authorization, user} = data
            localStorage.setItem('user', JSON.stringify(user))
            localStorage.setItem('authorization', JSON.stringify(authorization))
            // 跳转到主页
            this.$router.replace({name: 'Index'})
            // this.$Message.success(data.message)
            singleMsg('success', data.message)
          })
        }
      })
    },
    handleRegiste (name) {
      this.$refs[name].validate((valid) => {
        if (valid) {
          // 注册成功后登录
          Registe(this.loginForm).then((data) => {
            // this.$Message.success(data.message)
            singleMsg('success', data.message)
            this.handleLogin(name)
          })
        }
      })
    }
  },
  created () {
    // 进入登录页面时清空localStorage数据
    localStorage.removeItem('user')
    localStorage.removeItem('authorization')
    // 如果记住用户，进入页面时回填
    let isRemenber = JSON.parse(localStorage.getItem('isRemenber'))
    if (isRemenber) {
      this.isRemenber = isRemenber
      this.loginForm.username = JSON.parse(localStorage.getItem('username'))
    }
  }
}
</script>

<style scoped>
#loginLayout {
  height: auto;
  width: 370px;
  margin: 200px auto;
  text-align: center;
  border-radius: 8px;
  background: url(../assets/img/main_bg.png) repeat;
  padding: 50px 40px;
}
h1, a {
  color: #FFFFFF;
}
.isRemenber {
  color: #FFFFFF;
  float: left;
}
</style>

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import store from './store'
import 'vant/lib/index.css' // Import Vant styles globally
import lazyLoad from './directives/lazyLoad'

const app = createApp(App)

// 注册全局指令
app.directive('lazy', lazyLoad)

app.use(router)
app.use(store)
app.mount('#app')

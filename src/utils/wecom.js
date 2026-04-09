import wx from 'weixin-js-sdk'
import { getWeComJSConfig } from '@/api'

/**
 * 初始化企业微信 JS-SDK
 * @param {Array} jsApiList 需要使用的 JS 接口列表
 * @returns {Promise} 
 */
export const initWeComConfig = async (jsApiList = ['scanQRCode']) => {
  return new Promise(async (resolve, reject) => {
    try {
      // 当前页面 URL（不含 # 及其后面的部分）
      const url = window.location.href.split('#')[0]
      
      // 获取配置
      const res = await getWeComJSConfig(url)
      if (res?.ret !== true || !res?.config) {
        return reject(new Error('获取企业微信配置失败'))
      }

      const { appId, timestamp, nonceStr, signature } = res.config

      // 配置 wx.config
      wx.config({
        beta: true, // 必须这么写，否则在微信插件有些jsapi会有问题
        debug: false, // 开启调试模式
        appId: appId, // 必填，企业微信的corpID
        timestamp: timestamp, // 必填，生成签名的时间戳
        nonceStr: nonceStr, // 必填，生成签名的随机串
        signature: signature, // 必填，签名
        jsApiList: jsApiList // 必填，需要使用的JS接口列表
      })

      wx.ready(() => {
        resolve()
      })

      wx.error((res) => {
        reject(new Error(`微信 JS-SDK 初始化失败: ${JSON.stringify(res)}`))
      })
    } catch (error) {
      reject(error)
    }
  })
}

/**
 * 调用企业微信扫码
 * @returns {Promise<string>} 返回扫码结果
 */
export const scanQRCode = () => {
  return new Promise((resolve, reject) => {
    wx.scanQRCode({
      desc: 'scanQRCode desc',
      needResult: 1, // 默认为0，扫描结果由企业微信处理，1则直接返回扫描结果
      scanType: ["qrCode", "barCode"], // 可以指定扫二维码还是条形码（一维码），默认二者都有
      success: function (res) {
        // 回调
        const result = res.resultStr
        resolve(result)
      },
      error: function (res) {
        if (res.errMsg.indexOf('function_not_exist') > 0) {
          reject(new Error('版本过低请升级'))
        } else {
          reject(new Error(res.errMsg))
        }
      }
    })
  })
}

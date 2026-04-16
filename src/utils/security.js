// XSS 防护工具函数

// HTML 转义，防止 XSS 攻击
// text: 需要转义的文本
// 返回转义后的安全文本
export function escapeHtml(text) {
  if (!text || typeof text !== 'string') {
    return text;
  }
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// 过滤危险标签和属性
// html: 需要过滤的 HTML 字符串
// 返回过滤后的安全 HTML
export function sanitizeHtml(html) {
  if (!html || typeof html !== 'string') {
    return html;
  }
  
  // 创建临时 DOM 元素
  const temp = document.createElement('div');
  temp.innerHTML = html;
  
  // 危险标签列表
  const dangerousTags = ['script', 'iframe', 'object', 'embed', 'form', 'input'];
  // 危险属性列表
  const dangerousAttributes = ['onclick', 'onload', 'onerror', 'onmouseover', 'href'];
  
  // 移除危险标签
  dangerousTags.forEach(tag => {
    const elements = temp.getElementsByTagName(tag);
    while (elements.length > 0) {
      elements[0].parentNode.removeChild(elements[0]);
    }
  });
  
  // 移除危险属性
  const allElements = temp.getElementsByTagName('*');
  for (let i = 0; i < allElements.length; i++) {
    const element = allElements[i];
    dangerousAttributes.forEach(attr => {
      if (element.hasAttribute(attr)) {
        // 如果 href 属性包含 javascript: 协议，也移除
        if (attr === 'href') {
          const value = element.getAttribute(attr);
          if (value && value.toLowerCase().startsWith('javascript:')) {
            element.removeAttribute(attr);
          }
        } else {
          element.removeAttribute(attr);
        }
      }
    });
  }
  
  return temp.innerHTML;
}

// 过滤输入文本，移除特殊字符
// text: 需要过滤的文本
// 返回过滤后的文本
export function sanitizeInput(text) {
  if (!text || typeof text !== 'string') {
    return text;
  }
  // 移除潜在的 XSS 攻击向量
  return text
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '');
}

// 验证手机号格式
// phone: 手机号字符串
// 返回是否有效
export function isValidPhone(phone) {
  if (!phone) return false;
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

// 验证邮箱格式
// email: 邮箱字符串
// 返回是否有效
export function isValidEmail(email) {
  if (!email) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// 验证序列号格式（字母数字组合）
// serialNo: 序列号字符串
// 返回是否有效
export function isValidSerialNo(serialNo) {
  if (!serialNo) return false;
  const serialRegex = /^[a-zA-Z0-9-_]+$/;
  return serialRegex.test(serialNo);
}

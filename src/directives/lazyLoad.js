// 图片懒加载指令

// 存储观察器实例
const observerMap = new WeakMap();

// 创建 IntersectionObserver 实例
const createObserver = (el, binding) => {
  const options = {
    root: null,
    rootMargin: '0px 0px 50px 0px', // 提前 50px 开始加载
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = binding.value;
        
        if (src) {
          // 创建新图片对象预加载
          const image = new Image();
          image.onload = () => {
            img.src = src;
            img.classList.add('lazy-loaded');
          };
          image.onerror = () => {
            img.classList.add('lazy-error');
            // 可以设置默认错误图片
            // img.src = '/default-error.png';
          };
          image.src = src;
        }
        
        // 停止观察
        observer.unobserve(img);
        observerMap.delete(img);
      }
    });
  }, options);

  return observer;
};

// 懒加载指令
const lazyLoad = {
  mounted(el, binding) {
    // 设置占位样式
    el.classList.add('lazy-loading');
    
    // 创建观察器
    const observer = createObserver(el, binding);
    observer.observe(el);
    observerMap.set(el, observer);
  },
  
  updated(el, binding) {
    // 如果值变化，重新观察
    if (binding.oldValue !== binding.value) {
      // 清除旧的观察器
      const oldObserver = observerMap.get(el);
      if (oldObserver) {
        oldObserver.unobserve(el);
      }
      
      // 重置状态
      el.classList.remove('lazy-loaded', 'lazy-error');
      el.classList.add('lazy-loading');
      
      // 创建新的观察器
      const newObserver = createObserver(el, binding);
      newObserver.observe(el);
      observerMap.set(el, newObserver);
    }
  },
  
  unmounted(el) {
    // 清理观察器
    const observer = observerMap.get(el);
    if (observer) {
      observer.unobserve(el);
      observerMap.delete(el);
    }
  }
};

export default lazyLoad;

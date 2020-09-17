# js反混淆使用介绍

*目前已经实现的是变量名反混淆，十六进制数反混淆，while true循环结构反混淆，for结构反混淆*

### 环境需求

* 1、 需要安装nodejs
* 2、需要：
  * npm install @babel/traverse
  * npm install @babel/generator
  * npm install @babel/types
  * Nom install @babel/generator

### demo执行解释

* 1、demo文件在js/general_simple.js，对origin_js/中的1111.js进行反混淆

```javascript
var silple_js = require('./js/simple_js');  // 这里倒入反混淆接口
_x7933 = ["undefined", "hasInstance"]  // 需要用到的全局数组
silple_js.beautiful('./origin_js/1111.js', "./origin_js/1111_.js", "","_x7933");  // 第一个参数：需要反混淆文件路径；第二个参数：反混淆后的代码存放文件路径；第三个参数：变量名反混淆的函数名（用函数混淆的）；第四个参数：变量名反混淆的数组名（用数组混淆的）
```


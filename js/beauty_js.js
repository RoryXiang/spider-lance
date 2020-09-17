const fs = require('fs');
// 把js源码转成语法树
const parser = require("@babel/parser");
// 遍历语法树中的节点
const traverse = require("@babel/traverse").default;
// 提供对语法树中Node的一系列方法比如判断Node类型，辅助创建Node等
const t = require("@babel/types");
// 根据语法树生成js代码
const generator = require("@babel/generator").default;


exports.beautiful = function (old_file, new_file, callname, membername) {
    membernamestr = membername;
    callnamestr = callname
    fs.readFile(old_file, { "encoding": 'utf-8' }, function (err, data) {
        //  转换成语法树
        const ast = parser.parse(data);
        // 我们要转换的代码
        decrypt(ast);  // 普通变量替换
        decrypt2(ast);  // 结构转换
        // 转换完后放到generator生成新的js
        let { code } = generator(ast);
        // 针对代码中!![]/![] 直接进行通过字符串替换
        code = code.replace(/!!\[\]/g, 'true').replace(/!\[\]/g, 'false');
        // 写到新文件中
        fs.writeFile(new_file, code, function (err) {
            if (!err) {
                console.log('finished')
            } else {
                console.log(err)
            }
        })
    });
};

function decrypt(ast) {  // 普通变量反混淆

    traverse(ast,  {
        CallExpression: {  // 替换变量名混淆
            enter: [callToStr]
        },
        StringLiteral: {  // 数字16进制转换成10进制
            enter: [removeExtra]
        },
        MemberExpression: {  // 替换变量名混淆 b[3]这种
            enter: [memberToStr]
        },
        NumericLiteral: removeExtra,  // 数字16进制转换成10进制
        VariableDeclarator: {  // 移除未被修改的变量
            enter: [removeUselessVaria]
        }
    })
};

// 结构反混淆
function decrypt2(ast) {  // 结构反混淆
    traverse(ast, {
        WhileStatement: replaceWhile, // while 结构消除
        // ForStatement: generateTransferFile,   // for 结构消除
        // VariableDeclarator: replaceFns,  //
        // FunctionDeclaration: "",
    })
}

// 替换变量名混淆 函数类型混淆 b('0x88')
function callToStr(path) {  // 替换变量名混淆 函数类型混淆 b('0x88')
    const id = path.node;
    if (id.type === "CallExpression" && id.callee.name === callnamestr){  // 设置替换条件
        let data = eval(`${id.callee.name}('${id.arguments[0].value}')`);  // 获取替换值
        path.replaceWith(t.valueToNode(data))  // 替换操作。
    }
}

// 替换变量名混淆 数组类型混淆 _dfdw[0]
function memberToStr(path) {  // 替换变量名混淆 数组类型混淆 _dfdw[0]
    const id = path.node;
    if (id.type === "MemberExpression" && id.object.name === membernamestr){  // 设置替换条件
        let data = eval(`${id.object.name}['${id.property.value}']`);  // 获取替换值
        path.replaceWith(t.valueToNode(data))  // 替换操作。
    }
}

// 移除未被修改的变量
function removeUselessVaria(path) {  // 移除未被修改的变量
    const {id} = path.node;

    const binding = path.scope.getBinding(id.name);
    if (!binding || binding.constantViolations.length > 0)
    {//如果变量被修改过，则不能进行删除动作。
        return;
    }
    if (binding.referencePaths.length === 0)
    {//长度为0，说明变量没有被使用过。
        try {
            path.remove();
        }
        catch (error) {
        }
    }
}

// 数字16进制转换成10进制
function removeExtra(path) {  // 数字16进制转换成10进制
    delete path.node.extra
}

// 消除掉while 循环结构。
function replaceWhile(path) { // 消除掉while 循环结构。
    let node = path.node;

    // 判断基础的结构 while(true) {}
    // console.log("-------------");
    // if (!t.isBooleanLiteral(node.test) || node.test.value !== true) return;
    if (node.test.prefix !== true) return;
    // console.log(node);
    if (!t.isBlockStatement(node.body)) return;
    // console.log(node)
    const body = node.body.body;
    // console.log(body)
    // 判断包含一个switch和一个break
    if (!t.isSwitchStatement(body[0]) || !t.isMemberExpression(body[0].discriminant) || !t.isBreakStatement(body[1])) return;

    const switchStm = body[0];
    // switch (idxArr[idx++]) 找到idxArr变量的名称
    const arrName = switchStm['discriminant'].object.name;
    // console.log("---- "+arrName)
    // 找到sibling前一个Node
    let varKey = path.key - 2;
    let varPath = path.getSibling(varKey);
    // console.log("----varPath "+varPath)
    // 找到idxArr这个Node
    let varNode = varPath.node.declarations.filter(declarator => declarator.id.name === arrName)[0];
    // console.log(varNode.init.callee.object)
    if (!varNode.init.callee.object.value) return;  // 有的idxArr 是通过计算出来的，这里获取不到
    // 把值取出来分割成数组 ["0", "1", "3", "6", "2" ...]
    let idxArr = varNode.init.callee.object.value.split('|');
    // console.log("arr "+idxArr)
    // 所有的case
    const runBody = switchStm.cases
    let retBody = []
    idxArr.map(targetIdx => {
        // 根据顺序找到对应的语句
        let targetBody = runBody[targetIdx].consequent
        // 把continue删除
        if (t.isContinueStatement(targetBody[targetBody.length - 1])) {
            targetBody.pop()
        }
        retBody = retBody.concat(targetBody)
    })
    // 如果是一个Node替换为多个，要使用replaceWithMultiple
    path.replaceWithMultiple(retBody)
    // remove idxArr var/index
    varPath.remove()
}

function replaceFns(path) {
    // 遍历VariableDeclarator
    let node = path.node;
    // 变量右边是不是一个对象字面量
    if (!t.isObjectExpression(node.init)) return;
    let properties = node.init.properties;
    if (properties.length === 0) return;
    try {
        // 这里简单的判断了对象第一个属性值是不是个函数，并且函数只有一条return语句
        // 看起来有些不严谨，但是对于这份代码没有问题，没有出现和这个结构一样但后面的值不满足的情况。。
        if (!t.isFunctionExpression(properties[0].value)) return;
        if (properties[0].value.body.body.length !== 1) return;
        let retStmt = properties[0].value.body.body[0];
        if (!t.isReturnStatement(retStmt)) return

    } catch (error) {
        console.log(error)
        console.log('wrong fn arr', properties)
    }
    // 存储一下变量名，后面调用都是objName[key]，所以需要匹配它
    let objName = node.id.name;
    console.log(properties.length)
    if (properties.length > 100) return;
    // 一个一个函数进行查找
    properties.forEach(prop => {
        // console.log("/////")
        // console.log(prop)
        // key
        let key = prop.key.value;
        // 需要替换成的语句
        try {
            var retStmt = prop.value.body.body[0];
            // console.log(222222)
        }catch (error) {
            // console.log(333333)
            var retStmt = prop.value.value;
            // console.log(44444)
        }
        // console.log(retStmt)
        // path.getFunctionParent可以方便的帮我们找出最近的一个包含此path的父function, 这样我们就可以在此作用域遍历了
        const fnPath = path.getFunctionParent();
        fnPath.traverse({
            // 找所有函数调用 fn()
            CallExpression: function (_path) {
                // 确保是obj['key'] 或 obj.add等相似的调用
                if (!t.isMemberExpression(_path.node.callee)) return;
                let node = _path.node.callee;
                // 第一位是上面定义的objName
                if (!t.isIdentifier(node.object) || node.object.name !== objName) return;
                // key值是我们当前遍历到的
                if (!t.isStringLiteral(node.property) || node.property.value !== key) return;

                // 参数
                let args = _path.node.arguments;

                /* 其实定义的函数总共分三类
                 * 1. function _0x3eeee4(a, b) {
                 *        return a & b; // BinaryExpression
                 *    }
                 * 2. function _0x3eeee4(a, b) {
                 *        return a === b; // LogicalExpression
                 *    }
                 * 3. function _0x3eeee4(a, b, c) {
                 *        return a(b, c) // CallExpression
                 *    }
                 * * 3. function _0x3eeee4(a) {
                 *        return a() // CallExpression
                 *    }
                 * 4. 固定值 b('0x5ee') === /ggYHo{?EbHdKdo]{1]
                 * 下面的代码就是对调用的代码做一个转换。这里可以看到t.Node并传入对应的参数可以帮助我们生成相应的节点, t.isNode是判断是否*  为某个type的Node
                 */

                if (t.isStringLiteral(retStmt.argument)) {
                    _path.replaceWith(t.valueToNode(retStmt))
                } return;
                if (t.isBinaryExpression(retStmt.argument) && args.length === 2) {
                    _path.replaceWith(t.binaryExpression(retStmt.argument.operator, args[0], args[1]))
                }
                if (t.isLogicalExpression(retStmt.argument) && args.length === 2) {
                    _path.replaceWith(t.logicalExpression(retStmt.argument.operator, args[0], args[1]))
                }
                if (t.isCallExpression(retStmt.argument) && t.isIdentifier(retStmt.argument.callee)) {
                    _path.replaceWith(t.callExpression(args[0], args.slice(1)))
                }
                if (t.isCallExpression(retStmt.argument) && t.isIdentifier(retStmt.argument.callee)) {
                    _path.replaceWith(t.callExpression(args[0], args.slice(1)))
                }
            }
        })
    });
    // 最后删掉这些定义的函数 已经没有用了
    path.remove()
}

// for 结构消除
function generateTransferFile(path, filePath) {  // for 结构消除
    let node = path.node;
    const argValues = node.arguments;
    const paramIdentifiers = node.callee.params.map(n => n.name);
    // 找到var _0x3f0c99 = arguments;中变量名_0x3f0c99，我们改造最后要return出去
    let argVarNode
    path.traverse({
        enter: function (_path) {
            if (_path.node.name === 'arguments') {
                const varPath = _path.find(parentPath => {
                    return parentPath.isVariableDeclarator()
                });
                if (varPath) {
                    argVarNode = varPath.node.id;
                    _path.stop()
                }

            }
        }
    });
    // node.callee.body是BlockStatement, node.callee.body.body是函数体, 由于最后一个是内部的自执行函数，我们先去掉
    const body = node.callee.body.body.slice(0, node.callee.body.body.length - 1);
    // 里面的代码主体
    const mainBody = node.callee.body.body[node.callee.body.body.length - 1];

    // 把转换完的arguments return出去
    const retStatement = t.returnStatement(argVarNode);
    // 套个function的壳子 function transfer(){codes}
    const fn = t.functionDeclaration(t.identifier('transfer'), [], t.blockStatement(body.concat(retStatement)))

    // 因为需要生成一个完整的js，所以我们要补上最外面的program节点 并把函数导出, babel/template可以协助我们把代码的字符串转为ast
    const program = t.file(t.program([fn, template.ast('module.exports = transfer')]));


    traverse(program, {
        Identifier: {
            enter: (path) => {
                // 由于这个转换的时候字符串还是在参数的变量中，我们直接替换
                const node = path.node;
                const idIdx = paramIdentifiers.indexOf(node.name);
                if (idIdx > -1) {
                    let valueNode = argValues[idIdx];
                    path.replaceWith(valueNode)
                }
            }
        },
        StringLiteral: {
            // 替换完变量为字符串才好运行, 所以这一步转判断ast的方法在exit的时候执行
            exit: path => {
                // 代码太长了不贴了..方法都差不多 有兴趣去github看吧
            }
        }
    });

    let { code } = generator(program);
    path.get('callee.body').replaceWith(t.blockStatement([mainBody]));
    fs.writeFileSync(filePath, code, { encoding: 'utf-8' })
}
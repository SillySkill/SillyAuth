# 调试分数计算问题

## 测试步骤

### 1. 重新构建应用

```bash
cd android
gradlew.bat clean assembleDebug
```

### 2. 安装到设备

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### 3. 查看日志

**打开日志监控（在新终端窗口）：**

```bash
# Windows
adb logcat -v time | findstr "QuizActivity"

# 或保存到文件
adb logcat -v time > quiz_debug.log
```

### 4. 测试流程

1. 清空日志：`adb logcat -c`
2. 打开知识问答
3. 答对3题
4. 弹出恭喜窗口
5. 点击"查看详情"
6. 查看日志输出

## 期望的日志输出

正常情况应该看到类似：

```
=== calculateScore 开始 ===
题目总数: 20
userAnswers长度: 20
题目0: userAnswer=0, correctAnswer=0
题目0: 答对 ✓
题目1: userAnswer=1, correctAnswer=1
题目1: 答对 ✓
题目2: userAnswer=0, correctAnswer=0
题目2: 答对 ✓
题目3: userAnswer=-1, correctAnswer=1
题目3: 未作答
...
=== calculateScore 结束, 正确数: 3 ===
```

## 问题排查

### 如果看到 "userAnswers=null"

说明数组没有初始化，检查 loadQuestionsFromBank() 方法

### 如果所有题目都是 "未作答" (userAnswer=-1)

说明答案没有被正确记录，检查 selectAnswer() 方法

### 如果 correctAnswer 都是 0 或异常值

说明题库解析有问题，检查 Question 对象创建

### 如果计算结果正确但显示0分

说明 Intent 传递有问题，检查 showResult() 中的 putExtra

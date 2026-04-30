# Claude Code 子 Agent 系统

基于 `/md/role` 目录下的角色描述，为 Claude Code 搭建的子 Agent 系统，每个 Agent 负责不同的专业能力。

## 系统架构

```
agents/
├── agent-manager.js      # Agent管理器（核心）
├── agent-factory.js      # Agent工厂
├── agents/               # Agent实现
│   ├── security-auditor.js
│   ├── test-writer.js
│   ├── code-reviewer.js
│   ├── refactor-engineer.js
│   └── doc-writer.js
└── README.md
```

## 可用 Agent

### 1. Security Auditor（安全审计员）
- **权限模式**: deny-all（只读）
- **可用工具**: Read, Grep
- **职责**: 找出高风险漏洞与可利用路径，并给出可执行修复建议
- **输出格式**:
  - Critical（必须立刻修）
  - High（优先修）
  - Medium（建议修）
- **检测能力**:
  - SQL注入
  - XSS漏洞
  - 命令注入
  - 硬编码密钥
  - 路径遍历
  - 不安全反序列化
  - 弱加密算法
  - 认证绕过

### 2. Test Writer（测试编写者）
- **权限模式**: inherit（继承）
- **可用工具**: Read, Write, Edit, Grep, Bash
- **职责**: 为变更补齐单测/集成测试，并尽量跑一遍验证
- **支持框架**:
  - Jest/Vitest (JavaScript/TypeScript)
  - Pytest (Python)
  - Go test (Go)
  - JUnit (Java)
- **测试类型**:
  - 单元测试
  - 集成测试
  - API测试

### 3. Code Reviewer（代码审查员）
- **权限模式**: deny-all（只读）
- **可用工具**: Read, Grep
- **职责**: 严格代码审查，给出可执行的 review checklist
- **审查维度**:
  - 逻辑正确性（边界/异常/并发）
  - 可维护性（命名/结构/重复）
  - 性能（热路径/无谓 IO/复杂度）
  - 安全（注入/鉴权/敏感信息）

### 4. Refactor Engineer（重构工程师）
- **权限模式**: inherit（继承）
- **可用工具**: Read, Write, Edit, Grep
- **职责**: 面向可维护性的重构（小步、可验证）
- **重构模式**:
  - 提取函数
  - 提取变量
  - 重命名
  - 引入参数对象
  - 用多态替代条件
  - 合并重复
  - 简化条件

### 5. Doc Writer（文档编写者）
- **权限模式**: inherit（继承）
- **可用工具**: Read, Write, Edit, Grep
- **职责**: 为功能/模块补齐开发者文档（README/ADR/使用示例）
- **文档类型**:
  - README.md
  - API文档
  - ADR（架构决策记录）
  - 使用示例
  - 贡献指南

## 使用方式

### 基本用法

```javascript
const manager = require('./agent-manager');

// 列出所有可用的Agent
const agents = manager.listAgents();
console.log(agents);

// 运行单个Agent
const result = await manager.runAgent('security-auditor', {
  files: ['src/**/*.js'],
  changedCode: [...]
});
```

### 并行运行多个Agent

```javascript
const results = await manager.runParallel([
  {
    agentId: 'security-auditor',
    input: { files: ['src/**/*.js'] }
  },
  {
    agentId: 'code-reviewer',
    input: { files: ['src/**/*.js'] }
  }
]);
```

### 串行运行（Pipeline模式）

```javascript
const context = await manager.runPipeline([
  {
    agentId: 'code-reviewer',
    input: { files: ['src/app.js'] }
  },
  {
    agentId: 'refactor-engineer',
    input: { files: ['src/app.js'] }
  },
  {
    agentId: 'test-writer',
    input: { files: ['src/app.js'] }
  }
]);
```

## Agent输出示例

### Security Auditor 输出

```json
{
  "findings": [
    {
      "file": "src/auth.js",
      "line": 42,
      "severity": "Critical",
      "type": "sqlInjection",
      "description": "SQL注入漏洞：攻击者可以通过输入恶意SQL语句来操作数据库",
      "code": "const query = `SELECT * FROM users WHERE id = ${userId}`;",
      "exploit": "攻击者可以在输入字段中输入 \"1' OR '1'='1\" 来绕过认证",
      "fix": "使用参数化查询（prepared statements）或ORM"
    }
  ],
  "summary": {
    "total": 5,
    "critical": 2,
    "high": 2,
    "medium": 1
  }
}
```

### Code Reviewer 输出

```json
{
  "reviews": [
    {
      "file": "src/utils.js",
      "issues": [
        {
          "category": "logic",
          "check": "边界条件",
          "message": "循环缺少边界条件检查",
          "suggestion": "添加循环边界检查，防止无限循环或数组越界"
        }
      ],
      "suggestions": [
        {
          "category": "maintainability",
          "check": "函数长度",
          "message": "函数过长（67 行）",
          "suggestion": "将长函数拆分为多个小函数"
        }
      ]
    }
  ],
  "overall": {
    "verdict": "需要小幅度修改后可以合并",
    "totalIssues": 3,
    "totalSuggestions": 5
  }
}
```

### Refactor Engineer 输出

```json
{
  "refactorsApplied": 4,
  "changes": [
    {
      "file": "src/api.js",
      "type": "extractFunction",
      "success": true,
      "changes": {
        "description": "将 processRequest 中的代码提取为独立函数",
        "steps": [
          "1. 识别可提取的逻辑块",
          "2. 创建新函数，将代码移入",
          "3. 替换原代码为函数调用",
          "4. 编写测试验证行为不变"
        ]
      }
    }
  ],
  "rollbackPlan": [
    {
      "file": "src/api.js",
      "backup": { "location": "src/api.js.backup" },
      "command": "cp src/api.js.backup src/api.js"
    }
  ]
}
```

## 权限模式说明

### deny-all（只读模式）
- 只能使用 Read 和 Grep 工具
- 不能修改文件系统
- 适用于：安全审计、代码审查

### inherit（继承模式）
- 可以使用所有可用工具
- 可以修改文件系统
- 适用于：测试编写、重构、文档编写

## 集成到 Claude Code

可以通过以下方式将这些 Agent 集成到 Claude Code 的技能系统中：

### 方法1：作为技能调用

```javascript
// 在 Claude Code 技能系统中注册
{
  "name": "security-audit",
  "agent": "security-auditor",
  "description": "运行安全审计"
}
```

### 方法2：作为预提交钩子

```bash
# 在 git commit 前自动运行
npm run agents:security
npm run agents:review
```

### 方法3：作为 CI/CD 流程

```yaml
# .github/workflows/agents.yml
- name: Run Code Review
  run: npm run agents:review

- name: Run Security Audit
  run: npm run agents:security
```

## 扩展新 Agent

要添加新的 Agent，按照以下步骤：

1. 在 `/md/role` 下创建角色描述文件
2. 在 `agents/` 目录下创建实现文件
3. 在 `agent-manager.js` 中注册新 Agent

示例：

```javascript
// agent-manager.js
manager.register('new-agent', {
  name: 'New Agent',
  description: 'Agent描述',
  tools: ['Read', 'Write'],
  permissionMode: 'inherit',
  handler: require('./agents/new-agent')
});
```

## 最佳实践

1. **使用合适的权限模式**: 只读操作使用 deny-all，需要修改时使用 inherit
2. **优先使用并行运行**: 对于独立的任务，使用 runParallel 提高效率
3. **注意顺序依赖**: 后一个 Agent 需要前一个的输出时，使用 runPipeline
4. **保存回滚计划**: Refactor Engineer 会生成回滚计划，确保可以撤销变更
5. **审查输出**: Agent 提供的是建议，最终决定权在开发者

## 许可证

MIT

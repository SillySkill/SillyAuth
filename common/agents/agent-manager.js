/**
 * Agent Manager - 子Agent管理系统
 * 负责创建和管理具有不同专业能力的子Agent
 */

const { createAgent } = require('./agent-factory');

class AgentManager {
  constructor() {
    this.agents = new Map();
  }

  /**
   * 注册一个Agent
   */
  register(agentId, config) {
    this.agents.set(agentId, config);
  }

  /**
   * 获取Agent配置
   */
  getAgent(agentId) {
    return this.agents.get(agentId);
  }

  /**
   * 列出所有可用的Agent
   */
  listAgents() {
    return Array.from(this.agents.entries()).map(([id, config]) => ({
      id,
      name: config.name,
      description: config.description,
      tools: config.tools,
      permissionMode: config.permissionMode
    }));
  }

  /**
   * 创建Agent实例
   */
  createAgent(agentId, context = {}) {
    const config = this.agents.get(agentId);
    if (!config) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    return createAgent(config, context);
  }

  /**
   * 并行运行多个Agent
   */
  async runParallel(tasks) {
    const results = await Promise.allSettled(
      tasks.map(task => this.runAgent(task.agentId, task.input, task.options))
    );

    return results.map((result, index) => ({
      agentId: tasks[index].agentId,
      status: result.status,
      value: result.status === 'fulfilled' ? result.value : result.reason
    }));
  }

  /**
   * 串行运行多个Agent（后一个可以使用前一个的输出）
   */
  async runPipeline(tasks, initialContext = {}) {
    let context = initialContext;

    for (const task of tasks) {
      const result = await this.runAgent(
        task.agentId,
        { ...task.input, context },
        task.options
      );
      context = { ...context, [task.agentId]: result };
    }

    return context;
  }

  /**
   * 运行单个Agent
   */
  async runAgent(agentId, input, options = {}) {
    const agent = this.createAgent(agentId, options.context);
    return agent.execute(input, options);
  }
}

// 全局单例
const manager = new AgentManager();

// 注册内置Agent
manager.register('security-auditor', {
  name: 'Security Auditor',
  description: '安全审计与合规检查（只读）',
  tools: ['Read', 'Grep'],
  permissionMode: 'deny-all',
  handler: require('./agents/security-auditor')
});

manager.register('test-writer', {
  name: 'Test Writer',
  description: '为变更补齐单测/集成测试，并尽量跑一遍验证',
  tools: ['Read', 'Write', 'Edit', 'Grep', 'Bash'],
  permissionMode: 'inherit',
  handler: require('./agents/test-writer')
});

manager.register('code-reviewer', {
  name: 'Code Reviewer',
  description: '严格代码审查（只读），给出可执行的 review checklist',
  tools: ['Read', 'Grep'],
  permissionMode: 'deny-all',
  handler: require('./agents/code-reviewer')
});

manager.register('refactor-engineer', {
  name: 'Refactor Engineer',
  description: '面向可维护性的重构（小步、可验证）',
  tools: ['Read', 'Write', 'Edit', 'Grep'],
  permissionMode: 'inherit',
  handler: require('./agents/refactor-engineer')
});

manager.register('doc-writer', {
  name: 'Doc Writer',
  description: '为功能/模块补齐开发者文档（README/ADR/使用示例）',
  tools: ['Read', 'Write', 'Edit', 'Grep'],
  permissionMode: 'inherit',
  handler: require('./agents/doc-writer')
});

module.exports = manager;

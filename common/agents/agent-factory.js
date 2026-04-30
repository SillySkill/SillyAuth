/**
 * Agent Factory - Agent创建工厂
 */

class Agent {
  constructor(config, context = {}) {
    this.name = config.name;
    this.description = config.description;
    this.tools = config.tools;
    this.permissionMode = config.permissionMode;
    this.handler = config.handler;
    this.context = context;
  }

  /**
   * 执行Agent任务
   */
  async execute(input, options = {}) {
    // 检查权限
    this.checkPermissions(options);

    // 执行具体的Agent逻辑
    const result = await this.handler.execute(input, {
      ...options,
      context: this.context
    });

    return this.formatOutput(result);
  }

  /**
   * 检查权限模式
   */
  checkPermissions(options) {
    if (this.permissionMode === 'deny-all') {
      const deniedTools = ['Write', 'Edit', 'Bash'];
      const requestedTools = options.tools || [];

      for (const tool of requestedTools) {
        if (deniedTools.includes(tool)) {
          throw new Error(
            `Agent "${this.name}" has deny-all permission mode and cannot use ${tool}`
          );
        }
      }
    }
  }

  /**
   * 格式化输出
   */
  formatOutput(result) {
    return {
      agent: this.name,
      timestamp: new Date().toISOString(),
      ...result
    };
  }
}

function createAgent(config, context) {
  return new Agent(config, context);
}

module.exports = { createAgent, Agent };

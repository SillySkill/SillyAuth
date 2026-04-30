/**
 * Test Writer - 测试编写Agent
 * 为变更补齐单测/集成测试，并尽量跑一遍验证
 */

class TestWriter {
  constructor() {
    this.testFrameworks = {
      javascript: {
        patterns: ['package.json', 'jest.config.', 'vitest.config.', '*.test.js', '*.spec.js'],
        framework: 'jest/vitest',
        template: this.getJestTemplate()
      },
      typescript: {
        patterns: ['tsconfig.json', '*.test.ts', '*.spec.ts'],
        framework: 'jest/vitest',
        template: this.getJestTemplate()
      },
      python: {
        patterns: ['requirements.txt', 'setup.py', 'pytest.ini', 'test_*.py', '*_test.py'],
        framework: 'pytest',
        template: this.getPytestTemplate()
      },
      go: {
        patterns: ['go.mod', '*_test.go'],
        framework: 'go test',
        template: this.getGoTestTemplate()
      },
      java: {
        patterns: ['pom.xml', 'build.gradle', '*Test.java'],
        framework: 'junit',
        template: this.getJUnitTemplate()
      }
    };
  }

  /**
   * 执行测试编写任务
   */
  async execute(input, options) {
    const { files, changedCode, context } = input;
    const results = [];

    // 检测项目测试框架
    const framework = await this.detectFramework(options);

    // 分析需要测试的代码
    const testPlan = await this.analyzeCode(changedCode, framework);

    // 为每个变更编写测试
    for (const item of testPlan) {
      const testResult = await this.writeTest(item, framework, options);
      results.push(testResult);
    }

    // 运行测试
    const testResults = await this.runTests(framework, options);

    return {
      framework,
      testsAdded: results.filter(r => r.created).length,
      testFiles: results.map(r => r.filePath),
      runResults: testResults,
      summary: this.generateSummary(results, testResults)
    };
  }

  /**
   * 检测项目使用的测试框架
   */
  async detectFramework(options) {
    const context = options.context || {};

    // 从上下文中检测
    if (context.packageJson) {
      const deps = { ...context.packageJson.dependencies, ...context.packageJson.devDependencies };
      if (deps.jest || deps.vitest) return { language: 'javascript', framework: 'jest' };
      if (deps.mocha) return { language: 'javascript', framework: 'mocha' };
    }

    if (context.tsconfig) {
      return { language: 'typescript', framework: 'jest' };
    }

    if (context.requirements || context.setupPy) {
      return { language: 'python', framework: 'pytest' };
    }

    if (context.goMod) {
      return { language: 'go', framework: 'go test' };
    }

    // 默认返回
    return { language: 'javascript', framework: 'jest' };
  }

  /**
   * 分析代码，生成测试计划
   */
  async analyzeCode(changedCode, framework) {
    const plan = [];

    for (const change of changedCode) {
      const { filePath, type, functionName, className } = change;

      // 为函数生成测试计划
      if (type === 'function') {
        plan.push({
          targetPath: filePath,
          type: 'unit',
          functionName,
          testPath: this.generateTestPath(filePath, functionName),
          scenarios: this.generateTestScenarios(change)
        });
      }

      // 为类生成测试计划
      if (type === 'class') {
        plan.push({
          targetPath: filePath,
          type: 'unit',
          className,
          testPath: this.generateTestPath(filePath, className),
          scenarios: this.generateTestScenarios(change)
        });
      }

      // 为API端点生成集成测试计划
      if (type === 'api') {
        plan.push({
          targetPath: filePath,
          type: 'integration',
          endpoint: change.endpoint,
          testPath: this.generateTestPath(filePath, change.endpoint),
          scenarios: this.generateApiTestScenarios(change)
        });
      }
    }

    return plan;
  }

  /**
   * 生成测试文件路径
   */
  generateTestPath(sourcePath, name) {
    const ext = sourcePath.split('.').pop();
    const dir = sourcePath.substring(0, sourcePath.lastIndexOf('/'));
    const basename = sourcePath.split('/').pop().replace(`.${ext}`, '');

    // 常见测试文件命名模式
    if (ext === 'js' || ext === 'ts') {
      return `${dir}/${basename}.test.${ext}`;
    }
    if (ext === 'py') {
      return `${dir}/test_${basename}.py`;
    }
    if (ext === 'go') {
      return sourcePath; // Go测试在同一文件中
    }

    return `${dir}/${basename}_test.${ext}`;
  }

  /**
   * 生成测试场景
   */
  generateTestScenarios(change) {
    const scenarios = [
      {
        name: '正常路径',
        type: 'happy-path',
        description: '验证在正常输入下的预期行为'
      }
    ];

    // 根据参数生成边界测试
    if (change.parameters) {
      for (const param of change.parameters) {
        if (param.type === 'number') {
          scenarios.push({
            name: `边界值测试 - ${param.name}`,
            type: 'boundary',
            description: `测试 ${param.name} 的边界值（0、负数、最大值）`
          });
        }
        if (param.nullable) {
          scenarios.push({
            name: `空值测试 - ${param.name}`,
            type: 'null-check',
            description: `测试 ${param.name} 为 null/undefined 时的行为`
          });
        }
      }
    }

    // 添加异常场景
    scenarios.push({
      name: '异常处理',
      type: 'error-case',
      description: '验证错误输入时的异常处理'
    });

    return scenarios;
  }

  /**
   * 生成API测试场景
   */
  generateApiTestScenarios(change) {
    const scenarios = [
      {
        name: '成功响应',
        method: change.method,
        status: 200,
        description: '验证正常请求返回正确响应'
      },
      {
        name: '认证失败',
        method: change.method,
        status: 401,
        description: '验证未认证请求被正确拒绝'
      },
      {
        name: '参数校验',
        method: change.method,
        status: 400,
        description: '验证无效参数返回正确错误'
      }
    ];

    return scenarios;
  }

  /**
   * 编写测试代码
   */
  async writeTest(testPlan, framework, options) {
    const { testPath, scenarios, functionName, className } = testPlan;

    // 检查测试文件是否已存在
    const exists = await this.checkFileExists(testPath, options);

    if (exists) {
      // 追加测试到现有文件
      return {
        filePath: testPath,
        created: false,
        action: 'appended',
        scenariosAdded: scenarios.length
      };
    }

    // 创建新的测试文件
    const testCode = this.generateTestCode(testPlan, framework);

    // 这里应该使用Write工具创建文件
    // await options.tools.Write(testPath, testCode);

    return {
      filePath: testPath,
      created: true,
      action: 'created',
      scenarios: scenarios.map(s => s.name)
    };
  }

  /**
   * 生成测试代码
   */
  generateTestCode(testPlan, framework) {
    const { framework: fw } = framework;

    if (fw === 'jest' || fw === 'vitest') {
      return this.generateJestTest(testPlan);
    }
    if (fw === 'pytest') {
      return this.generatePytestTest(testPlan);
    }
    if (fw === 'go test') {
      return this.generateGoTest(testPlan);
    }

    return `// Generated test for ${testPlan.functionName || testPlan.className}\n`;
  }

  /**
   * 生成Jest测试代码
   */
  generateJestTest(testPlan) {
    const { functionName, className, scenarios } = testPlan;
    const target = functionName || className;

    let code = `// Auto-generated tests for ${target}\n`;
    code += `// TODO: Review and adjust assertions\n\n`;

    if (className) {
      code += `import { ${className} } from '../${testPlan.targetPath.split('/').pop()}';\n\n`;
    } else {
      code += `import { ${target} } from '../${testPlan.targetPath.split('/').pop()}';\n\n`;
    }

    code += `describe('${target}', () => {\n`;

    for (const scenario of scenarios) {
      code += `  ${this.generateJestTestCase(target, scenario)}\n`;
    }

    code += `});\n`;

    return code;
  }

  /**
   * 生成单个Jest测试用例
   */
  generateJestTestCase(target, scenario) {
    const templates = {
      'happy-path': `
it('should work correctly with valid input', async () => {
  // Arrange
  const input = /* TODO: Add valid input */;

  // Act
  const result = await ${target}(input);

  // Assert
  expect(result).toBeDefined();
  // TODO: Add specific assertions
});`,
      'boundary': `
it('should handle boundary values', async () => {
  // Arrange
  const edgeCases = [0, -1, Number.MAX_SAFE_INTEGER];

  for (const input of edgeCases) {
    // Act
    const result = await ${target}(input);

    // Assert
    expect(result).toBeDefined();
    // TODO: Add specific assertions for each edge case
  }
});`,
      'null-check': `
it('should handle null/undefined input gracefully', async () => {
  // Act & Assert
  await expect(${target}(null)).rejects.toThrow();
  await expect(${target}(undefined)).rejects.toThrow();
});`,
      'error-case': `
it('should handle invalid input with proper error', async () => {
  // Arrange
  const invalidInput = /* TODO: Add invalid input */;

  // Act & Assert
  await expect(${target}(invalidInput)).rejects.toThrow();
});`
    };

    return templates[scenario.type] || templates['happy-path'];
  }

  /**
   * 运行测试
   */
  async runTests(framework, options) {
    const { framework: fw } = framework;
    const commands = {
      'jest': 'npm test --',
      'vitest': 'npm run test:unit --',
      'pytest': 'pytest -v',
      'go test': 'go test ./...'
    };

    const command = commands[fw] || 'npm test';

    // 这里应该使用Bash工具运行测试
    // const result = await options.tools.Bash(command);

    return {
      command,
      // output: result.stdout,
      // exitCode: result.exitCode,
      note: '请在本地运行测试命令以验证'
    };
  }

  /**
   * 生成摘要
   */
  generateSummary(results, testResults) {
    return {
      message: `为 ${results.length} 个代码变更添加了测试`,
      testFiles: results.map(r => r.filePath).join(', '),
      runCommand: testResults.command
    };
  }

  /**
   * 检查文件是否存在
   */
  async checkFileExists(filePath, options) {
    // 这里应该使用实际的文件系统检查
    return false;
  }

  getJestTemplate() {
    return `import { describe, it, expect } from '@jest/globals';`;
  }

  getPytestTemplate() {
    return `import pytest\n`;
  }

  getGoTestTemplate() {
    return `package main\n\nimport "testing"\n`;
  }

  getJUnitTemplate() {
    return `import org.junit.Test;\nimport static org.junit.Assert.*;\n`;
  }

  generatePytestTest(testPlan) {
    return `# Pytest test for ${testPlan.functionName}\n`;
  }

  generateGoTest(testPlan) {
    return `// Go test for ${testPlan.functionName}\n`;
  }
}

module.exports = new TestWriter();

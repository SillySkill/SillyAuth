/**
 * Doc Writer - 文档编写Agent
 * 为功能/模块补齐开发者文档（README/ADR/使用示例）
 */

class DocWriter {
  constructor() {
    this.docTypes = {
      readme: {
        name: 'README',
        description: '项目主文档',
        template: this.getReadmeTemplate()
      },
      api: {
        name: 'API文档',
        description: 'API接口文档',
        template: this.getApiTemplate()
      },
      adr: {
        name: 'ADR',
        description: '架构决策记录',
        template: this.getAdrTemplate()
      },
      usage: {
        name: '使用示例',
        description: '代码使用示例',
        template: this.getUsageTemplate()
      },
      contributing: {
        name: '贡献指南',
        description: '如何贡献代码',
        template: this.getContributingTemplate()
      }
    };
  }

  /**
   * 执行文档编写任务
   */
  async execute(input, options) {
    const { files, docType, context } = input;

    const results = [];

    // 分析代码，生成文档内容
    const analysis = await this.analyzeCode(files, options);

    // 根据文档类型生成文档
    if (docType === 'all' || !docType) {
      // 生成所有类型的文档
      for (const type of Object.keys(this.docTypes)) {
        const result = await this.generateDoc(type, analysis, options);
        results.push(result);
      }
    } else {
      const result = await this.generateDoc(docType, analysis, options);
      results.push(result);
    }

    return {
      docsCreated: results.filter(r => r.created).length,
      docs: results,
      summary: this.generateSummary(results)
    };
  }

  /**
   * 分析代码以生成文档
   */
  async analyzeCode(files, options) {
    const analysis = {
      project: {},
      modules: [],
      apis: [],
      examples: []
    };

    for (const filePath of files) {
      const moduleInfo = await this.analyzeFile(filePath, options);

      if (moduleInfo.type === 'entry' || filePath.includes('package.json')) {
        analysis.project = { ...analysis.project, ...moduleInfo };
      } else if (moduleInfo.type === 'api') {
        analysis.apis.push(moduleInfo);
      } else {
        analysis.modules.push(moduleInfo);
      }
    }

    return analysis;
  }

  /**
   * 分析单个文件
   */
  async analyzeFile(filePath, options) {
    const info = {
      path: filePath,
      name: filePath.split('/').pop(),
      type: 'module'
    };

    try {
      // 获取文件内容（实际应使用Read工具）
      const content = options.context?.fileContents?.[filePath] || '';

      // 检测文件类型
      if (filePath.includes('package.json')) {
        info.type = 'entry';
        Object.assign(info, this.parsePackageJson(content));
      } else if (filePath.includes('router.') || filePath.includes('route') || filePath.includes('controller')) {
        info.type = 'api';
        Object.assign(info, this.parseApiFile(content));
      } else {
        Object.assign(info, this.parseModuleFile(content));
      }

    } catch (error) {
      info.error = error.message;
    }

    return info;
  }

  /**
   * 解析 package.json
   */
  parsePackageJson(content) {
    try {
      const pkg = JSON.parse(content);
      return {
        name: pkg.name || 'Untitled Project',
        version: pkg.version,
        description: pkg.description || '',
        scripts: pkg.scripts || {},
        dependencies: Object.keys(pkg.dependencies || {}),
        devDependencies: Object.keys(pkg.devDependencies || {})
      };
    } catch {
      return {};
    }
  }

  /**
   * 解析API文件
   */
  parseApiFile(content) {
    const endpoints = [];

    // 匹配路由定义
    const routePatterns = [
      /router\.(get|post|put|delete|patch)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      /app\.(get|post|put|delete|patch)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      /@(Get|Post|Put|Delete|Patch)\s*\(\s*['"`]([^'"`]+)['"`]/g
    ];

    for (const pattern of routePatterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        endpoints.push({
          method: match[1].toUpperCase(),
          path: match[2],
          line: this.getLineNumber(content, match.index)
        });
      }
    }

    return { endpoints };
  }

  /**
   * 解析模块文件
   */
  parseModuleFile(content) {
    const info = {
      exports: [],
      functions: [],
      classes: []
    };

    // 匹配导出的函数
    const exportPatterns = [
      /export\s+(?:const|function)\s+(\w+)/g,
      /module\.exports\s*=\s*(\w+)/g,
      /exports\.(\w+)\s*=/g
    ];

    for (const pattern of exportPatterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        info.exports.push(match[1]);
      }
    }

    // 匹配类定义
    const classPattern = /class\s+(\w+)/g;
    let match;
    while ((match = classPattern.exec(content)) !== null) {
      info.classes.push(match[1]);
    }

    return info;
  }

  /**
   * 生成文档
   */
  async generateDoc(docType, analysis, options) {
    const template = this.docTypes[docType];
    if (!template) {
      throw new Error(`未知的文档类型: ${docType}`);
    }

    const content = this.renderTemplate(template, analysis);

    // 确定文档路径
    const docPath = this.getDocPath(docType, analysis);

    // 检查文档是否已存在
    const exists = await this.checkDocExists(docPath, options);

    // 这里应该使用Write工具写入文档
    // await options.tools.Write(docPath, content);

    return {
      type: docType,
      path: docPath,
      created: !exists,
      content: content.substring(0, 200) + '...'
    };
  }

  /**
   * 渲染模板
   */
  renderTemplate(template, analysis) {
    let content = template.template;

    // 替换项目信息
    content = content.replace(/\{\{projectName\}\}/g, analysis.project.name || 'Project');
    content = content.replace(/\{\{description\}\}/g, analysis.project.description || '项目描述');
    content = content.replace(/\{\{version\}\}/g, analysis.project.version || '1.0.0');

    // 替换脚本
    if (analysis.project.scripts) {
      const scriptsSection = this.generateScriptsSection(analysis.project.scripts);
      content = content.replace(/\{\{scripts\}\}/g, scriptsSection);
    }

    // 替换API文档
    if (analysis.apis.length > 0) {
      const apiSection = this.generateApiSection(analysis.apis);
      content = content.replace(/\{\{apiSection\}\}/g, apiSection);
    }

    // 替换模块列表
    if (analysis.modules.length > 0) {
      const modulesSection = this.generateModulesSection(analysis.modules);
      content = content.replace(/\{\{modules\}\}/g, modulesSection);
    }

    return content;
  }

  /**
   * 生成脚本部分
   */
  generateScriptsSection(scripts) {
    let section = '## 可用脚本\n\n';

    for (const [name, command] of Object.entries(scripts)) {
      section += `### \`${name}\`\n\n`;
      section += `\`\`\`bash\nnpm run ${name}\n\`\`\`\n\n`;
    }

    return section;
  }

  /**
   * 生成API部分
   */
  generateApiSection(apis) {
    let section = '## API 文档\n\n';

    for (const api of apis) {
      if (api.endpoints) {
        for (const endpoint of api.endpoints) {
          section += `### ${endpoint.method} ${endpoint.path}\n\n`;
          section += `定义于: \`${api.path}:${endpoint.line}\`\n\n`;
          section += `**请求示例：**\n\n`;
          section += `\`\`\`bash\n`;
          section += `curl -X ${endpoint.method} http://localhost:3000${endpoint.path}\n`;
          section += `\`\`\`\n\n`;
        }
      }
    }

    return section;
  }

  /**
   * 生成模块部分
   */
  generateModulesSection(modules) {
    let section = '## 模块说明\n\n';

    for (const module of modules) {
      section += `### ${module.name}\n\n`;
      if (module.exports && module.exports.length > 0) {
        section += `导出: ${module.exports.join(', ')}\n\n`;
      }
      if (module.classes && module.classes.length > 0) {
        section += `类: ${module.classes.join(', ')}\n\n`;
      }
    }

    return section;
  }

  /**
   * 获取文档路径
   */
  getDocPath(docType, analysis) {
    const paths = {
      readme: 'README.md',
      api: 'docs/API.md',
      adr: 'docs/ADR/001-initial-architecture.md',
      usage: 'docs/USAGE.md',
      contributing: 'CONTRIBUTING.md'
    };
    return paths[docType] || `${docType}.md`;
  }

  /**
   * 检查文档是否存在
   */
  async checkDocExists(docPath, options) {
    // 这里应该使用实际的文件系统检查
    return false;
  }

  /**
   * 获取行号
   */
  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  /**
   * 生成摘要
   */
  generateSummary(results) {
    const created = results.filter(r => r.created).map(r => r.path);
    const updated = results.filter(r => !r.created).map(r => r.path);

    return {
      message: `文档生成完成`,
      created,
      updated,
      allPaths: results.map(r => r.path)
    };
  }

  /**
   * 模板定义
   */
  getReadmeTemplate() {
    return `# {{projectName}}

{{description}}

## 安装

\`\`\`bash
npm install
\`\`\`

## 快速开始

\`\`\`bash
npm install
npm start
\`\`\`

{{scripts}}

{{modules}}

## 许可证

MIT
`;
  }

  getApiTemplate() {
    return `# API 文档

{{apiSection}}

## 请求格式

所有API请求使用JSON格式：

\`\`\`json
{
  "data": "value"
}
\`\`\`

## 响应格式

成功响应：

\`\`\`json
{
  "success": true,
  "data": {}
}
\`\`\`

错误响应：

\`\`\`json
{
  "success": false,
  "error": "错误信息"
}
\`\`\`
`;
  }

  getAdrTemplate() {
    return `# ADR 001: 初始架构设计

## 状态
已采纳

## 上下文
需要为项目选择初始架构。

## 决策
采用模块化架构，各模块职责清晰。

## 后果
- 优点：易于维护和扩展
- 缺点：初期开发速度较慢
`;
  }

  getUsageTemplate() {
    return `# 使用示例

## 基本用法

\`\`\`javascript
const {{projectName}} = require('{{projectName}}');

// 使用示例
const result = {{projectName}}.doSomething();
\`\`\`

## 高级用法

\`\`\`javascript
// 配置选项
const options = {
  debug: true,
  timeout: 5000
};

const result = {{projectName}}.doSomething(options);
\`\`\`

## 常见问题

### 问题1

解决方案描述。

### 问题2

解决方案描述。
`;
  }

  getContributingTemplate() {
    return `# 贡献指南

感谢您的贡献！

## 开发流程

1. Fork 项目
2. 创建特性分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交更改 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 开启 Pull Request

## 代码规范

- 使用 ESLint 进行代码检查
- 遵循现有代码风格
- 添加必要的测试

## 提交信息规范

\`\`
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
\`\``
  }
}

module.exports = new DocWriter();

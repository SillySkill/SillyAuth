/**
 * Refactor Engineer - 重构Agent
 * 面向可维护性的重构（小步、可验证）
 */

class RefactorEngineer {
  constructor() {
    this.refactorPatterns = {
      extractFunction: {
        name: '提取函数',
        description: '将一段重复或复杂的逻辑提取为独立函数',
        trigger: '代码重复或函数过长'
      },
      extractVariable: {
        name: '提取变量',
        description: '将复杂表达式提取为有意义的变量',
        trigger: '表达式复杂或重复计算'
      },
      renameSymbol: {
        name: '重命名',
        description: '将符号名称改为更具描述性的名称',
        trigger: '命名不够清晰'
      },
      introduceParameterObject: {
        name: '引入参数对象',
        description: '将多个相关参数组合成对象',
        trigger: '参数过多（超过4个）'
      },
      replaceConditionalWithPolymorphism: {
        name: '用多态替代条件',
        description: '使用继承/接口替代复杂的条件语句',
        trigger: '重复的 switch/case 或 if/else if'
      },
      decomposeConditional: {
        name: '分解条件',
        description: '将复杂的条件表达式分解为独立函数',
        trigger: '条件表达式过于复杂'
      },
      consolidateDuplicate: {
        name: '合并重复',
        description: '将重复的代码片段合并为一个',
        trigger: '存在重复代码'
      },
      simplifyConditional: {
        name: '简化条件',
        description: '使用卫语句等简化嵌套条件',
        trigger: '深层嵌套的 if/else'
      }
    };
  }

  /**
   * 执行重构任务
   */
  async execute(input, options) {
    const { files, refactorScope, context } = input;

    const results = [];

    // 分析代码，识别重构机会
    const opportunities = await this.analyzeRefactorOpportunities(files, options);

    // 如果指定了重构范围，筛选相关的机会
    const scopedOpportunities = this.filterByScope(opportunities, refactorScope);

    // 按优先级排序
    const prioritized = this.prioritizeOpportunities(scopedOpportunities);

    // 执行重构
    for (const opportunity of prioritized) {
      const result = await this.applyRefactor(opportunity, options);
      results.push(result);
    }

    return {
      refactorsApplied: results.length,
      changes: results,
      summary: this.generateSummary(results),
      rollbackPlan: this.generateRollbackPlan(results)
    };
  }

  /**
   * 分析重构机会
   */
  async analyzeRefactorOpportunities(files, options) {
    const opportunities = [];

    for (const filePath of files) {
      const fileOpportunities = await this.analyzeFile(filePath, options);
      opportunities.push(...fileOpportunities);
    }

    return opportunities;
  }

  /**
   * 分析单个文件
   */
  async analyzeFile(filePath, options) {
    const opportunities = [];

    try {
      // 获取文件内容（实际应使用Read工具）
      const content = options.context?.fileContents?.[filePath] || '';

      // 检测各种重构机会
      opportunities.push(...this.detectExtractFunction(content, filePath));
      opportunities.push(...this.detectExtractVariable(content, filePath));
      opportunities.push(...this.detectRenameOpportunities(content, filePath));
      opportunities.push(...this.detectParameterObject(content, filePath));
      opportunities.push(...this.detectPolymorphism(content, filePath));
      opportunities.push(...this.detectDuplicateCode(content, filePath));
      opportunities.push(...this.detectComplexConditional(content, filePath));

    } catch (error) {
      // 无法分析的文件
    }

    return opportunities;
  }

  /**
   * 检测提取函数的机会
   */
  detectExtractFunction(content, filePath) {
    const opportunities = [];
    const lines = content.split('\n');
    let currentFunction = null;
    let functionStart = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // 检测函数定义
      const functionMatch = line.match(/(function|const\s+\w+\s*=\s*(?:async\s*)?\(|def\s+(\w+))/);
      if (functionMatch) {
        currentFunction = functionMatch[2] || functionMatch[3] || 'anonymous';
        functionStart = i;
        continue;
      }

      // 检测函数结束
      if (currentFunction && /^\s*}\s*$/.test(line)) {
        const functionLength = i - functionStart;
        if (functionLength > 30) {
          opportunities.push({
            type: 'extractFunction',
            file: filePath,
            functionName: currentFunction,
            startLine: functionStart + 1,
            endLine: i + 1,
            reason: `函数过长（${functionLength} 行），建议拆分`,
            priority: functionLength > 50 ? 'high' : 'medium',
            effort: 'medium'
          });
        }
        currentFunction = null;
      }

      // 检测重复代码块
      const codeBlock = line.trim();
      if (codeBlock.length > 50) {
        const occurrences = this.countOccurrences(content, codeBlock);
        if (occurrences > 1) {
          opportunities.push({
            type: 'extractFunction',
            file: filePath,
            codeSnippet: codeBlock.substring(0, 50) + '...',
            reason: '重复代码块，应提取为函数',
            priority: 'high',
            effort: 'low'
          });
        }
      }
    }

    return opportunities;
  }

  /**
   * 检测提取变量的机会
   */
  detectExtractVariable(content, filePath) {
    const opportunities = [];
    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // 检测复杂表达式
      if (line.includes('&&') || line.includes('||')) {
        const operators = (line.match(/&&|\|\|/g) || []).length;
        if (operators >= 3) {
          opportunities.push({
            type: 'extractVariable',
            file: filePath,
            line: i + 1,
            code: line.trim(),
            reason: '复杂条件表达式，应提取为有意义的变量',
            priority: 'medium',
            effort: 'low'
          });
        }
      }

      // 检测重复计算
      const calculations = line.match(/[\w.]+\s*[\+\-\*\/]\s*[\w.]+/g) || [];
      for (const calc of calculations) {
        const occurrences = this.countOccurrences(content, calc);
        if (occurrences > 2) {
          opportunities.push({
            type: 'extractVariable',
            file: filePath,
            line: i + 1,
            expression: calc,
            reason: '重复计算，应提取为变量',
            priority: 'low',
            effort: 'low'
          });
        }
      }
    }

    return opportunities;
  }

  /**
   * 检测重命名机会
   */
  detectRenameOpportunities(content, filePath) {
    const opportunities = [];

    // 检测单字母变量（除了循环变量）
    const singleLetterVars = content.match(/(?:let|const|var)\s+([a-z])\s*=/g) || [];
    for (const match of singleLetterVars) {
      const varName = match.match(/(?:let|const|var)\s+([a-z])\s*=/)[1];
      if (!['i', 'j', 'k', 'x', 'y', '_'].includes(varName)) {
        opportunities.push({
          type: 'renameSymbol',
          file: filePath,
          symbol: varName,
          reason: '变量名不够描述性',
          suggestion: `更具描述性的名称（如：${this.suggestBetterName(varName)}）`,
          priority: 'low',
          effort: 'low'
        });
      }
    }

    // 检测缩写
    const abbreviations = content.match(/\b(cnt|conf|msg|req|res|err|tmp|ctx)\b/g) || [];
    for (const abbr of new Set(abbreviations)) {
      opportunities.push({
        type: 'renameSymbol',
        file: filePath,
        symbol: abbr,
        reason: '使用缩写降低可读性',
        suggestion: this.expandAbbreviation(abbr),
        priority: 'low',
        effort: 'low'
      });
    }

    return opportunities;
  }

  /**
   * 检测参数对象机会
   */
  detectParameterObject(content, filePath) {
    const opportunities = [];

    const functionDefs = content.match(
      /(?:function|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\()([^(]*\))/g
    ) || [];

    for (const funcDef of functionDefs) {
      const params = funcDef.match(/\(([^)]+)\)/);
      if (params) {
        const paramList = params[1].split(',').map(p => p.trim());
        if (paramList.length > 4) {
          opportunities.push({
            type: 'introduceParameterObject',
            file: filePath,
            parameters: paramList,
            reason: `参数过多（${paramList.length} 个），建议使用参数对象`,
            suggestion: this.suggestParameterObjectName(funcDef),
            priority: 'medium',
            effort: 'medium'
          });
        }
      }
    }

    return opportunities;
  }

  /**
   * 检测多态机会
   */
  detectPolymorphism(content, filePath) {
    const opportunities = [];

    // 检测重复的 switch/case
    const switchBlocks = content.match(/switch\s*\([^)]+\)\s*{[\s\S]*?}/g) || [];
    for (const switchBlock of switchBlocks) {
      const cases = (switchBlock.match(/case\s+[\w.]+:/g) || []).length;
      if (cases >= 3) {
        opportunities.push({
          type: 'replaceConditionalWithPolymorphism',
          file: filePath,
          reason: `存在 ${cases} 个 case 的 switch，考虑使用多态`,
          priority: 'medium',
          effort: 'high'
        });
      }
    }

    // 检测重复的 if/else if 链
    const ifChains = content.match(/if\s*\([^)]+\)\s*{[\s\S]*?}\s*else\s+if/g) || [];
    for (const ifChain of ifChains) {
      const conditions = (ifChain.match(/else\s+if/g) || []).length + 1;
      if (conditions >= 4) {
        opportunities.push({
          type: 'replaceConditionalWithPolymorphism',
          file: filePath,
          reason: `存在 ${conditions} 个分支的 if/else if，考虑使用多态`,
          priority: 'low',
          effort: 'high'
        });
      }
    }

    return opportunities;
  }

  /**
   * 检测重复代码
   */
  detectDuplicateCode(content, filePath) {
    const opportunities = [];
    const lines = content.split('\n');
    const minBlockLength = 3;

    for (let i = 0; i < lines.length - minBlockLength; i++) {
      const block = lines.slice(i, i + minBlockLength).join('\n');
      const rest = lines.slice(i + minBlockLength).join('\n');

      if (rest.includes(block)) {
        opportunities.push({
          type: 'consolidateDuplicate',
          file: filePath,
          startLine: i + 1,
          reason: `从第 ${i + 1} 行开始的代码块有重复`,
          priority: 'high',
          effort: 'medium'
        });
        i += minBlockLength - 1; // 跳过已检查的行
      }
    }

    return opportunities;
  }

  /**
   * 检测复杂条件
   */
  detectComplexConditional(content, filePath) {
    const opportunities = [];
    const lines = content.split('\n');

    let nestingLevel = 0;
    let maxNesting = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (/\bif\s*\(/.test(line)) {
        nestingLevel++;
        maxNesting = Math.max(maxNesting, nestingLevel);
      }

      if (/^\s*}\s*$/.test(line)) {
        nestingLevel--;
      }

      if (nestingLevel > 3) {
        opportunities.push({
          type: 'simplifyConditional',
          file: filePath,
          line: i + 1,
          reason: `嵌套层级过深（${nestingLevel} 层），建议使用卫语句`,
          priority: 'medium',
          effort: 'low'
        });
      }
    }

    return opportunities;
  }

  /**
   * 应用重构
   */
  async applyRefactor(opportunity, options) {
    const { type, file, ...details } = opportunity;

    // 创建备份
    const backup = await this.createBackup(file, options);

    try {
      let changes;

      switch (type) {
        case 'extractFunction':
          changes = await this.refactorExtractFunction(opportunity, options);
          break;
        case 'extractVariable':
          changes = await this.refactorExtractVariable(opportunity, options);
          break;
        case 'renameSymbol':
          changes = await this.refactorRename(opportunity, options);
          break;
        case 'introduceParameterObject':
          changes = await this.refactorParameterObject(opportunity, options);
          break;
        case 'consolidateDuplicate':
          changes = await this.refactorConsolidate(opportunity, options);
          break;
        case 'simplifyConditional':
          changes = await this.refactorSimplifyConditional(opportunity, options);
          break;
        default:
          changes = { warning: `未实现的重构类型: ${type}` };
      }

      return {
        file,
        type,
        success: true,
        changes,
        backup
      };

    } catch (error) {
      return {
        file,
        type,
        success: false,
        error: error.message,
        backup
      };
    }
  }

  /**
   * 具体重构方法
   */
  async refactorExtractFunction(opportunity, options) {
    // 提取函数的具体实现
    return {
      description: `将 ${opportunity.functionName} 中的代码提取为独立函数`,
      steps: [
        `1. 识别可提取的逻辑块`,
        `2. 创建新函数，将代码移入`,
        `3. 替换原代码为函数调用`,
        `4. 编写测试验证行为不变`
      ]
    };
  }

  async refactorExtractVariable(opportunity, options) {
    return {
      description: `提取复杂表达式为变量`,
      steps: [
        `1. 识别复杂表达式`,
        `2. 创建有意义的变量名`,
        `3. 替换表达式为变量引用`
      ]
    };
  }

  async refactorRename(opportunity, options) {
    return {
      oldName: opportunity.symbol,
      newName: opportunity.suggestion,
      description: `重命名 ${opportunity.symbol} 为 ${opportunity.suggestion}`
    };
  }

  async refactorParameterObject(opportunity, options) {
    return {
      parameters: opportunity.parameters,
      objectName: opportunity.suggestion,
      description: `将 ${opportunity.parameters.length} 个参数组合成对象`
    };
  }

  async refactorConsolidate(opportunity, options) {
    return {
      description: `合并从第 ${opportunity.startLine} 行开始的重复代码`,
      steps: [
        `1. 提取重复代码为函数`,
        `2. 替换所有重复处为函数调用`
      ]
    };
  }

  async refactorSimplifyConditional(opportunity, options) {
    return {
      description: `简化第 ${opportunity.line} 行的条件嵌套`,
      steps: [
        `1. 使用卫语句提前返回`,
        `2. 提取复杂条件为独立函数`
      ]
    };
  }

  /**
   * 辅助方法
   */
  countOccurrences(content, substring) {
    const regex = new RegExp(this.escapeRegex(substring), 'g');
    return (content.match(regex) || []).length;
  }

  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  suggestBetterName(singleLetter) {
    const suggestions = {
      'a': 'array',
      'b': 'buffer',
      'c': 'count',
      'd': 'data',
      'e': 'element',
      'f': 'flag',
      'n': 'number',
      'o': 'object',
      'p': 'pointer',
      'r': 'result',
      's': 'string',
      't': 'temp',
      'v': 'value'
    };
    return suggestions[singleLetter] || 'newName';
  }

  expandAbbreviation(abbr) {
    const expansions = {
      'cnt': 'count',
      'conf': 'config',
      'msg': 'message',
      'req': 'request',
      'res': 'response',
      'err': 'error',
      'tmp': 'temporary',
      'ctx': 'context'
    };
    return expansions[abbr] || abbr;
  }

  suggestParameterObjectName(funcDef) {
    const match = funcDef.match(/(?:function|(?:const|let|var)\s+)(\w+)/);
    const funcName = match ? match[1] : 'function';
    return `${funcName}Options`;
  }

  filterByScope(opportunities, scope) {
    if (!scope || scope === 'all') {
      return opportunities;
    }
    return opportunities.filter(op => op.type === scope);
  }

  prioritizeOpportunities(opportunities) {
    const priorityOrder = { 'high': 0, 'medium': 1, 'low': 2 };
    return opportunities.sort((a, b) => {
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return a.effort === 'low' ? -1 : 1;
    });
  }

  async createBackup(filePath, options) {
    return {
      file: filePath,
      timestamp: new Date().toISOString(),
      location: `${filePath}.backup`
    };
  }

  generateSummary(results) {
    const byType = {};
    const byPriority = { high: 0, medium: 0, low: 0 };

    for (const result of results) {
      if (result.success) {
        byType[result.type] = (byType[result.type] || 0) + 1;
        // byPriority[...]
      }
    }

    return {
      total: results.length,
      successful: results.filter(r => r.success).length,
      byType,
      byPriority
    };
  }

  generateRollbackPlan(results) {
    return results.filter(r => r.success).map(r => ({
      file: r.file,
      backup: r.backup,
      command: `cp ${r.backup.location} ${r.file}`
    }));
  }
}

module.exports = new RefactorEngineer();

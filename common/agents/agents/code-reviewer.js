/**
 * Code Reviewer - 代码审查Agent
 * 严格代码审查，给出可执行的 review checklist
 */

class CodeReviewer {
  constructor() {
    this.reviewCategories = {
      logic: {
        name: '逻辑正确性',
        checks: ['边界条件', '异常处理', '并发问题', '空值处理', '类型安全']
      },
      maintainability: {
        name: '可维护性',
        checks: ['命名清晰', '代码重复', '函数长度', '复杂度', '注释质量']
      },
      performance: {
        name: '性能',
        checks: ['热路径优化', '不必要的IO', '算法复杂度', '内存泄漏', '缓存使用']
      },
      security: {
        name: '安全',
        checks: ['注入攻击', '鉴权校验', '敏感信息', '加密存储', '输入验证']
      }
    };
  }

  /**
   * 执行代码审查
   */
  async execute(input, options) {
    const { files, changedCode, context } = input;

    const reviews = [];

    // 审查每个变更
    for (const change of changedCode) {
      const review = await this.reviewChange(change, options);
      reviews.push(review);
    }

    // 生成整体评估
    const overall = this.generateOverallAssessment(reviews);

    // 生成 review checklist
    const checklist = this.generateChecklist(reviews);

    return {
      reviews,
      overall,
      checklist,
      summary: this.generateSummary(reviews)
    };
  }

  /**
   * 审查单个代码变更
   */
  async reviewChange(change, options) {
    const { filePath, type, code, diff } = change;

    const issues = [];
    const suggestions = [];
    const styleNotes = [];

    // 逻辑正确性检查
    const logicIssues = this.checkLogicCorrectness(change);
    issues.push(...logicIssues);

    // 可维护性检查
    const maintainabilitySuggestions = this.checkMaintainability(change);
    suggestions.push(...maintainabilitySuggestions);

    // 性能检查
    const performanceSuggestions = this.checkPerformance(change);
    suggestions.push(...performanceSuggestions);

    // 安全检查
    const securityIssues = this.checkSecurity(change);
    issues.push(...securityIssues);

    // 代码风格检查
    const styleIssues = this.checkStyle(change);
    styleNotes.push(...styleIssues);

    return {
      file: filePath,
      type: change.type,
      issues: issues.map(i => ({ ...i, level: 'must-fix' })),
      suggestions: suggestions.map(s => ({ ...s, level: 'should-fix' })),
      styleNotes: styleNotes.map(s => ({ ...s, level: 'nice-to-have' })),
      summary: this.generateChangeSummary(issues, suggestions, styleNotes)
    };
  }

  /**
   * 检查逻辑正确性
   */
  checkLogicCorrectness(change) {
    const issues = [];
    const { code, functionName, className } = change;

    // 检查边界条件
    if (this.hasLoopWithoutBoundsCheck(code)) {
      issues.push({
        category: 'logic',
        check: '边界条件',
        message: '循环缺少边界条件检查',
        line: this.findLineNumber(code, /for\s*\(/),
        suggestion: '添加循环边界检查，防止无限循环或数组越界'
      });
    }

    // 检查异常处理
    if (this.hasUnhandledException(code)) {
      issues.push({
        category: 'logic',
        check: '异常处理',
        message: '存在未处理的异常',
        line: this.findLineNumber(code, /throw|reject|\bcatch\b/),
        suggestion: '为可能抛出异常的操作添加 try-catch 或错误处理'
      });
    }

    // 检查并发问题
    if (this.hasRaceCondition(code)) {
      issues.push({
        category: 'logic',
        check: '并发问题',
        message: '可能存在竞态条件',
        line: this.findLineNumber(code, /async|await|Promise/),
        suggestion: '使用适当的同步机制（锁、队列等）处理并发访问'
      });
    }

    // 检查空值处理
    if (this.hasNullCheckMissing(code)) {
      issues.push({
        category: 'logic',
        check: '空值处理',
        message: '缺少空值检查',
        line: this.findLineNumber(code, /\.\w+\[/),
        suggestion: '在使用对象属性或数组元素前检查 null/undefined'
      });
    }

    return issues;
  }

  /**
   * 检查可维护性
   */
  checkMaintainability(change) {
    const suggestions = [];
    const { code, functionName } = change;

    // 检查命名
    if (this.hasPoorNaming(code)) {
      suggestions.push({
        category: 'maintainability',
        check: '命名清晰',
        message: '变量或函数命名不够清晰',
        suggestion: '使用描述性的名称，避免缩写和单字母变量（除循环变量）'
      });
    }

    // 检查代码重复
    if (this.hasCodeDuplication(code)) {
      suggestions.push({
        category: 'maintainability',
        check: '代码重复',
        message: '存在重复代码',
        suggestion: '将重复逻辑提取为独立函数'
      });
    }

    // 检查函数长度
    if (this.isFunctionTooLong(code)) {
      suggestions.push({
        category: 'maintainability',
        check: '函数长度',
        message: `函数过长（${this.countLines(code)} 行）`,
        suggestion: '将长函数拆分为多个小函数，每个函数只做一件事'
      });
    }

    // 检查复杂度
    if (this.isHighComplexity(code)) {
      suggestions.push({
        category: 'maintainability',
        check: '复杂度',
        message: '圈复杂度过高',
        suggestion: '简化嵌套逻辑，使用早返回、卫语句等技巧'
      });
    }

    return suggestions;
  }

  /**
   * 检查性能问题
   */
  checkPerformance(change) {
    const suggestions = [];
    const { code } = change;

    // 检查热路径
    if (this.hasInefficientLoop(code)) {
      suggestions.push({
        category: 'performance',
        check: '热路径优化',
        message: '循环中存在可以优化的操作',
        suggestion: '将循环不变的计算移到循环外，考虑使用更高效的数据结构'
      });
    }

    // 检查不必要的IO
    if (this.hasUnnecessaryIO(code)) {
      suggestions.push({
        category: 'performance',
        check: '不必要的IO',
        message: '存在重复或不必要的IO操作',
        suggestion: '批量处理IO操作，或使用缓存减少重复IO'
      });
    }

    // 检查算法复杂度
    const complexity = this.analyzeComplexity(code);
    if (complexity > 2) {
      suggestions.push({
        category: 'performance',
        check: '算法复杂度',
        message: `嵌套层级过深（O(n^${complexity})）`,
        suggestion: '考虑使用更高效的算法或数据结构'
      });
    }

    // 检查内存泄漏
    if (this.hasMemoryLeak(code)) {
      suggestions.push({
        category: 'performance',
        check: '内存泄漏',
        message: '可能存在内存泄漏',
        suggestion: '确保正确清理资源（事件监听器、定时器、引用等）'
      });
    }

    return suggestions;
  }

  /**
   * 检查安全问题
   */
  checkSecurity(change) {
    const issues = [];
    const { code } = change;

    // SQL注入
    if (this.hasSQLInjection(code)) {
      issues.push({
        category: 'security',
        check: '注入攻击',
        message: '存在SQL注入风险',
        line: this.findLineNumber(code, /query|execute/),
        suggestion: '使用参数化查询或ORM，避免字符串拼接SQL'
      });
    }

    // XSS
    if (this.hasXSS(code)) {
      issues.push({
        category: 'security',
        check: '注入攻击',
        message: '存在XSS风险',
        line: this.findLineNumber(code, /innerHTML|document\.write/),
        suggestion: '对用户输入进行HTML转义，使用textContent而非innerHTML'
      });
    }

    // 鉴权校验
    if (this.hasMissingAuth(code)) {
      issues.push({
        category: 'security',
        check: '鉴权校验',
        message: '端点缺少身份验证',
        suggestion: '添加身份验证和授权检查'
      });
    }

    // 敏感信息
    if (this.hasSensitiveData(code)) {
      issues.push({
        category: 'security',
        check: '敏感信息',
        message: '可能泄露敏感信息',
        line: this.findLineNumber(code, /password|secret|token/),
        suggestion: '避免在日志或错误消息中输出敏感信息，使用环境变量存储密钥'
      });
    }

    return issues;
  }

  /**
   * 检查代码风格
   */
  checkStyle(change) {
    const notes = [];
    const { code } = change;

    // 检查缩进
    if (this.hasInconsistentIndentation(code)) {
      notes.push({
        category: 'style',
        check: '代码风格',
        message: '缩进不一致',
        suggestion: '使用统一的缩进风格（建议2或4空格）'
      });
    }

    // 检查尾随逗号
    if (this.hasInconsistentTrailingComma(code)) {
      notes.push({
        category: 'style',
        check: '代码风格',
        message: '尾随逗号使用不一致',
        suggestion: '统一使用或不使用尾随逗号'
      });
    }

    return notes;
  }

  /**
   * 辅助检查方法
   */
  hasLoopWithoutBoundsCheck(code) {
    return /for\s*\(\s*let\s+\w+\s*=\s*0\s*;/.test(code) &&
           !/if\s*\([^)]*>=.*length[^)]*\)/.test(code);
  }

  hasUnhandledException(code) {
    return (code.includes('await') || code.includes('.then(')) &&
           !code.includes('catch') &&
           !code.includes('try');
  }

  hasRaceCondition(code) {
    return code.includes('await') &&
           code.includes('Promise.all') === false &&
           code.includes('mutex') === false &&
           code.includes('lock') === false;
  }

  hasNullCheckMissing(code) {
    return /\.\w+\[/ && !code.includes('?.') && !code.includes('!= null');
  }

  hasPoorNaming(code) {
    return /\b[a-z]\b(?!\s*[,;)])/;
  }

  hasCodeDuplication(code) {
    const lines = code.split('\n');
    const seen = new Set();
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.length > 20 && seen.has(trimmed)) {
        return true;
      }
      seen.add(trimmed);
    }
    return false;
  }

  isFunctionTooLong(code) {
    return this.countLines(code) > 50;
  }

  isHighComplexity(code) {
    const nesting = code.match(/\{/g) || [];
    return nesting.length > 5;
  }

  hasInefficientLoop(code) {
    return /for\s*\(.*\)\s*{[\s\S]*?for\s*\(/.test(code);
  }

  hasUnnecessaryIO(code) {
    const readCount = (code.match(/readFile|readFileSync/g) || []).length;
    return readCount > 1;
  }

  analyzeComplexity(code) {
    let depth = 0;
    let maxDepth = 0;
    for (const char of code) {
      if (char === '{') depth++;
      if (char === '}') depth--;
      maxDepth = Math.max(maxDepth, depth);
    }
    return maxDepth;
  }

  hasMemoryLeak(code) {
    return (code.includes('addEventListener') || code.includes('setInterval')) &&
           !code.includes('removeEventListener') &&
           !code.includes('clearInterval');
  }

  hasSQLInjection(code) {
    return /query\s*\(\s*['"`][^'"`]*\+/i.test(code);
  }

  hasXSS(code) {
    return /innerHTML\s*=/.test(code);
  }

  hasMissingAuth(code) {
    return code.includes('router.') &&
           !code.includes('auth') &&
           !code.includes('require');
  }

  hasSensitiveData(code) {
    return /console\.log\([^)]*password|console\.log\([^)]*secret|console\.log\([^)]*token/i.test(code);
  }

  hasInconsistentIndentation(code) {
    const lines = code.split('\n');
    const indents = lines.map(l => l.match(/^\s*/)[0].length);
    const uniqueIndents = new Set(indents);
    return uniqueIndents.size > 3;
  }

  hasInconsistentTrailingComma(code) {
    const hasComma = /,\s*\]/.test(code) || /,\s*\}/.test(code);
    const hasNoComma = /\w\s*\]/.test(code) || /\w\s*\}/.test(code);
    return hasComma && hasNoComma;
  }

  findLineNumber(code, pattern) {
    const lines = code.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        return i + 1;
      }
    }
    return 1;
  }

  countLines(code) {
    return code.split('\n').length;
  }

  /**
   * 生成单个变更的摘要
   */
  generateChangeSummary(issues, suggestions, styleNotes) {
    return {
      mustFix: issues.length,
      shouldFix: suggestions.length,
      niceToHave: styleNotes.length,
      overall: issues.length === 0 ? 'LGTM' : '需要修改'
    };
  }

  /**
   * 生成整体评估
   */
  generateOverallAssessment(reviews) {
    const totalIssues = reviews.reduce((sum, r) => sum + r.issues.length, 0);
    const totalSuggestions = reviews.reduce((sum, r) => sum + r.suggestions.length, 0);

    let verdict;
    if (totalIssues === 0 && totalSuggestions === 0) {
      verdict = 'LGTM (Looks Good To Me)';
    } else if (totalIssues === 0) {
      verdict = 'LGTM with suggestions';
    } else if (totalIssues < 3) {
      verdict = '需要小幅度修改后可以合并';
    } else {
      verdict = '建议修改后再次审查';
    }

    return {
      verdict,
      totalIssues,
      totalSuggestions,
      confidence: totalIssues === 0 ? 'high' : 'medium'
    };
  }

  /**
   * 生成审查清单
   */
  generateChecklist(reviews) {
    const checklist = {
      mustFix: [],
      suggested: [],
      optional: []
    };

    for (const review of reviews) {
      for (const issue of review.issues) {
        checklist.mustFix.push({
          file: review.file,
          line: issue.line,
          check: issue.check,
          message: issue.message,
          suggestion: issue.suggestion
        });
      }

      for (const suggestion of review.suggestions) {
        checklist.suggested.push({
          file: review.file,
          check: suggestion.check,
          message: suggestion.message,
          suggestion: suggestion.suggestion
        });
      }

      for (const note of review.styleNotes) {
        checklist.optional.push({
          file: review.file,
          check: note.check,
          message: note.message,
          suggestion: note.suggestion
        });
      }
    }

    return checklist;
  }

  /**
   * 生成摘要
   */
  generateSummary(reviews) {
    return {
      totalFiles: reviews.length,
      totalMustFix: reviews.reduce((sum, r) => sum + r.issues.length, 0),
      totalShouldFix: reviews.reduce((sum, r) => sum + r.suggestions.length, 0),
      totalOptional: reviews.reduce((sum, r) => sum + r.styleNotes.length, 0)
    };
  }
}

module.exports = new CodeReviewer();

/**
 * Security Auditor - 安全审计Agent
 * 目标：找出高风险漏洞与可利用路径，并给出可执行修复建议
 */

class SecurityAuditor {
  constructor() {
    this.vulnerabilityTypes = {
      sqlInjection: {
        severity: 'Critical',
        patterns: [
          /SELECT.*FROM.*WHERE.*\$\{.*\}/i,
          /SELECT.*FROM.*WHERE.*\+/i,
          /query\([^)]*\+[^)]*\)/i,
          /execute\([^)]*\+[^)]*\)/i
        ],
        description: 'SQL注入漏洞：攻击者可以通过输入恶意SQL语句来操作数据库'
      },
      xss: {
        severity: 'High',
        patterns: [
          /innerHTML\s*=\s*[^;]+/,
          /document\.write\([^)]*\)/,
          /dangerouslySetInnerHTML/
        ],
        description: 'XSS漏洞：未经过滤的用户输入直接渲染到页面'
      },
      commandInjection: {
        severity: 'Critical',
        patterns: [
          /exec\([^)]*\+[^)]*\)/i,
          /spawn\([^)]*\+[^)]*\)/i,
          /child_process\.(exec|spawn)\([^)]*\+[^)]*\)/i
        ],
        description: '命令注入：用户输入可以执行系统命令'
      },
      hardcodedSecrets: {
        severity: 'High',
        patterns: [
          /password\s*[:=]\s*['"][^'"]{8,}['"]/i,
          /api[_-]?key\s*[:=]\s*['"][^'"]{20,}['"]/i,
          /secret\s*[:=]\s*['"][^'"]{16,}['"]/i,
          /token\s*[:=]\s*['"][^'"]{32,}['"]/i
        ],
        description: '硬编码的敏感信息：密钥、密码等直接写在代码中'
      },
      pathTraversal: {
        severity: 'High',
        patterns: [
          /fs\.readFile\([^)]*\+[^)]*\)/i,
          /fs\.writeFile\([^)]*\+[^)]*\)/i,
          /path\.join\([^,]*\+[^)]*\)/i
        ],
        description: '路径遍历：攻击者可以访问预期外的文件系统路径'
      },
      insecureDeserialization: {
        severity: 'Critical',
        patterns: [
          /JSON\.parse\([^)]*req\.body/i,
          /eval\([^)]*\)/i,
          /\.deserialize\(/
        ],
        description: '不安全的反序列化：可能导致远程代码执行'
      },
      weakCrypto: {
        severity: 'Medium',
        patterns: [
          /md5\(/i,
          /sha1\(/i,
          /createCipher\(/i,
          /rc4/i
        ],
        description: '弱加密算法：使用了已知不安全的加密算法'
      },
      authBypass: {
        severity: 'Critical',
        patterns: [
          /@RequestMapping.*public\s*function/i,
          /app\.get\([^)]*function\s*\([^)]*req[^)]*\)\s*{/,
          /router\.get\([^)]*\)\s*\(\s*req\s*,\s*res\s*\)/
        ],
        description: '认证绕过：敏感端点缺少身份验证'
      }
    };
  }

  /**
   * 执行安全审计
   */
  async execute(input, options) {
    const { files, context } = input;
    const findings = [];

    // 扫描每个文件
    for (const filePath of files) {
      const fileFindings = await this.auditFile(filePath, options);
      findings.push(...fileFindings);
    }

    // 按严重程度排序
    const severityOrder = ['Critical', 'High', 'Medium'];
    findings.sort((a, b) => {
      return severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity);
    });

    return {
      findings,
      summary: this.generateSummary(findings),
      recommendations: this.generateRecommendations(findings)
    };
  }

  /**
   * 审计单个文件
   */
  async auditFile(filePath, options) {
    const findings = [];

    try {
      // 这里需要使用实际的Read工具读取文件
      // const content = await options.tools.Read(filePath);
      const content = options.context?.fileContents?.[filePath] || '';

      for (const [vulnType, vulnConfig] of Object.entries(this.vulnerabilityTypes)) {
        const matches = this.scanForVulnerability(content, vulnConfig.patterns);

        for (const match of matches) {
          findings.push({
            file: filePath,
            line: match.line,
            severity: vulnConfig.severity,
            type: vulnType,
            description: vulnConfig.description,
            code: match.code,
            exploit: this.generateExploitPath(vulnType, match),
            fix: this.generateFix(vulnType, match)
          });
        }
      }
    } catch (error) {
      findings.push({
        file: filePath,
        severity: 'Medium',
        type: 'scan-error',
        description: `无法扫描文件: ${error.message}`
      });
    }

    return findings;
  }

  /**
   * 扫描特定类型的漏洞
   */
  scanForVulnerability(content, patterns) {
    const matches = [];
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      patterns.forEach(pattern => {
        if (pattern.test(line)) {
          matches.push({
            line: index + 1,
            code: line.trim(),
            pattern: pattern.toString()
          });
        }
      });
    });

    return matches;
  }

  /**
   * 生成攻击路径描述
   */
  generateExploitPath(vulnType, match) {
    const exploits = {
      sqlInjection: '攻击者可以在输入字段中输入 "1\' OR \'1\'=\'1" 来绕过认证',
      xss: '攻击者可以输入 "<script>alert(document.cookie)</script>" 来窃取Cookie',
      commandInjection: '攻击者可以输入 "; cat /etc/passwd" 来读取系统文件',
      hardcodedSecrets: '攻击者可以通过反编译或代码泄露获取密钥',
      pathTraversal: '攻击者可以输入 "../../../etc/passwd" 来读取任意文件',
      insecureDeserialization: '攻击者可以构造恶意对象导致远程代码执行',
      weakCrypto: '攻击者可以使用彩虹表或暴力破解破解哈希',
      authBypass: '攻击者可以直接访问URL获取敏感数据'
    };

    return exploits[vulnType] || '具体攻击路径需要进一步分析';
  }

  /**
   * 生成修复建议
   */
  generateFix(vulnType, match) {
    const fixes = {
      sqlInjection: '使用参数化查询（prepared statements）或ORM',
      xss: '对用户输入进行HTML转义，使用textContent而非innerHTML',
      commandInjection: '避免将用户输入直接传递给命令行，使用白名单验证',
      hardcodedSecrets: '将密钥移到环境变量或密钥管理服务',
      pathTraversal: '验证并规范化路径，限制在指定目录内',
      insecureDeserialization: '使用安全的序列化格式，验证输入数据',
      weakCrypto: '使用强加密算法：SHA-256、bcrypt、AES-256',
      authBypass: '添加身份验证中间件，检查用户权限'
    };

    return fixes[vulnType] || '参考安全最佳实践进行修复';
  }

  /**
   * 生成审计摘要
   */
  generateSummary(findings) {
    const summary = {
      total: findings.length,
      critical: findings.filter(f => f.severity === 'Critical').length,
      high: findings.filter(f => f.severity === 'High').length,
      medium: findings.filter(f => f.severity === 'Medium').length
    };

    return summary;
  }

  /**
   * 生成整体建议
   */
  generateRecommendations(findings) {
    const recommendations = [];

    if (findings.some(f => f.severity === 'Critical')) {
      recommendations.push({
        priority: 1,
        action: '立即修复所有Critical级别的漏洞',
        reason: '这些漏洞可能被直接利用造成严重后果'
      });
    }

    if (findings.some(f => f.type === 'sqlInjection')) {
      recommendations.push({
        priority: 2,
        action: '实施安全编码培训，重点讲解SQL注入防护',
        reason: 'SQL注入是最常见的Web应用漏洞之一'
      });
    }

    if (findings.some(f => f.type === 'hardcodedSecrets')) {
      recommendations.push({
        priority: 3,
        action: '集成密钥管理服务，实施密钥轮换策略',
        reason: '硬编码的密钥可能已泄露，需要立即更换'
      });
    }

    return recommendations;
  }
}

module.exports = new SecurityAuditor();

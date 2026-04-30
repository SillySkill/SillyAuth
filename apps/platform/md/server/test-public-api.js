/**
 * 公共 API 测试脚本
 *
 * 用于测试首页集成所需的公共 API 端点
 *
 * 使用方法：
 *   node test-public-api.js
 */

const http = require('http');

// 配置
const CONFIG = {
  API_BASE: process.env.API_BASE || 'http://localhost:3001/api/v1/public',
  TIMEOUT: 10000,
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('\n' + '='.repeat(60));
  log(title, 'blue');
  console.log('='.repeat(60));
}

function logTest(name, passed, details = '') {
  const icon = passed ? '✓' : '✗';
  const color = passed ? 'green' : 'red';
  log(`${icon} ${name}`, color);
  if (details) {
    console.log(`  ${details}`);
  }
}

// HTTP 请求函数
function fetchAPI(endpoint) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint, CONFIG.API_BASE);

    const options = {
      method: 'GET',
      timeout: CONFIG.TIMEOUT,
    };

    const req = http.request(url, options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({
            status: res.statusCode,
            data: json,
          });
        } catch (error) {
          resolve({
            status: res.statusCode,
            data: data,
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('请求超时'));
    });

    req.end();
  });
}

// 格式化 JSON
function formatJSON(obj) {
  return JSON.stringify(obj, null, 2);
}

// 测试函数集合
const tests = {
  /**
   * 测试 1: 健康检查
   */
  async testHealth() {
    logSection('测试 1: 健康检查');

    try {
      const response = await fetchAPI('/health');
      const passed = response.status === 200 && response.data.success === true;

      logTest('健康检查端点', passed, `状态码: ${response.status}`);
      if (passed) {
        log(`响应: ${formatJSON(response.data)}`, 'green');
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('健康检查端点', false, error.message);
      return false;
    }
  },

  /**
   * 测试 2: 市场统计数据
   */
  async testMarketStats() {
    logSection('测试 2: 市场统计数据');

    try {
      const response = await fetchAPI('/market/stats');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        response.data.data !== undefined;

      logTest('市场统计 API', passed, `状态码: ${response.status}`);

      if (passed) {
        const stats = response.data.data;
        log('统计数据:', 'green');
        log(`  - Skills 总数: ${stats.total_skills || 0}`, 'green');
        log(`  - 供应商总数: ${stats.total_vendors || 0}`, 'green');
        log(`  - 团队总数: ${stats.total_teams || 0}`, 'green');
        log(`  - 用户总数: ${stats.total_users || 0}`, 'green');
        log(`  - 总下载量: ${stats.total_downloads || 0}`, 'green');
        log(`  - AI 准确率: ${stats.ai_accuracy || 'N/A'}`, 'green');
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('市场统计 API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 3: 免费 Skills 列表
   */
  async testFreeSkills() {
    logSection('测试 3: 免费 Skills 列表');

    try {
      const response = await fetchAPI('/skills?type=free&limit=5');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        Array.isArray(response.data.data);

      logTest('免费 Skills API', passed, `状态码: ${response.status}`);

      if (passed) {
        const skills = response.data.data;
        log(`返回 ${skills.length} 个免费 Skills:`, 'green');

        skills.slice(0, 2).forEach((skill, index) => {
          log(`\n  Skill #${index + 1}:`, 'green');
          log(`    - 名称: ${skill.name}`, 'green');
          log(`    - 类型: ${skill.type}`, 'green');
          log(`    - 分类: ${skill.category}`, 'green');
          log(`    - 下载量: ${skill.download_count || 0}`, 'green');
          log(`    - 评分: ${skill.rating_avg || 'N/A'}`, 'green');
        });
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('免费 Skills API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 4: 商用 Skills 列表
   */
  async testCommercialSkills() {
    logSection('测试 4: 商用 Skills 列表');

    try {
      const response = await fetchAPI('/skills?type=commercial&limit=5');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        Array.isArray(response.data.data);

      logTest('商用 Skills API', passed, `状态码: ${response.status}`);

      if (passed) {
        const skills = response.data.data;
        log(`返回 ${skills.length} 个商用 Skills:`, 'green');

        skills.slice(0, 2).forEach((skill, index) => {
          log(`\n  Skill #${index + 1}:`, 'green');
          log(`    - 名称: ${skill.name}`, 'green');
          log(`    - 类型: ${skill.type}`, 'green');
          log(`    - 价格: ¥${skill.price || 0}`, 'green');
          log(`    - 下载量: ${skill.download_count || 0}`, 'green');
        });
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('商用 Skills API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 5: 精选 Skills
   */
  async testFeaturedSkills() {
    logSection('测试 5: 精选 Skills');

    try {
      const response = await fetchAPI('/skills?is_featured=true&limit=5');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        Array.isArray(response.data.data);

      logTest('精选 Skills API', passed, `状态码: ${response.status}`);

      if (passed) {
        const skills = response.data.data;
        log(`返回 ${skills.length} 个精选 Skills`, 'green');
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('精选 Skills API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 6: 供应商列表
   */
  async testVendors() {
    logSection('测试 6: 供应商列表');

    try {
      const response = await fetchAPI('/vendors?limit=5');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        Array.isArray(response.data.data);

      logTest('供应商列表 API', passed, `状态码: ${response.status}`);

      if (passed) {
        const vendors = response.data.data;
        log(`返回 ${vendors.length} 个供应商:`, 'green');

        vendors.slice(0, 2).forEach((vendor, index) => {
          log(`\n  供应商 #${index + 1}:`, 'green');
          log(`    - 用户名: ${vendor.username}`, 'green');
          log(`    - Skills 数: ${vendor.total_skills || 0}`, 'green');
          log(`    - 总下载: ${vendor.total_downloads || 0}`, 'green');
          log(`    - 评分: ${vendor.rating_avg || 'N/A'}`, 'green');
          log(`    - 认证: ${vendor.is_verified ? '是' : '否'}`, 'green');
        });
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('供应商列表 API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 7: Skills 分类
   */
  async testCategories() {
    logSection('测试 7: Skills 分类');

    try {
      const response = await fetchAPI('/skills/categories');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        Array.isArray(response.data.data);

      logTest('分类列表 API', passed, `状态码: ${response.status}`);

      if (passed) {
        const categories = response.data.data;
        log(`返回 ${categories.length} 个分类:`, 'green');

        categories.forEach((cat) => {
          log(
            `  - ${cat.label || cat.value}: ${cat.count} 个 Skills`,
            'green'
          );
        });
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('分类列表 API', false, error.message);
      return false;
    }
  },

  /**
   * 测试 8: 分页功能
   */
  async testPagination() {
    logSection('测试 8: 分页功能');

    try {
      const response = await fetchAPI('/skills?page=1&limit=2');
      const passed =
        response.status === 200 &&
        response.data.success === true &&
        response.data.meta !== undefined;

      logTest('分页功能', passed, `状态码: ${response.status}`);

      if (passed) {
        const meta = response.data.meta;
        log('分页信息:', 'green');
        log(`  - 当前页: ${meta.page}`, 'green');
        log(`  - 每页数量: ${meta.limit}`, 'green');
        log(`  - 总记录数: ${meta.total}`, 'green');
        log(`  - 总页数: ${meta.totalPages}`, 'green');
      } else {
        log(`响应: ${formatJSON(response.data)}`, 'red');
      }

      return passed;
    } catch (error) {
      logTest('分页功能', false, error.message);
      return false;
    }
  },
};

// 主测试函数
async function runTests() {
  log('='.repeat(60), 'blue');
  log('公共 API 测试', 'blue');
  log('='.repeat(60));
  log(`测试地址: ${CONFIG.API_BASE}`, 'yellow');
  log(`开始时间: ${new Date().toLocaleString('zh-CN')}`, 'yellow');

  const results = [];

  // 运行所有测试
  results.push(await tests.testHealth());
  results.push(await tests.testMarketStats());
  results.push(await tests.testFreeSkills());
  results.push(await tests.testCommercialSkills());
  results.push(await tests.testFeaturedSkills());
  results.push(await tests.testVendors());
  results.push(await tests.testCategories());
  results.push(await tests.testPagination());

  // 汇总结果
  logSection('测试结果汇总');

  const passed = results.filter((r) => r).length;
  const failed = results.length - passed;

  log(`总测试数: ${results.length}`, 'blue');
  log(`通过: ${passed}`, 'green');
  log(`失败: ${failed}`, failed > 0 ? 'red' : 'green');
  log(`成功率: ${((passed / results.length) * 100).toFixed(1)}%`, 'blue');

  log('\n结束时间: ' + new Date().toLocaleString('zh-CN'), 'yellow');
  log('='.repeat(60), 'blue');

  // 返回退出码
  process.exit(failed > 0 ? 1 : 0);
}

// 运行测试
runTests().catch((error) => {
  log(`\n测试运行失败: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});

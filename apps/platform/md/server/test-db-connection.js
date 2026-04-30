const { Client } = require('pg');

// 数据库连接配置（云端服务器）
const config = {
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
  connectionTimeoutMillis: 10000,
};

async function testConnection() {
  const client = new Client(config);

  console.log('='.repeat(50));
  console.log('开始测试 PostgreSQL 数据库连接...');
  console.log('='.repeat(50));
  console.log(`主机: ${config.host}:${config.port}`);
  console.log(`数据库: ${config.database}`);
  console.log(`用户: ${config.user}`);
  console.log('='.repeat(50));

  try {
    // 尝试连接
    console.log('正在连接数据库...');
    await client.connect();
    console.log('✓ 数据库连接成功!');

    // 测试查询
    console.log('\n执行测试查询...');
    const result = await client.query('SELECT version();');
    console.log('✓ 查询成功!');
    console.log(`\nPostgreSQL 版本: ${result.rows[0].version}`);

    // 检查表数量
    const tables = await client.query(`
      SELECT count(*) as count
      FROM information_schema.tables
      WHERE table_schema = 'public'
    `);
    console.log(`\n数据库表数量: ${tables.rows[0].count}`);

    console.log('\n' + '='.repeat(50));
    console.log('✓ 数据库连接测试完成 - 所有测试通过!');
    console.log('='.repeat(50));

    await client.end();
    process.exit(0);
  } catch (error) {
    console.error('\n✗ 数据库连接失败!');
    console.error(`错误信息: ${error.message}`);
    console.error('\n可能的原因:');
    console.error('1. 服务器防火墙未开放 5432 端口');
    console.error('2. 数据库容器未启动');
    console.error('3. 网络连接问题');
    console.error('4. 数据库配置不正确');
    console.error('\n解决方法:');
    console.error('- SSH 登录服务器检查: docker ps | grep sillymd');
    console.error('- 检查容器日志: docker logs sillymd-postgres');
    console.error('- 检查端口监听: netstat -tlnp | grep 5432');
    console.error('- 测试连接: docker exec sillymd-postgres pg_isready -U sillyAdmin');
    console.error('='.repeat(50));

    await client.end().catch(() => {});
    process.exit(1);
  }
}

testConnection();

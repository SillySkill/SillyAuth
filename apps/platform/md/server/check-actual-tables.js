const { Client } = require('pg');

const config = {
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
  connectionTimeoutMillis: 10000,
};

async function checkActualTables() {
  const client = new Client(config);

  try {
    await client.connect();
    console.log('✓ 数据库连接成功!\n');

    // 检查 skills 表结构
    console.log('Skills 表结构:');
    console.log('='.repeat(60));
    const skillsColumns = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns
      WHERE table_name = 'skills'
      ORDER BY ordinal_position;
    `);
    skillsColumns.rows.forEach(col => {
      console.log(`  - ${col.column_name}: ${col.data_type}${col.is_nullable === 'NO' ? ' NOT NULL' : ''}`);
    });

    // 检查是否有数据
    const skillsCount = await client.query(`SELECT COUNT(*) as count FROM skills`);
    console.log(`\n总记录数: ${skillsCount.rows[0].count}\n`);

    // 获取几条示例数据
    const sampleSkills = await client.query(`
      SELECT * FROM skills
      LIMIT 3
    `);
    console.log('示例数据:');
    console.log('='.repeat(60));
    console.log(JSON.stringify(sampleSkills.rows, null, 2));

    await client.end();
    process.exit(0);
  } catch (error) {
    console.error('错误:', error.message);
    await client.end().catch(() => {});
    process.exit(1);
  }
}

checkActualTables();

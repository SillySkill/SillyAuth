const { Client } = require('pg');

const config = {
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
  connectionTimeoutMillis: 10000,
};

async function checkTables() {
  const client = new Client(config);

  try {
    await client.connect();
    console.log('✓ 数据库连接成功!\n');

    // 获取所有表名
    const tablesResult = await client.query(`
      SELECT tablename
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY tablename;
    `);

    console.log('数据库表列表:');
    console.log('='.repeat(60));
    tablesResult.rows.forEach((row, index) => {
      console.log(`${index + 1}. ${row.tablename}`);
    });

    // 检查首页所需的关键表
    const requiredTables = [
      'content',
      'navigation',
      'carousel',
      'skill',
      'vendor',
      'user',
      'ActivityLog'
    ];

    console.log('\n\n首页集成所需表检查:');
    console.log('='.repeat(60));

    const existingTables = tablesResult.rows.map(row => row.tablename);

    requiredTables.forEach(table => {
      const exists = existingTables.includes(table);
      console.log(`${exists ? '✓' : '✗'} ${table} ${exists ? '' : '(缺失)'}`);
    });

    // 检查关键表的列结构
    console.log('\n\n关键表结构:');
    console.log('='.repeat(60));

    const tablesToCheck = ['skill', 'vendor', 'carousel', 'content'];

    for (const tableName of tablesToCheck) {
      if (existingTables.includes(tableName)) {
        console.log(`\n表: ${tableName}`);
        console.log('-'.repeat(60));

        const columnsResult = await client.query(`
          SELECT column_name, data_type, is_nullable, column_default
          FROM information_schema.columns
          WHERE table_name = '${tableName}'
          ORDER BY ordinal_position;
        `);

        columnsResult.rows.forEach(col => {
          console.log(`  - ${col.column_name}: ${col.data_type}${col.is_nullable === 'NO' ? ' NOT NULL' : ''}`);
        });
      }
    }

    // 检查是否有示例数据
    console.log('\n\n示例数据统计:');
    console.log('='.repeat(60));

    const stats = [
      { table: 'skill', name: 'Skills' },
      { table: 'vendor', name: 'Vendors' },
      { table: 'carousel', name: 'Carousel Items' },
      { table: 'navigation', name: 'Navigation Items' }
    ];

    for (const stat of stats) {
      if (existingTables.includes(stat.table)) {
        const result = await client.query(`SELECT COUNT(*) as count FROM "${stat.table}"`);
        console.log(`${stat.name}: ${result.rows[0].count} 条记录`);
      }
    }

    await client.end();
    process.exit(0);
  } catch (error) {
    console.error('错误:', error.message);
    await client.end().catch(() => {});
    process.exit(1);
  }
}

checkTables();

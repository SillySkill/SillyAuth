const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const config = {
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
};

async function runMigration() {
  const client = new Client(config);

  try {
    await client.connect();
    console.log('✓ 数据库连接成功\n');

    // 读取迁移文件
    const migrationFile = path.join(__dirname, 'migrations', '003_add_tutorials_and_downloads.sql');
    const migrationSQL = fs.readFileSync(migrationFile, 'utf8');

    console.log('开始执行迁移 003: 添加教程和下载资源表...\n');

    // 直接执行整个SQL文件
    try {
      await client.query(migrationSQL);
      console.log('✓ 迁移执行成功！\n');
    } catch (err) {
      console.log('注意:', err.message);
      console.log('继续验证表结构...\n');
    }

    // 验证表是否创建成功
    console.log('验证表结构...');
    const tablesToCheck = ['tutorials', 'tutorial_chapters', 'downloads', 'download_versions', 'tutorial_progress', 'download_records'];

    for (const tableName of tablesToCheck) {
      const result = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables
          WHERE table_schema = 'public'
          AND table_name = '${tableName}'
        );
      `);

      const exists = result.rows[0].exists;
      console.log(`${exists ? '✓' : '✗'} ${tableName}`);

      if (exists) {
        // 获取记录数
        const countResult = await client.query(`SELECT COUNT(*) as count FROM ${tableName}`);
        console.log(`  记录数: ${countResult.rows[0].count}`);
      }
    }

    await client.end();
    process.exit(0);
  } catch (error) {
    console.error('\n错误:', error.message);
    await client.end().catch(() => {});
    process.exit(1);
  }
}

runMigration();

const { Client } = require('pg');

const config = {
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026',
};

(async () => {
  const client = new Client(config);
  try {
    await client.connect();

    const result = await client.query(`
      SELECT tablename
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY tablename;
    `);

    console.log('数据库中的所有表:');
    result.rows.forEach(row => {
      console.log('  -', row.tablename);
    });

    await client.end();
  } catch (err) {
    console.error('错误:', err.message);
    await client.end().catch(() => {});
    process.exit(1);
  }
})();

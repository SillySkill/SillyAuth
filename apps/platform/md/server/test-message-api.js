/**
 * 测试消息系统 API
 */

const pg = require('pg');
const { Pool } = pg;

const pool = new Pool({
  host: '47.96.133.238',
  port: 5432,
  database: 'sillymd',
  user: 'sillyAdmin',
  password: 'Jcoding2026'
});

async function testMessageAPI() {
  console.log('========================================');
  console.log('测试消息系统数据库结构');
  console.log('========================================\n');

  try {
    // 检查表是否存在
    console.log('1. 检查表结构...');
    const tables = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('conversations', 'conversation_participants', 'messages')
      ORDER BY table_name;
    `);

    console.log('找到的表:', tables.rows.map(r => r.table_name));

    // 检查枚举类型
    console.log('\n2. 检查枚举类型...');
    const enums = await pool.query(`
      SELECT typname, enumlabel
      FROM pg_enum
      JOIN pg_type ON pg_enum.enumtypid = pg_type.oid
      WHERE typname IN ('conversation_type', 'message_type', 'conversation_participant_role')
      ORDER BY typname, enumsortorder;
    `);

    const enumTypes = {};
    enums.rows.forEach(row => {
      if (!enumTypes[row.typname]) {
        enumTypes[row.typname] = [];
      }
      enumTypes[row.typname].push(row.enumlabel);
    });

    console.log('枚举类型:', enumTypes);

    // 创建测试数据
    console.log('\n3. 创建测试数据...');

    // 获取现有用户（包括种子用户用于测试）
    const users = await pool.query(`
      SELECT id, username
      FROM users
      WHERE is_active = TRUE
      ORDER BY id
      LIMIT 5
    `);

    if (users.rows.length < 2) {
      console.log('❌ 数据库中用户不足，无法创建测试对话');
      return;
    }

    console.log('找到用户:', users.rows.map(u => `${u.id}:${u.username}`).join(', '));

    // 创建测试对话
    const conversationResult = await pool.query(`
      INSERT INTO conversations (conversation_type, created_by, is_group, last_message_at)
      VALUES ('direct', $1, FALSE, CURRENT_TIMESTAMP)
      RETURNING id
    `, [users.rows[0].id]);

    const conversationId = conversationResult.rows[0].id;
    console.log(`✓ 创建对话 ID: ${conversationId}`);

    // 添加参与者
    await pool.query(`
      INSERT INTO conversation_participants (conversation_id, user_id, role, has_unread)
      VALUES ($1, $2, 'owner', FALSE),
             ($1, $3, 'member', TRUE)
    `, [conversationId, users.rows[0].id, users.rows[1].id]);

    console.log('✓ 添加参与者');

    // 发送测试消息
    const messages = [
      '你好！很高兴认识你',
      '你好，有什么我可以帮助的吗？',
      '想咨询一下关于项目的问题',
      '当然，请说'
    ];

    for (let i = 0; i < messages.length; i++) {
      const senderId = i % 2 === 0 ? users.rows[0].id : users.rows[1].id;

      await pool.query(`
        INSERT INTO messages (conversation_id, sender_id, content, message_type)
        VALUES ($1, $2, $3, 'text')
      `, [conversationId, senderId, messages[i]]);

      console.log(`✓ 发送消息 ${i + 1}: ${messages[i]}`);
    }

    // 更新对话最后消息时间
    await pool.query(`
      UPDATE conversations
      SET last_message_at = CURRENT_TIMESTAMP
      WHERE id = $1
    `, [conversationId]);

    // 查询验证
    console.log('\n4. 验证数据...');

    const conversationCheck = await pool.query(`
      SELECT
        c.id,
        c.conversation_type,
        c.last_message_at,
        (SELECT COUNT(*) FROM conversation_participants WHERE conversation_id = c.id) as participant_count,
        (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
      FROM conversations c
      WHERE c.id = $1
    `, [conversationId]);

    console.log('对话信息:', conversationCheck.rows[0]);

    const messagesCheck = await pool.query(`
      SELECT
        m.id,
        m.content,
        m.message_type,
        m.created_at,
        u.username as sender_username
      FROM messages m
      JOIN users u ON m.sender_id = u.id
      WHERE m.conversation_id = $1
      ORDER BY m.created_at ASC
    `, [conversationId]);

    console.log('\n消息列表:');
    messagesCheck.rows.forEach(msg => {
      console.log(`  [${msg.sender_username}] ${msg.content}`);
    });

    // 统计信息
    console.log('\n5. 数据库统计...');
    const stats = await pool.query(`
      SELECT
        (SELECT COUNT(*) FROM conversations WHERE is_active = TRUE) as total_conversations,
        (SELECT COUNT(*) FROM conversation_participants) as total_participants,
        (SELECT COUNT(*) FROM messages WHERE is_deleted = FALSE) as total_messages
    `);

    console.log('统计:', stats.rows[0]);

    console.log('\n========================================');
    console.log('✓ 测试完成！');
    console.log('========================================');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error(error.stack);
  } finally {
    await pool.end();
  }
}

testMessageAPI();

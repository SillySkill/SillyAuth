#!/bin/bash
# ============================================
# 种子数据导入脚本（服务器端）
# 版本: 1.0
# ============================================

set -e

DB_NAME="sillymd"
DB_USER="sillyAdmin"
SEEDS_DIR="/opt/sillymd/seeds"

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

error() {
    echo "[ERROR] $*" >&2
    exit 1
}

# 生成密码哈希（简单实现）
generate_hash() {
    local password="$1"
    echo -n "$password" | md5sum | cut -d' ' -f1
}

main() {
    log "开始导入种子数据..."

    # 检查种子数据文件
    if [ ! -f "$SEEDS_DIR/demo-data.json" ]; then
        error "种子数据文件不存在: $SEEDS_DIR/demo-data.json"
    fi

    log "读取种子数据..."
    USERS=$(jq -c '.users[]' "$SEEDS_DIR/demo-data.json")
    SKILLS=$(jq -c '.skills[]' "$SEEDS_DIR/demo-data.json" 2>/dev/null || echo "")

    # 统计
    USER_COUNT=$(echo "$USERS" | wc -l)
    SKILL_COUNT=$(echo "$SKILLS" | wc -l)

    log "发现 $USER_COUNT 个用户，$SKILL_COUNT 个 Skills"

    # 导入用户
    log "导入种子用户..."
    echo "$USERS" | while read -r user; do
        username=$(echo "$user" | jq -r '.username')
        display_name=$(echo "$user" | jq -r '.displayName // .username')
        bio=$(echo "$user" | jq -r '.bio // ""')
        avatar=$(echo "$user" | jq -r '.avatar // ""')
        role=$(echo "$user" | jq -r '.role // "user"')
        vendor_level=$(echo "$user" | jq -r '.vendorLevel // "normal"')

        # 生成默认密码：username + "123456"
        password_hash=$(generate_hash "${username}123456")

        docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
        INSERT INTO users (
            username, email, password_hash, role, vendor_level,
            avatar_url, bio, is_active, is_verified,
            preferred_language, theme_preference
        ) VALUES (
            '$username',
            '$username@seed.local',
            '$password_hash',
            '$role',
            '$vendor_level',
            '$avatar',
            '\$(echo "$bio" | sed "s/'\''/''/g")',
            true,
            true,
            'zh-CN',
            'tech-blue'
        ) ON CONFLICT (username) DO NOTHING;
        " >/dev/null 2>&1

        if [ $? -eq 0 ]; then
            log "  ✓ 导入用户: $username ($display_name)"
        fi
    done

    # 获取种子用户 ID 映射
    log "创建用户 ID 映射..."
    docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    CREATE TABLE IF NOT EXISTS seed_user_mapping (
        seed_id VARCHAR(50) PRIMARY KEY,
        real_id BIGINT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO seed_user_mapping (seed_id, real_id)
    SELECT
        username,
        id
    FROM users
    WHERE email LIKE '%@seed.local'
    ON CONFLICT (seed_id) DO NOTHING;
    " >/dev/null 2>&1

    # 导入 Skills
    if [ -n "$SKILLS" ]; then
        log "导入种子 Skills..."

        echo "$SKILLS" | while read -r skill; do
            skill_name=$(echo "$skill" | jq -r '.name')
            author_id=$(echo "$skill" | jq -r '.authorId')
            description=$(echo "$skill" | jq -r '.description // ""' | sed "s/'/''/g")
            type=$(echo "$skill" | jq -r '.type // "code"')
            price=$(echo "$skill" | jq -r '.pricing.price // 0')
            pricing_type=$(echo "$skill" | jq -r '.pricing.type // "free"')
            rating=$(echo "$skill" | jq -r '.rating // 5.0')
            downloads=$(echo "$skill" | jq -r '.downloads // 0')

            # 获取真实用户 ID
            real_author_id=$(docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -tAc "
                SELECT real_id FROM seed_user_mapping WHERE seed_id = '$author_id';
            " 2>/dev/null | head -1)

            if [ -z "$real_author_id" ]; then
                continue
            fi

            # 生成 skill_id
            skill_id="seed_${skill_name// /_}"

            docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
            INSERT INTO skills (
                skill_id, name, description, author_id,
                category, type, version, status,
                price, is_featured, view_count, download_count,
                rating_avg, rating_count, published_at
            ) VALUES (
                '$skill_id',
                '\$(echo "$skill_name" | sed "s/'\''/''/g")',
                '$description',
                $real_author_id,
                'tech',
                '$type',
                '1.0.0',
                'approved',
                $price,
                true,
                $((downloads * 2)),
                $downloads,
                $rating,
                10,
                CURRENT_TIMESTAMP
            ) ON CONFLICT (skill_id) DO NOTHING;
            " >/dev/null 2>&1

            if [ $? -eq 0 ]; then
                log "  ✓ 导入 Skill: $skill_name"
            fi
        done
    fi

    # 标记种子数据
    log "标记种子数据..."
    docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    -- 为种子数据添加标记
    COMMENT ON TABLE seed_user_mapping IS '种子数据用户映射表（用于清理）';

    -- 创建种子数据清理函数
    CREATE OR REPLACE FUNCTION clean_seed_data()
    RETURNS TEXT AS $$
    DECLARE
        user_count INT;
        skill_count INT;
    BEGIN
        -- 统计
        SELECT COUNT(*) INTO user_count FROM users WHERE email LIKE '%@seed.local';
        SELECT COUNT(*) INTO skill_count FROM skills WHERE skill_id LIKE 'seed_%';

        -- 删除种子 Skills
        DELETE FROM skills WHERE skill_id LIKE 'seed_%';

        -- 删除种子用户
        DELETE FROM users WHERE email LIKE '%@seed.local';

        -- 删除映射表
        DELETE FROM seed_user_mapping;

        RETURN format('已删除 %d 个种子用户和 %d 个种子 Skills', user_count, skill_count);
    END;
    $$ LANGUAGE plpgsql;

    COMMENT ON FUNCTION clean_seed_data() IS '清理所有种子数据的函数';
    " >/dev/null 2>&1

    log "======================================"
    log "种子数据导入完成！"
    log "======================================"

    # 显示统计
    docker exec sillymd-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT
        '种子用户' as type,
        COUNT(*) as count
    FROM users
    WHERE email LIKE '%@seed.local'
    UNION ALL
    SELECT
        '种子 Skills' as type,
        COUNT(*) as count
    FROM skills
    WHERE skill_id LIKE 'seed_%';
    "

    log ""
    log "提示：可以使用以下 SQL 清理种子数据："
    log "  SELECT clean_seed_data();"
    log ""
}

main "$@"

-- ============================================
-- Migration 008: 任务与成就系统
-- Task and Achievement System
--
-- 实现每日任务、成就系统、积分奖励
-- ============================================

-- ============================================
-- 1. 每日任务表
-- ============================================
CREATE TABLE IF NOT EXISTS daily_tasks (
    id SERIAL PRIMARY KEY,
    task_key VARCHAR(100) NOT NULL UNIQUE,  -- 任务唯一标识
    task_name VARCHAR(255) NOT NULL,
    task_name_en VARCHAR(255),
    task_description TEXT,
    task_description_en TEXT,
    task_type VARCHAR(50) NOT NULL,  -- sign_in, browse_content, purchase, share, invite, etc.
    task_target INTEGER NOT NULL,     -- 目标值（例如：浏览3次）
    task_reward_points INTEGER NOT NULL DEFAULT 0,  -- 奖励积分
    task_reward_currency VARCHAR(20) DEFAULT 'points',  -- 奖励类型: points, coupon, content
    reward_data JSONB,                 -- 奖励数据（优惠券ID、内容ID等）
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(100),                 -- 图标
    color VARCHAR(20),                 -- 颜色标识
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_task_type CHECK (
        task_type IN (
            'sign_in', 'browse_content', 'purchase_content',
            'share_content', 'invite_friend', 'complete_profile',
            'first_purchase', 'continuous_sign_in', 'watch_video',
            'download_resource', 'post_comment', 'like_content'
        )
    )
);

CREATE INDEX idx_daily_tasks_type ON daily_tasks(task_type);
CREATE INDEX idx_daily_tasks_active ON daily_tasks(is_active, display_order);

-- 预设每日任务
INSERT INTO daily_tasks (
    task_key, task_name, task_name_en, task_description,
    task_type, task_target, task_reward_points, icon, color, display_order
) VALUES
    ('daily_sign_in', '每日签到', 'Daily Sign In', '每天登录签到即可获得积分', 'sign_in', 1, 5, 'calendar', 'blue', 1),
    ('browse_3_tutorials', '浏览3个教程', 'Browse 3 Tutorials', '浏览任意3个教程内容', 'browse_content', 3, 10, 'book', 'green', 2),
    ('purchase_content', '购买付费内容', 'Purchase Paid Content', '购买任意付费内容', 'purchase_content', 1, 50, 'shopping-cart', 'orange', 3),
    ('share_content', '分享内容', 'Share Content', '分享任意内容到社交平台', 'share_content', 1, 15, 'share-alt', 'purple', 4)
ON CONFLICT (task_key) DO NOTHING;

-- ============================================
-- 2. 用户任务完成记录表
-- ============================================
CREATE TABLE IF NOT EXISTS user_task_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER NOT NULL REFERENCES daily_tasks(id) ON DELETE CASCADE,
    completion_date DATE NOT NULL,      -- 完成日期
    progress INTEGER NOT NULL DEFAULT 0,  -- 当前进度
    target INTEGER NOT NULL,             -- 目标值
    is_completed BOOLEAN DEFAULT FALSE,
    is_rewarded BOOLEAN DEFAULT FALSE,   -- 是否已发放奖励
    reward_given_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_task_date UNIQUE (user_id, task_id, completion_date)
);

CREATE INDEX idx_user_task_progress_user ON user_task_progress(user_id, completion_date);
CREATE INDEX idx_user_task_progress_task ON user_task_progress(task_id);
CREATE INDEX idx_user_task_progress_completed ON user_task_progress(is_completed, is_rewarded);

-- ============================================
-- 3. 成就表
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    achievement_key VARCHAR(100) NOT NULL UNIQUE,
    achievement_name VARCHAR(255) NOT NULL,
    achievement_name_en VARCHAR(255),
    description TEXT,
    description_en TEXT,
    achievement_type VARCHAR(50) NOT NULL,  -- milestone, cumulative, challenge
    requirement_type VARCHAR(50) NOT NULL,  -- sign_in_days, total_purchases, total_spent, etc.
    requirement_target INTEGER NOT NULL,
    reward_points INTEGER NOT NULL DEFAULT 0,
    reward_title VARCHAR(100),             -- 特殊头衔
    reward_badge VARCHAR(100),             -- 徽章图标
    icon VARCHAR(100),
    color VARCHAR(20),
    is_secret BOOLEAN DEFAULT FALSE,       -- 是否隐藏成就
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_achievement_type CHECK (
        achievement_type IN ('milestone', 'cumulative', 'challenge', 'special')
    )
);

CREATE INDEX idx_achievements_type ON achievements(achievement_type);
CREATE INDEX idx_achievements_active ON achievements(is_active, display_order);

-- 预设成就
INSERT INTO achievements (
    achievement_key, achievement_name, achievement_name_en, description,
    achievement_type, requirement_type, requirement_target,
    reward_points, reward_title, icon, color, display_order
) VALUES
    ('first_sign_in', '初来乍到', 'First Sign In', '完成首次签到', 'milestone', 'sign_in_days', 1, 10, '新手', 'user', 'blue', 1),
    ('sign_in_7_days', '坚持一周', '7 Days Streak', '连续签到7天', 'cumulative', 'continuous_sign_in', 7, 50, '坚持者', 'calendar-check', 'green', 2),
    ('sign_in_30_days', '月度达人', 'Monthly Master', '连续签到30天', 'cumulative', 'continuous_sign_in', 30, 300, '月度达人', 'trophy', 'purple', 3),
    ('first_purchase', '首次消费', 'First Purchase', '完成首次购买', 'milestone', 'total_purchases', 1, 100, '消费者', 'shopping-bag', 'orange', 4),
    ('purchase_10_items', '收藏家', 'Collector', '累计购买10个付费内容', 'cumulative', 'total_purchases', 10, 200, '收藏家', 'gift', 'yellow', 5),
    ('spend_1000_yuan', '千元俱乐部', '1000 RMB Club', '累计消费1000元', 'cumulative', 'total_spent', 1000, 500, 'VIP客户', 'crown', 'red', 6)
ON CONFLICT (achievement_key) DO NOTHING;

-- ============================================
-- 4. 用户成就记录表
-- ============================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    progress INTEGER NOT NULL DEFAULT 0,
    target INTEGER NOT NULL,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP WITH TIME ZONE,
    rewarded BOOLEAN DEFAULT FALSE,        -- 是否已发放奖励
    reward_given_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_achievement UNIQUE (user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_unlocked ON user_achievements(is_unlocked);

-- ============================================
-- 5. 签到记录表
-- ============================================
CREATE TABLE IF NOT EXISTS sign_in_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sign_in_date DATE NOT NULL,
    sign_in_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    consecutive_days INTEGER NOT NULL DEFAULT 1,  -- 连续签到天数
    points_earned INTEGER NOT NULL DEFAULT 5,  -- 本次签到获得的积分
    is_first_sign_in_today BOOLEAN DEFAULT TRUE,  -- 今天是否首次签到
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_date UNIQUE (user_id, sign_in_date)
);

CREATE INDEX idx_sign_in_records_user ON sign_in_records(user_id, sign_in_date);
CREATE INDEX idx_sign_in_records_consecutive ON sign_in_records(user_id, consecutive_days DESC);

-- ============================================
-- 6. 触发器：自动更新任务进度
-- ============================================

-- 更新连续签到天数
CREATE OR REPLACE FUNCTION update_consecutive_sign_in_days()
RETURNS TRIGGER AS $$
DECLARE
    v_consecutive INTEGER;
BEGIN
    -- 获取用户之前的连续签到天数
    SELECT COALESCE(MAX(consecutive_days), 0)
    INTO v_consecutive
    FROM sign_in_records
    WHERE user_id = NEW.user_id
      AND sign_in_date = (
          SELECT MAX(sign_in_date)
          FROM sign_in_records
          WHERE user_id = NEW.user_id
            AND sign_in_date < CURRENT_DATE
      );

    -- 如果昨天签到了，连续天数+1，否则从1开始
    IF v_consecutive > 0 THEN
        NEW.consecutive_days = v_consecutive + 1;
    ELSE
        NEW.consecutive_days = 1;
    END IF;

    -- 连续签到奖励：每7天额外奖励
    IF NEW.consecutive_days >= 7 AND NEW.consecutive_days % 7 = 0 THEN
        NEW.points_earned = 5 + NEW.consecutive_days;  -- 基础5分 + 连续奖励
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_consecutive_days
    BEFORE INSERT ON sign_in_records
    FOR EACH ROW
    EXECUTE FUNCTION update_consecutive_sign_in_days();

-- ============================================
-- 7. 视图：用户今日任务概览
-- ============================================
CREATE OR REPLACE VIEW v_user_daily_tasks AS
SELECT
    u.id AS user_id,
    dt.id AS task_id,
    dt.task_key,
    dt.task_name,
    dt.task_description,
    dt.task_type,
    dt.task_target,
    dt.task_reward_points,
    dt.icon,
    dt.color,
    COALESCE(utp.progress, 0) AS progress,
    dt.task_target AS target,
    CASE WHEN utp.is_completed IS TRUE THEN TRUE ELSE FALSE END AS is_completed,
    CASE WHEN utp.is_rewarded IS TRUE THEN TRUE ELSE FALSE END AS is_rewarded
FROM users u
CROSS JOIN daily_tasks dt
LEFT JOIN user_task_progress utp ON (
    utp.task_id = dt.id
    AND utp.user_id = u.id
    AND utp.completion_date = CURRENT_DATE
)
WHERE dt.is_active = TRUE;

-- ============================================
-- 8. 函数：用户签到
-- ============================================
CREATE OR REPLACE FUNCTION user_sign_in(
    p_user_id INTEGER,
    p_ip_address VARCHAR(45) DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
    v_total_points INTEGER;
    v_consecutive INTEGER;
    v_new_record RECORD;
BEGIN
    -- 插入签到记录
    INSERT INTO sign_in_records (
        user_id, sign_in_date, ip_address, user_agent
    ) VALUES (
        p_user_id, CURRENT_DATE, p_ip_address, p_user_agent
    )
    RETURNING * INTO v_new_record;

    -- 更新用户积分
    UPDATE user_points
    SET
        balance = balance + v_new_record.points_earned,
        total_earned = total_earned + v_new_record.points_earned,
        -- 连续签到7天增加经验值
        experience = experience + CASE
            WHEN v_new_record.consecutive_days >= 30 THEN 50
            WHEN v_new_record.consecutive_days >= 7 THEN 20
            ELSE 5
        END
    WHERE user_id = p_user_id;

    -- 记录积分交易
    INSERT INTO point_transactions (
        user_id,
        transaction_type,
        transaction_source,
        amount,
        balance_before,
        balance_after,
        description
    )
    SELECT
        p_user_id,
        'earn',
        'daily_sign_in',
        v_new_record.points_earned,
        balance - v_new_record.points_earned,
        balance,
        '每日签到奖励，连续' || v_new_record.consecutive_days || '天'
    FROM user_points
    WHERE user_id = p_user_id;

    -- 自动完成每日签到任务
    INSERT INTO user_task_progress (
        user_id, task_id, completion_date, progress, target, is_completed, completed_at
    )
    SELECT
        p_user_id,
        id,
        CURRENT_DATE,
        1,
        1,
        TRUE,
        CURRENT_TIMESTAMP
    FROM daily_tasks
    WHERE task_key = 'daily_sign_in'
    ON CONFLICT (user_id, task_id, completion_date)
    DO UPDATE SET
        is_completed = TRUE,
        completed_at = CURRENT_TIMESTAMP;

    -- 检查并解锁成就
    PERFORM check_and_unlock_achievements(p_user_id);

    -- 返回结果
    SELECT
        v_new_record.points_earned AS points_earned,
        v_new_record.consecutive_days AS consecutive_days,
        up.balance AS current_balance
    INTO v_total_points, v_consecutive, up.balance
    FROM user_points up
    WHERE up.user_id = p_user_id;

    RETURN json_build_object(
        'success', TRUE,
        'points_earned', v_total_points,
        'consecutive_days', v_consecutive,
        'current_balance', v_total_points,
        'sign_in_date', v_new_record.sign_in_date,
        'sign_in_time', v_new_record.sign_in_time
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 9. 函数：检查并解锁成就
-- ============================================
CREATE OR REPLACE FUNCTION check_and_unlock_achievements(
    p_user_id INTEGER
) RETURNS VOID AS $$
DECLARE
    v_achievement RECORD;
    v_user_stats RECORD;
    v_progress INTEGER;
BEGIN
    -- 获取用户统计信息
    SELECT
        COALESCE(SUM(CASE WHEN consecutive_days >= 1 THEN 1 ELSE 0 END), 0) AS total_sign_in_days,
        COALESCE(MAX(consecutive_days), 0) AS max_consecutive_days,
        COALESCE(SUM(CASE WHEN is_completed = TRUE THEN 1 ELSE 0 END), 0) AS total_completed_tasks,
        COALESCE(SUM(final_price), 0) AS total_spent
    INTO v_user_stats
    FROM sign_in_records
    WHERE user_id = p_user_id;

    -- 检查每个成就
    FOR v_achievement IN
        SELECT * FROM achievements WHERE is_active = TRUE
    LOOP
        -- 计算当前进度
        v_progress := 0;

        CASE v_achievement.requirement_type
            WHEN 'sign_in_days' THEN
                SELECT COUNT(*) INTO v_progress FROM sign_in_records WHERE user_id = p_user_id;
            WHEN 'continuous_sign_in' THEN
                SELECT COALESCE(MAX(consecutive_days), 0) INTO v_progress FROM sign_in_records WHERE user_id = p_user_id;
            WHEN 'total_purchases' THEN
                SELECT COUNT(*) INTO v_progress FROM orders WHERE user_id = p_user_id AND payment_status = 'paid';
            WHEN 'total_spent' THEN
                v_progress := FLOOR(v_user_stats.total_spent);
            ELSE
                v_progress := 0;
        END CASE;

        -- 检查是否达成
        IF v_progress >= v_achievement.requirement_target THEN
            -- 解锁成就
            INSERT INTO user_achievements (
                user_id, achievement_id, progress, target, is_unlocked, unlocked_at
            ) VALUES (
                p_user_id, v_achievement.id, v_progress, v_achievement.requirement_target, TRUE, CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id, achievement_id)
            DO UPDATE SET
                progress = v_progress,
                is_unlocked = TRUE,
                unlocked_at = CASE WHEN user_achievements.is_unlocked = FALSE THEN CURRENT_TIMESTAMP ELSE user_achievements.unlocked_at END;

            -- 发放奖励（如果还没发放）
            IF NOT FOUND OR (FOUND AND NOT user_achievements.rewarded) THEN
                UPDATE user_points
                SET
                    balance = balance + v_achievement.reward_points,
                    total_earned = total_earned + v_achievement.reward_points
                WHERE user_id = p_user_id;

                -- 记录积分交易
                INSERT INTO point_transactions (
                    user_id,
                    transaction_type,
                    transaction_source,
                    amount,
                    balance_before,
                    balance_after,
                    description
                )
                SELECT
                    p_user_id,
                    'earn',
                    'achievement_reward',
                    v_achievement.reward_points,
                    balance - v_achievement.reward_points,
                    balance,
                    '成就奖励：' || v_achievement.achievement_name
                FROM user_points
                WHERE user_id = p_user_id;

                -- 标记为已奖励
                UPDATE user_achievements
                SET rewarded = TRUE,
                reward_given_at = CURRENT_TIMESTAMP
                WHERE user_id = p_user_id
                  AND achievement_id = v_achievement.id;
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 10. 函数：检查任务完成状态
-- ============================================
CREATE OR REPLACE FUNCTION check_task_completion(
    p_user_id INTEGER,
    p_task_key VARCHAR(100)
) RETURNS INTEGER AS $$
DECLARE
    v_progress INTEGER;
BEGIN
    -- 根据任务类型检查进度
    IF p_task_key = 'browse_3_tutorials' THEN
        SELECT COUNT(*) INTO v_progress
        FROM tutorial_view_records
        WHERE user_id = p_user_id
          AND viewed_at >= CURRENT_DATE;

    ELSIF p_task_key = 'purchase_content' THEN
        SELECT COUNT(*) INTO v_progress
        FROM orders
        WHERE user_id = p_user_id
          AND payment_status = 'paid'
          AND paid_at >= CURRENT_DATE;

    ELSIF p_task_key = 'share_content' THEN
        SELECT COUNT(*) INTO v_progress
        FROM share_records
        WHERE user_id = p_user_id
          AND shared_at >= CURRENT_DATE;

    ELSE
        v_progress := 0;
    END IF;

    RETURN v_progress;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 11. 授权
-- ============================================
GRANT SELECT, INSERT, UPDATE, DELETE ON daily_tasks TO sillymd_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_task_progress TO sillymd_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON achievements TO sillymd_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_achievements TO sillymd_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON sign_in_records TO sillymd_user;
GRANT EXECUTE ON FUNCTION user_sign_in TO sillymd_user;
GRANT EXECUTE ON FUNCTION check_and_unlock_achievements TO sillymd_user;
GRANT EXECUTE ON FUNCTION check_task_completion TO sillymd_user;
GRANT SELECT ON v_user_daily_tasks TO sillymd_user;

-- ============================================
-- 完成
-- ============================================
COMMENT ON TABLE daily_tasks IS '每日任务配置';
COMMENT ON TABLE user_task_progress IS '用户任务进度记录';
COMMENT ON TABLE achievements IS '成就配置';
COMMENT ON TABLE user_achievements IS '用户成就记录';
COMMENT ON TABLE sign_in_records IS '签到记录';

SELECT 'Migration 008: Task and Achievement System completed successfully' AS status;

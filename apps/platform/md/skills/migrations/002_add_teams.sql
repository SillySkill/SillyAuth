-- ============================================
-- 迁移脚本: 添加团队协作功能
-- 版本: 002
-- 描述: 创建团队、团队成员和项目相关表
-- 作者: 数据库团队
-- 日期: 2026-02-03
-- 向前兼容: 是
-- 可回滚: 是
-- ============================================

BEGIN;

-- 防止重复执行
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '002') THEN
        RAISE EXCEPTION 'Migration 002 already applied';
    END IF;
END
$$;

-- ============================================
-- 团队表
-- ============================================
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    member_count INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON TABLE teams IS '团队主表，用于多领域协作';
COMMENT ON COLUMN teams.id IS '团队 ID';
COMMENT ON COLUMN teams.team_name IS '团队名称（3-100字符，唯一）';
COMMENT ON COLUMN teams.team_slug IS '团队 URL 标识符（唯一）';
COMMENT ON COLUMN teams.owner_id IS '团队所有者 ID';
COMMENT ON COLUMN teams.description IS '团队简介';
COMMENT ON COLUMN teams.avatar_url IS '团队头像 URL';
COMMENT ON COLUMN teams.member_count IS '成员数量（冗余字段）';
COMMENT ON COLUMN teams.is_active IS '团队是否激活';
COMMENT ON COLUMN teams.created_at IS '团队创建时间';
COMMENT ON COLUMN teams.updated_at IS '最后更新时间';

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_teams_owner_id ON teams(owner_id);
CREATE INDEX idx_teams_slug ON teams(team_slug);

-- ============================================
-- 团队成员表
-- ============================================
CREATE TABLE team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role team_role DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (team_id, user_id)
);

COMMENT ON TABLE team_members IS '团队成员关系表';
COMMENT ON COLUMN team_members.id IS '成员 ID';
COMMENT ON COLUMN team_members.team_id IS '团队 ID';
COMMENT ON COLUMN team_members.user_id IS '成员用户 ID';
COMMENT ON COLUMN team_members.role IS '角色：owner=所有者, admin=管理员, member=成员, viewer=访客';
COMMENT ON COLUMN team_members.joined_at IS '加入时间';

CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

-- ============================================
-- 团队项目表
-- ============================================
CREATE TABLE team_projects (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    project_slug VARCHAR(200) NOT NULL,
    description TEXT,
    owner_id BIGINT NOT NULL,
    project_status project_status DEFAULT 'planned',
    progress INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    UNIQUE (team_id, project_slug)
);

COMMENT ON TABLE team_projects IS '团队项目表';
COMMENT ON COLUMN team_projects.id IS '项目 ID';
COMMENT ON COLUMN team_projects.team_id IS '所属团队 ID';
COMMENT ON COLUMN team_projects.project_name IS '项目名称';
COMMENT ON COLUMN team_projects.project_slug IS '项目 URL 标识符';
COMMENT ON COLUMN team_projects.description IS '项目描述';
COMMENT ON COLUMN team_projects.owner_id IS '项目负责人 ID';
COMMENT ON COLUMN team_projects.project_status IS '项目状态：planned=计划中, in_progress=进行中, on_hold=暂停, completed=已完成, cancelled=已取消';
COMMENT ON COLUMN team_projects.progress IS '项目进度百分比（0-100）';
COMMENT ON COLUMN team_projects.is_active IS '是否激活';
COMMENT ON COLUMN team_projects.created_at IS '创建时间';
COMMENT ON COLUMN team_projects.updated_at IS '最后更新时间';

CREATE TRIGGER update_team_projects_updated_at BEFORE UPDATE ON team_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_team_projects_team_id ON team_projects(team_id);
CREATE INDEX idx_team_projects_status ON team_projects(project_status);

-- ============================================
-- 项目 Skills 关联表
-- ============================================
CREATE TABLE project_skills (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    role TEXT DEFAULT 'other',
    order_index INT DEFAULT 0,
    added_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (project_id, skill_id)
);

COMMENT ON TABLE project_skills IS '项目-Skills 关联表';
COMMENT ON COLUMN project_skills.id IS '关联 ID';
COMMENT ON COLUMN project_skills.project_id IS '项目 ID';
COMMENT ON COLUMN project_skills.skill_id IS 'Skill ID';
COMMENT ON COLUMN project_skills.role IS '在项目中的角色：frontend, backend, tool, other';
COMMENT ON COLUMN project_skills.order_index IS '排序索引';
COMMENT ON COLUMN project_skills.added_at IS '添加时间';

CREATE INDEX idx_project_skills_project_id ON project_skills(project_id);
CREATE INDEX idx_project_skills_skill_id ON project_skills(skill_id);

-- ============================================
-- 项目里程碑表
-- ============================================
CREATE TABLE project_milestones (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    milestone_name VARCHAR(200) NOT NULL,
    description TEXT,
    target_date TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'planned',
    completed_at TIMESTAMPTZ,
    created_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

COMMENT ON TABLE project_milestones IS '项目里程碑表';
COMMENT ON COLUMN project_milestones.id IS '里程碑 ID';
COMMENT ON COLUMN project_milestones.project_id IS '项目 ID';
COMMENT ON COLUMN project_milestones.milestone_name IS '里程碑名称';
COMMENT ON COLUMN project_milestones.description IS '描述';
COMMENT ON COLUMN project_milestones.target_date IS '目标完成时间';
COMMENT ON COLUMN project_milestones.status IS '状态：planned, in_progress, completed, delayed';
COMMENT ON COLUMN project_milestones.completed_at IS '实际完成时间';
COMMENT ON COLUMN project_milestones.created_by IS '创建者 ID';
COMMENT ON COLUMN project_milestones.created_at IS '创建时间';
COMMENT ON COLUMN project_milestones.updated_at IS '更新时间';

CREATE TRIGGER update_project_milestones_updated_at BEFORE UPDATE ON project_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX idx_project_milestones_status ON project_milestones(status);

-- ============================================
-- 记录迁移版本
-- ============================================
INSERT INTO schema_migrations (version, description, rollback_available)
VALUES ('002', '添加团队协作功能', TRUE);

COMMIT;

-- ============================================
-- 回滚脚本
-- ============================================
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_project_milestones_status;
DROP INDEX IF EXISTS idx_project_milestones_project_id;
DROP INDEX IF EXISTS idx_project_skills_skill_id;
DROP INDEX IF EXISTS idx_project_skills_project_id;
DROP INDEX IF EXISTS idx_team_projects_status;
DROP INDEX IF EXISTS idx_team_projects_team_id;
DROP INDEX IF EXISTS idx_team_members_user_id;
DROP INDEX IF EXISTS idx_team_members_team_id;
DROP INDEX IF EXISTS idx_teams_slug;
DROP INDEX IF EXISTS idx_teams_owner_id;

-- 删除触发器
DROP TRIGGER IF EXISTS update_project_milestones_updated_at ON project_milestones;
DROP TRIGGER IF EXISTS update_team_projects_updated_at ON team_projects;
DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;

-- 删除表
DROP TABLE IF EXISTS project_milestones;
DROP TABLE IF EXISTS project_skills;
DROP TABLE IF EXISTS team_projects;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS teams;

-- 删除枚举类型
DROP TYPE IF EXISTS project_status;

-- 删除迁移记录
DELETE FROM schema_migrations WHERE version = '002';

COMMIT;
*/

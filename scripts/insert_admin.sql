-- Active: 1751424527724@@127.0.0.1@3306@cmdb
-- 初始化 admin 账号（请根据实际 hash 替换 hashed_password）
INSERT INTO users (
    id, email, username, full_name, hashed_password, is_active, is_superuser, is_verified, created_at, updated_at
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    'admin@example.com',
    'admin',
    '超级管理员',
    '$2b$12$eIX8n6Q1FQJ8Q1FQJ8Q1F.Q1FQJ8Q1FQJ8Q1FQJ8Q1FQJ8Q1FQJ8Q1', -- 示例 bcrypt hash
    1,
    1,
    1,
    NOW(),
    NOW()
);

-- 让 admin 拥有所有资源和所有操作的 Casbin 权限（MySQL版，通配符*）
-- 假设 casbin_rule 表结构为 Casbin SQLAlchemy Adapter 默认

INSERT INTO `casbin_rule` (`ptype`, `v0`, `v1`, `v2`) VALUES
('p', 'admin', 'asset', 'read'),
('p', 'admin', 'asset', 'write'),
('p', 'admin', 'asset', 'delete'),
('p', 'admin', 'user', 'read'),
('p', 'admin', 'user', 'write'),
('p', 'admin', 'user', 'delete'),
('p', 'admin', 'role', 'read'),
('p', 'admin', 'role', 'write'),
('p', 'admin', 'role', 'delete');

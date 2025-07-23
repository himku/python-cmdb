-- 创建 casbin_model 表
CREATE TABLE IF NOT EXISTS `casbin_model` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `content` TEXT NOT NULL COMMENT 'Casbin模型内容'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入初始 Casbin 权限模型内容
INSERT INTO `casbin_model` (`content`) VALUES (
'[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
');

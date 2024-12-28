-- 添加商机管理菜单
INSERT INTO menu (
    parent_id,
    path,
    name,
    component,
    title,
    icon,
    sort,
    hidden
) VALUES (
    (SELECT id FROM menu WHERE path = '/house'),  -- 获取房源管理的ID作为父ID
    '/house/opportunity',
    'Opportunity',
    'house/opportunity/index',
    '商机管理',
    'opportunity',
    4,  -- 在房源管理下排第4个
    0
); 

-- 添加商机管理相关API权限
INSERT INTO api (
    path,
    method,
    description,
    module
) VALUES 
    ('/v1/house/opportunities', 'GET', '获取商机列表', 'opportunity'),
    ('/v1/house/opportunities', 'POST', '创建商机', 'opportunity'),
    ('/v1/house/opportunities/{id}', 'PUT', '更新商机', 'opportunity'),
    ('/v1/house/opportunities/{id}', 'DELETE', '删除商机', 'opportunity');

-- 为管理员角色添加商机管理权限
INSERT INTO role_apis (
    role_id,
    api_id
) 
SELECT 
    (SELECT id FROM role WHERE role_key = 'admin'),
    id 
FROM api 
WHERE module = 'opportunity';

-- 为管理员角色添加商机管理菜单权限
INSERT INTO role_menus (
    role_id,
    menu_id
)
SELECT 
    (SELECT id FROM role WHERE role_key = 'admin'),
    id
FROM menu 
WHERE path = '/house/opportunity'; 
# 管理员小工具
通过自身存储的账号与密码，实现对环境变量的配置。
请将config.json.template修改为config.json后再进行使用。调用请初始化adminService类
将此文件夹放入项目根目录下，调用时请使用相对路径
## 自身配置：

```json
{
    "admin_id": [], # 管理员id，可以传入不同的特殊id作为表示符
    "admin_password": "", # 管理员密码
}
```

## 使用方法：
```python
from adminService.adminService import adminService

ad = adminService()

# 认证管理员
ad.verify_admin(admin_id, admin_password)

# 判断管理员
ad.is_admin(admin_id)

# 修改管理员密码
ad.change_password(admin_id, new_password)

# 清空管理员名单
ad.clear_admin(admin_id)

# 添加项目json值,可变参数(config[key1][key2][key3]=value), value需要使用value=格式
ad.append_json(admin_id, key1, key2, key3, value)

# 修改项目json值，同上
ad.update_json(admin_id, key1, key2, key3, value)

```

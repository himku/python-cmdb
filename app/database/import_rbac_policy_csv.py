"""
将 app/core/rbac_policy.csv 批量导入到数据库 Casbin 策略表
只需运行一次即可
"""
import os
import sys
import csv

# 确保可以从项目根目录运行
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.casbin_service import CasbinService

CSV_PATH = os.path.join(os.path.dirname(__file__), '../core/rbac_policy.csv')

def import_csv_to_db():
    print(f"开始导入 {CSV_PATH} 到数据库...")
    enforcer = CasbinService.get_enforcer()
    
    # 读取CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            row = [x.strip() for x in row if x.strip()]
            if not row or row[0].startswith('#'):
                continue
            if row[0] == 'p':
                # p, sub, obj, act
                if len(row) >= 4:
                    sub, obj, act = row[1], row[2], row[3]
                    if enforcer.add_policy(sub, obj, act):
                        print(f"添加策略: {sub} -> {obj} [{act}]")
                        count += 1
            elif row[0] == 'g':
                # g, user, role
                if len(row) >= 3:
                    user, role = row[1], row[2]
                    if enforcer.add_role_for_user(user, role):
                        print(f"分配角色: {user} -> {role}")
                        count += 1
        enforcer.save_policy()
    print(f"导入完成，共导入 {count} 条策略/角色分配。")

if __name__ == "__main__":
    import_csv_to_db() 
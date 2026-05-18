```text
auto-deployment/
├── terraform/
│   ├── main.tf          # 主配置文件
│   ├── variables.tf     # 变量定义
│   ├── outputs.tf       # 输出定义
│   └── terraform.tfvars # 变量赋值
├── ansible/
│   ├── inventory/       # 动态生成的 inventory
│   ├── playbooks/       # Ansible 剧本
│   └── roles/           # Ansible 角色
└── deploy.sh            # 自动化部署脚本
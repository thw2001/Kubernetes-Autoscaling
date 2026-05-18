#!/bin/bash
set -e

echo "========================================="
echo "开始清理实验环境（按量资源将停止计费）"
echo "========================================="

# 1. 进入 Terraform 目录
cd terraform

# 2. 销毁所有资源（自动确认）
echo "正在销毁 Terraform 管理的所有资源..."
terraform destroy -auto-approve

# 3. 清理临时文件（可选）
echo "清理本地临时文件..."
cd ..
rm -f ansible/inventory/aliyun.pyc   # Python 缓存（如果有）
rm -f terraform/terraform.tfstate  # 状态文件
rm -f terraform/terraform.tfstate.backup  # 状态文件备份（可选）
rm -f terraform/.terraform.lock.hcl  # 锁文件（可选）
rm -r terraform/.terraform

# 4. 清理 SSH known_hosts 中实验节点的记录（避免下次连接时提示）
echo "清理 SSH known_hosts ..."
cd ..
rm -f .ssh/known_hosts .ssh/known_hosts.old
echo "thw2001" | sudo -S rm -f /root/.ssh/known_hosts /root/.ssh/known_hosts.old
echo
echo "========================================="
echo "清理完成！所有按量资源已停止计费。"
echo "========================================="
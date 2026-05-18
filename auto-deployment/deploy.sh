#!/bin/bash
set -e

echo "========================================="
echo "k3s + AI 自动化部署脚本"
echo "========================================="

# 1. Terraform 创建基础设施
echo "[1/4] 使用Terraform创建云资源..."
cd terraform
terraform init
terraform apply -auto-approve

# 2. 获取IP地址
echo "[2/4] 获取节点IP..."
MASTER_IP=$(terraform output -raw master_public_ip)
WORKER_IPS=$(terraform output -json worker_public_ips | jq -r 'join(",")')
ALL_IPS=$(terraform output -json all_ips | jq -r 'join(" ")')

echo "Master IP: $MASTER_IP"
echo "Worker IPs: $WORKER_IPS"

# 3. 等待SSH就绪
echo "[3/4] 等待SSH服务就绪..."
for IP in $ALL_IPS; do
  echo "等待 $IP ..."
  while ! nc -z $IP 22; do
    sleep 5
  done
  echo "$IP SSH已就绪"
done

# 4. Ansible部署k3s
echo "[4/4] 使用Ansible部署k3s集群..."
cd ../ansible

export MASTER_IP=$MASTER_IP
export WORKER_IPS=$WORKER_IPS
export ANSIBLE_HOST_KEY_CHECKING=False

ansible-playbook -i inventory/aliyun.py playbooks/deploy-k3s.yml

echo "========================================="
echo "✅ 部署完成！"
echo "Master IP: $MASTER_IP"
echo "Worker IPs: $WORKER_IPS"
echo "连接集群: sudo ssh -i ~/.ssh/id_rsa_k3s root@$MASTER_IP"
echo "查看节点: kubectl get nodes"
echo "查看Pod: kubectl get pods --all-namespaces"
echo "========================================="
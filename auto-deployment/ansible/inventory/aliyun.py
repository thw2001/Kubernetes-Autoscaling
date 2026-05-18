#!/usr/bin/env python3
import json
import os
import sys

# 从环境变量或文件读取Terraform输出的IP
# 实际使用时，可以从terraform.tfstate解析，或者由deploy.sh传入

def main():
    master_ip = os.environ.get("MASTER_IP", "")
    worker_ips = os.environ.get("WORKER_IPS", "").split(",") if os.environ.get("WORKER_IPS") else []

    inventory = {
        "k3s_master": {
            "hosts": [master_ip] if master_ip else [],
            "vars": {
                "ansible_user": "root",
                "ansible_ssh_private_key_file": "~/.ssh/id_rsa_k3s"
            }
        },
        "k3s_worker": {
            "hosts": worker_ips,
            "vars": {
                "ansible_user": "root",
                "ansible_ssh_private_key_file": "~/.ssh/id_rsa_k3s"
            }
        },
        "_meta": {
            "hostvars": {}
    }
    }
    
    # 为 Master 节点添加 hostname
    if master_ip:
        inventory["_meta"]["hostvars"][master_ip] = {
            "hostname": "k3s-master"
        }

    # 为 Worker 节点添加 hostname（支持多个）
    for idx, ip in enumerate(worker_ips):
        name = "k3s-worker" if len(worker_ips) == 1 else f"k3s-worker-{idx}"
        inventory["_meta"]["hostvars"][ip] = {
            "hostname": name
        }

    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
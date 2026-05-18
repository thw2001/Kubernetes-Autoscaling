# 配置阿里云Provider
provider "alicloud" {

}

# 查询可用区
data "alicloud_zones" "default" {
  available_disk_category     = "cloud_essd"
  available_resource_creation = "VSwitch"
}

# 创建VPC
resource "alicloud_vpc" "vpc" {
  vpc_name   = var.cluster_name
  cidr_block = "172.16.0.0/16"
}

# 创建交换机
resource "alicloud_vswitch" "vsw" {
  vpc_id     = alicloud_vpc.vpc.id
  cidr_block = "172.16.0.0/24"
  zone_id    = data.alicloud_zones.default.zones.0.id
  vswitch_name = var.cluster_name
}

# 创建安全组
resource "alicloud_security_group" "sg" {
  security_group_name   = var.cluster_name
  vpc_id = alicloud_vpc.vpc.id
}

# 开放必要端口：SSH(22), k3s API(6443), etcd(2379), NodePort(30000-32767)
resource "alicloud_security_group_rule" "allow_ssh" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "22/22"
  priority          = 1
  security_group_id = alicloud_security_group.sg.id
  cidr_ip           = "0.0.0.0/0"
}

resource "alicloud_security_group_rule" "allow_k3s_api" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "6443/6443"
  priority          = 1
  security_group_id = alicloud_security_group.sg.id
  cidr_ip           = "0.0.0.0/0"
}

resource "alicloud_security_group_rule" "allow_nodeport" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "30000/32767"
  priority          = 1
  security_group_id = alicloud_security_group.sg.id
  cidr_ip           = "0.0.0.0/0"
}

resource "alicloud_key_pair" "k3s_key" {
  key_pair_name   = "k3s-key"
  public_key = file("~/.ssh/id_rsa_k3s.pub")
}

# 创建Master节点（按量付费）
resource "alicloud_instance" "master" {
  instance_name   = "${var.cluster_name}-master"
  host_name       = "${var.cluster_name}-master"
  image_id        = var.image_id  # Ubuntu 22.04
  instance_type   = var.master_instance_type
  security_groups = [alicloud_security_group.sg.id]
  vswitch_id      = alicloud_vswitch.vsw.id
  key_name        = alicloud_key_pair.k3s_key.id
  password        = ""
  
  system_disk_category = "cloud_essd"
  system_disk_size     = 40
  
  internet_max_bandwidth_out = 3

  instance_charge_type = "PostPaid"
  
  tags = {
    Role = "k3s-master"
  }
}

# 创建Worker节点（按量付费）
resource "alicloud_instance" "worker" {
  count           = var.worker_count
  instance_name   = "${var.cluster_name}-worker-${count.index}"
  host_name       = "${var.cluster_name}-worker-${count.index}"
  image_id        = var.image_id
  instance_type   = var.worker_instance_type
  security_groups = [alicloud_security_group.sg.id]
  vswitch_id      = alicloud_vswitch.vsw.id
  key_name        = alicloud_key_pair.k3s_key.id
  password        = ""
  
  system_disk_category = "cloud_essd"
  system_disk_size     = 40
  
  internet_max_bandwidth_out = 5
  
  instance_charge_type = "PostPaid"

  tags = {
    Role = "k3s-worker"
  }
}

# 输出IP地址供Ansible使用
output "master_public_ip" {
  value = alicloud_instance.master.public_ip
}

output "worker_public_ips" {
  value = alicloud_instance.worker[*].public_ip
}

output "all_ips" {
  value = concat(
    [alicloud_instance.master.public_ip],
    alicloud_instance.worker[*].public_ip
  )
}
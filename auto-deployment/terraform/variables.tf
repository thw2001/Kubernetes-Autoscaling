variable "cluster_name" {
  default = "k3s-ai-cluster"
}

variable "image_id" {
  default = "ubuntu_22_04_x64_20G_alibase_20260213.vhd"  # Ubuntu 22.04
}

variable "gpu_image_id" {
  default = "ubuntu_22_04_x64_100G_with_gpu_driver_and_cuda_alibase_20251229.vhd"  # GPU驱动已安装
}

variable "master_instance_type" {
  default = "ecs.e-c1m2.large"  # 2核4G
}

variable "worker_instance_type" {
  default = "ecs.e-c1m2.xlarge"  # 4核8G
}

variable "gpu_instance_type" {
  default = "ecs.gn6i-c4g1.xlarge"  # 4核15G + T4
}

variable "worker_count" {
  default = 1
}

variable "gpu_worker_count" {
  default = 1
}

variable "instance_password" {
  default = "YourPassword123!"  # 建议使用复杂密码
}
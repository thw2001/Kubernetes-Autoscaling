# Intelligent Proactive Autoscaling for Kubernetes  
# 面向 Kubernetes 的智能主动式弹性伸缩系统

本项目是一个**研究导向（research-oriented）**的 Kubernetes 主动式弹性伸缩实现，融合以下核心技术：

- **LSTM 负载预测（Workload Prediction）**
- **MC Dropout 不确定性估计（Uncertainty Estimation）**
- **基于 MDP 的决策建模（MDP Modeling）**
- **DQN 强化学习决策（RL-based Scaling Policy）**
- **Kubernetes 在线自动扩缩容执行（Online Scaling Execution）**

项目目标是同时优化：

- **服务性能（降低延迟）**
- **资源成本（减少资源浪费）**
- **伸缩稳定性（减少频繁震荡）**
- **预测风险（考虑预测不确定性）**

---

# 1. 项目背景

Kubernetes 默认的 **Horizontal Pod Autoscaler (HPA)** 属于**被动式（Reactive）扩缩容**：

- 只有当 CPU / Memory 指标超过阈值时才触发扩容；
- 面对突发流量时，容易出现：

  - 服务延迟骤增；
  - SLA 违约；
  - 扩容响应滞后。

本项目提出一种**主动式（Proactive）自动扩缩容方案**：

> 提前预测未来负载，并在系统真正过载前完成资源调整。

---

# 2. 系统整体架构

```text
                ┌──────────────────────┐
                │   Prometheus监控数据 │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   LSTM负载预测模块   │
                │   + MC Dropout       │
                └──────────┬───────────┘
                           │
                  (μ, σ, risk)
                           │
                           ▼
                ┌──────────────────────┐
                │   RL智能决策模块     │
                │      (DQN)           │
                └──────────┬───────────┘
                           │
                        action
                           │
                           ▼
                ┌──────────────────────┐
                │ kubectl scale执行层  │
                │ Kubernetes集群       │
                └──────────────────────┘
```

---

# 3. 项目目录结构

```text
autoscaling_project/
├── predictor/
│   ├── train_lstm.py
│   └── predictor.py
│
├── simulator/
│   └── autoscaling_env.py
│
├── rl/
│   └── train_dqn.py
│
├── controller/
│   └── autoscaling_controller.py
│
├── config/
│   ├── config.yaml
│   └── load_config.py
│
├── requirements.txt
└── README.md
```

---

# 4. 核心模块说明

---

## 4.1 LSTM 负载预测模块

文件位置：

```text
predictor/train_lstm.py
```

作用：

- 使用历史监控数据训练 LSTM 模型；
- 预测未来一段时间的系统负载；
- 输出预测值：

\[
\mu_t
\]

输入特征包括：

- CPU 利用率
- Memory 利用率
- 请求速率（QPS）
- 服务延迟（Latency）

输入窗口格式：

```text
(window_size, feature_dim)
```

默认：

```text
(20, 4)
```

训练完成后生成：

```text
lstm_model.pt
```

---

## 4.2 预测不确定性估计（MC Dropout）

文件位置：

```text
predictor/predictor.py
```

作用：

> 利用 Monte Carlo Dropout 对预测结果进行不确定性建模。

方法：

对同一输入进行多次随机前向传播：

\[
\{y_1,y_2,...,y_N\}
\]

计算：

预测均值：

\[
\mu=\frac{1}{N}\sum y_i
\]

预测标准差：

\[
\sigma=\sqrt{
\frac{1}{N}
\sum (y_i-\mu)^2
}
\]

定义风险指标：

\[
Risk=\frac{\sigma}{\mu}
\]

其中：

- σ 越大 → 预测越不稳定；
- Risk 越高 → RL 决策应更加保守。

---

## 4.3 MDP 决策环境建模

文件位置：

```text
simulator/autoscaling_env.py
```

状态空间：

\[
s_t=
(cpu,
mem,
qps,
replicas,
\mu,
\sigma,
risk)
\]

分别表示：

- 当前 CPU
- 当前内存
- 当前负载 QPS
- 当前 Pod 副本数
- 预测负载均值
- 预测不确定性
- 风险指标

---

动作空间：

```text
0 = Scale In   （缩容）
1 = Maintain   （保持）
2 = Scale Out  （扩容）
```

---

奖励函数：

\[
R_t=
-\alpha D_t
-\beta C_t
-\gamma O_t
-\eta Risk_t
\]

其中：

- \(D_t\)：性能惩罚（延迟）
- \(C_t\)：资源成本（Pod 数）
- \(O_t\)：震荡惩罚（频繁伸缩）
- \(Risk_t\)：预测风险惩罚

目标：

> 最大化长期累计奖励。

---

## 4.4 强化学习训练模块

文件位置：

```text
rl/train_dqn.py
```

算法：

- Deep Q-Network (DQN)

依赖库：

- Stable-Baselines3

目标：

学习最优扩缩容策略：

\[
\pi^*(s)
\]

训练输出：

```text
dqn_agent.zip
```

---

## 4.5 在线控制器模块

文件位置：

```text
controller/autoscaling_controller.py
```

运行流程：

### Step 1：获取实时监控数据

从 Prometheus 获取：

- CPU
- Memory
- QPS

---

### Step 2：构造时间窗口

取最近：

```text
20
```

个时间步监控序列。

---

### Step 3：LSTM 预测

得到：

```text
μ, σ
```

---

### Step 4：构造 RL 状态

```text
(cpu, mem, qps, pod, μ, σ, risk)
```

---

### Step 5：DQN 决策

输出：

```text
scale in / maintain / scale out
```

---

### Step 6：执行扩缩容

调用：

```bash
kubectl scale deployment ...
```

---

# 5. 环境安装

---

## 安装依赖

```bash
pip install -r requirements.txt
```

---

# 6. 准备训练数据

创建：

```text
metrics.csv
```

格式：

```csv
cpu,memory,qps,latency
0.5,0.4,100,120
0.6,0.5,120,130
0.7,0.6,135,150
...
```

---

# 7. 参数配置

配置文件：

```text
config/config.yaml
```

示例：

```yaml
lstm:
  window_size: 20
  epochs: 50
  learning_rate: 0.001
  hidden_size: 64
  mc_dropout_samples: 20

reward:
  alpha: 1.0
  beta: 0.2
  gamma: 0.1
  eta: 0.05

dqn:
  learning_rate: 0.0001
  gamma: 0.98
  batch_size: 64
  buffer_size: 100000
  total_timesteps: 200000

controller:
  decision_interval: 30
  deployment_name: myapp
```

---

# 8. 实验运行流程

---

## Step 1：训练 LSTM

```bash
python predictor/train_lstm.py
```

生成：

```text
lstm_model.pt
```

---

## Step 2：训练 RL Agent

```bash
python rl/train_dqn.py
```

生成：

```text
dqn_agent.zip
```

---

## Step 3：启动在线控制器

```bash
python controller/autoscaling_controller.py
```

---

# 9. Kubernetes 部署要求

当前控制器通过：

```bash
kubectl scale deployment myapp --replicas=N
```

执行伸缩。

要求：

- 已部署 Kubernetes 集群；
- 已配置 kubectl；
- 已存在目标 Deployment；
- 推荐安装：

  - K3s
  - Prometheus
  - Metrics Server

---
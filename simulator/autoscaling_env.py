import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config.load_config import load_config


class AutoscalingEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # 读取配置
        cfg = load_config()

        self.alpha = cfg["reward"]["alpha"]
        self.beta = cfg["reward"]["beta"]
        self.gamma = cfg["reward"]["gamma"]
        self.eta = cfg["reward"]["eta"]

        # 动作空间：
        # 0 = scale in
        # 1 = maintain
        # 2 = scale out
        self.action_space = spaces.Discrete(3)

        # 状态空间：
        # [cpu, mem, qps, pod, mu, sigma, risk]
        self.observation_space = spaces.Box(
            low=0,
            high=1e6,
            shape=(7,),
            dtype=np.float32,
        )

        self.state = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # 初始状态
        self.state = np.array(
            [
                0.5,   # cpu
                0.4,   # mem
                100,   # qps
                2,     # pod replicas
                100,   # predicted mean
                5,     # predicted uncertainty
                0.05,  # risk
            ],
            dtype=np.float32,
        )

        return self.state, {}

    def step(self, action):
        cpu, mem, qps, pod, mu, sigma, risk = self.state

        # --------------------------------
        # 1. 执行动作
        # --------------------------------
        if action == 0:
            pod = max(1, pod - 1)

        elif action == 2:
            pod = pod + 1

        # --------------------------------
        # 2. 简化负载动态模拟
        # --------------------------------
        qps = qps + np.random.normal(0, 5)

        qps = max(10, qps)

        cpu = qps / (pod * 100)

        mem = min(1.0, cpu * 0.8)

        # --------------------------------
        # 3. 模拟预测结果
        # --------------------------------
        mu = qps + np.random.normal(0, 2)

        sigma = abs(
            np.random.normal(5, 1)
        )

        risk = sigma / mu

        # --------------------------------
        # 4. 延迟模型
        # --------------------------------
        latency = np.exp(
            min(cpu, 5)
        )

        # --------------------------------
        # 5. Reward函数
        #
        # R = -αD -βC -γO -ηRisk
        # --------------------------------
        reward = -(
            self.alpha * latency
            + self.beta * pod
            + self.gamma * (action != 1)
            + self.eta * risk
        )

        # --------------------------------
        # 6. 更新状态
        # --------------------------------
        self.state = np.array(
            [
                cpu,
                mem,
                qps,
                pod,
                mu,
                sigma,
                risk,
            ],
            dtype=np.float32,
        )

        terminated = False
        truncated = False

        return (
            self.state,
            reward,
            terminated,
            truncated,
            {},
        )
import time
import subprocess
import numpy as np

from stable_baselines3 import DQN

from predictor.predictor import MCPredictor
from config.load_config import load_config


def query_metrics():
    """
    这里后续替换成
    Prometheus API 查询
    """

    cpu = 0.5
    mem = 0.4
    qps = 120

    return cpu, mem, qps


def scale_k8s(action, deployment):
    """
    action:
    0 -> scale in
    1 -> maintain
    2 -> scale out
    """

    if action == 0:
        replicas = 1

    elif action == 1:
        replicas = 2

    else:
        replicas = 3

    cmd = [
        "kubectl",
        "scale",
        "deployment",
        deployment,
        f"--replicas={replicas}",
    ]

    print(
        "Executing:",
        " ".join(cmd)
    )

    subprocess.run(cmd)


def main():
    cfg = load_config()

    interval = cfg[
        "controller"
    ]["decision_interval"]

    deployment = cfg[
        "controller"
    ]["deployment_name"]

    # RL模型
    dqn_model = DQN.load(
        "dqn_agent"
    )

    # LSTM预测器
    predictor = MCPredictor()

    print(
        "Autoscaling controller started..."
    )

    while True:
        # ----------------------------
        # 1. 查询当前指标
        # ----------------------------
        cpu, mem, qps = query_metrics()

        # ----------------------------
        # 2. LSTM预测
        #
        # 这里先用简单假输入
        # 后续换真实时间窗
        # ----------------------------
        dummy_input = np.random.rand(
            1, 20, 4
        )

        import torch

        x = torch.tensor(
            dummy_input,
            dtype=torch.float32
        )

        mu, sigma = predictor.predict(
            x
        )

        risk = sigma / mu

        # ----------------------------
        # 3. 构造状态
        # ----------------------------
        state = np.array(
            [
                cpu,
                mem,
                qps,
                2,      # 当前副本数
                mu,
                sigma,
                risk,
            ],
            dtype=np.float32,
        )

        # ----------------------------
        # 4. RL决策
        # ----------------------------
        action, _ = dqn_model.predict(
            state,
            deterministic=True,
        )

        print(
            f"cpu={cpu:.3f}, "
            f"qps={qps}, "
            f"mu={mu:.2f}, "
            f"sigma={sigma:.2f}, "
            f"risk={risk:.4f}"
        )

        print(
            "Chosen action:",
            action
        )

        # ----------------------------
        # 5. 执行动作
        # ----------------------------
        scale_k8s(
            action,
            deployment
        )

        # ----------------------------
        # 6. 等待下一轮
        # ----------------------------
        time.sleep(
            interval
        )


if __name__ == "__main__":
    main()
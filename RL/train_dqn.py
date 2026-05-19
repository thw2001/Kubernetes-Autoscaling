from stable_baselines3 import DQN
from simulator.autoscaling_env import AutoscalingEnv
from config.load_config import load_config


def main():
    cfg = load_config()

    dqn_cfg = cfg["dqn"]

    env = AutoscalingEnv()

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=dqn_cfg[
            "learning_rate"
        ],
        gamma=dqn_cfg[
            "gamma"
        ],
        batch_size=dqn_cfg[
            "batch_size"
        ],
        buffer_size=dqn_cfg[
            "buffer_size"
        ],
        verbose=1,
    )

    print("Training DQN...")

    model.learn(
        total_timesteps=dqn_cfg[
            "total_timesteps"
        ]
    )

    model.save(
        "dqn_agent"
    )

    print(
        "Saved: dqn_agent.zip"
    )


if __name__ == "__main__":
    main()
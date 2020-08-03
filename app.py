from agent import Env5gAirSim
from argparse import ArgumentParser

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

parser = ArgumentParser()
parser.add_argument("-r", "--read", dest="read", required=True,
                    help="metrics csv to read", metavar="FILE")
parser.add_argument("-w", "--write", dest="write", required=True,
                    help="weight csv to write", metavar="FILE")

args = parser.parse_args()

env = DummyVecEnv([lambda: Env5gAirSim(args.read, args.write, debug=True)])
model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=20000)
obs = 180000

while True:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()

# env = Env5gAirSim(args.read, args.write, debug=True)

# while True:
#     env.step(180000)

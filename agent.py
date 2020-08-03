import gym
import numpy as np
import pandas as pd
import time
import random

from collections import deque
from io import StringIO

from gym import spaces

INITIAL_WEIGHT = 180000
INITIAL_LINES_READING = 100000

DF_HEADERS = [
    'subchannel',
    'allocation_counter',
    'applicationType',
    'HeadOfLinePacketDelay',
    'HeadOfLinePacketDelayIsNull',
    'targetDelay',
    'targetDelayIsNull',
    'avgHeadOfLineDelay',
    'spectralEfficiency',
    'avgTransmissionRate',
    'numerator',
    'numeratorIsNull',
    'denominator',
    'denominatorIsNull',
    'weight',
    'weightIsNull',
    'metric',
]

DF_NON_SEQUENTIAL_COLS = [
    'applicationType',
    'HeadOfLinePacketDelay',
    'HeadOfLinePacketDelayIsNull',
    'targetDelay',
    'targetDelayIsNull',
    'avgHeadOfLineDelay',
    'spectralEfficiency',
    'avgTransmissionRate',
    'numerator',
    'numeratorIsNull',
    'denominator',
    'denominatorIsNull',
    'weightIsNull',
]

class Env5gAirSim(gym.Env):
    def __init__(self, dataset_5g_filename, communication_5g_filename, debug=False):
        super(Env5gAirSim, self).__init__()

        self.dataset_5f_filename = dataset_5g_filename
        self.communication_5g_filename = communication_5g_filename
        self.debug = debug
        self.line_amount = INITIAL_LINES_READING
        self.line_amount_created_from_stats = False
        self.current_step = 0

        self.action_space = spaces.Box(
            low=0.00001, high=10000000, shape=(1,), dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0.0000001, 0.008, 0, 0, 0, 0, 0]),
            high=np.array([3, 0.1, 1, 0.1, 1, 0.1, 0.1, 1000000, 6, 1, 1.5, 1, 1]),
            dtype=np.float32
        )
        self.current_allocation_counter = -1

        action = INITIAL_WEIGHT

        with open(communication_5g_filename, "w") as text_file:
            print(f"0,{action}", file=text_file)
            print(f"1,{action}", file=text_file)

        self._read_csv()

    def _read_csv(self, sep=';', header=None):
        with open(self.dataset_5f_filename, 'r') as f:
            q = deque(f, self.line_amount)

        self.df = pd.read_csv(StringIO(''.join(q)),
                                sep=sep,
                                header=header,
                                names=DF_HEADERS
                             )

        self.max_allocation_counter = self.df['allocation_counter'].max()

        self.step_rows = self.df['allocation_counter'] == self.max_allocation_counter - 1

        if not self.line_amount_created_from_stats and len(self.df) > 0:
            self.line_amount_created_from_stats = True
            self.line_amount = len(self.df) * 5

    def _take_action(self, action):
        self.current_allocation_counter = self.max_allocation_counter - 1

        if self.debug:
            print('Writing')

        with open(self.communication_5g_filename, "a") as text_file:
            print(f"{self.current_allocation_counter+1},{action}", file=text_file)

    def _next_observation(self):
        return self.df.loc[self.step_rows, DF_NON_SEQUENTIAL_COLS].mean()

    def step(self, action):
        we_should_write = False

        while not we_should_write:
            self._read_csv()

            we_should_write = self.max_allocation_counter > self.current_allocation_counter + 1

            if not we_should_write:
                if self.debug:
                    print('Sleeping')

                time.sleep(0.005)

        self.current_step += 1
        self._take_action(action)

        done = False
        reward = random.uniform(0, 100)  # symbolic, while we don't receive rewards
        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
        return self._next_observation()

    def render(self, mode='human', close=False):
        print(f'Step: {self.current_step}')

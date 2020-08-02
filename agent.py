import gym
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

class Env5gAirSim(gym.Env):
    def __init__(self, dataset_5g_filename, communication_5g_filename, debug=False):
        super(Env5gAirSim, self).__init__()

        self.dataset_5f_filename = dataset_5g_filename
        self.communication_5g_filename = communication_5g_filename
        self.debug = debug
        self.line_amount = INITIAL_LINES_READING
        self.line_amount_created_from_stats = False

        self.action_space = None  # TBD
        self.observation_space = None  # TBD
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

        if not self.line_amount_created_from_stats:
            self.line_amount_created_from_stats = True
            self.line_amount = len(self.df) * 5

    def _take_action(self, action):
        self.current_allocation_counter = self.max_allocation_counter - 1

        if self.debug:
            print('Writing')

        with open(self.communication_5g_filename, "a") as text_file:
            print(f"{self.current_allocation_counter+1},{action}", file=text_file)

    def _next_observation(self):
        obs = None
        
        return obs

    def step(self, action):
        we_should_write = False

        while not we_should_write:
            self._read_csv()

            we_should_write = self.max_allocation_counter > self.current_allocation_counter + 1

            if not we_should_write:
                if self.debug:
                    print('Sleeping')

                time.sleep(0.005)

        self._take_action(action)

        # self.current_step += 1
        done = False
        reward = random.uniform(0, 100)  # symbolic, while we don't receive rewards
        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
        return self._next_observation()

    def render(self, mode='human', close=False):
        pass

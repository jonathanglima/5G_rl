from agent import Env5gAirSim
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-r", "--read", dest="read", required=True,
                    help="metrics csv to read", metavar="FILE")
parser.add_argument("-w", "--write", dest="write", required=True,
                    help="weight csv to write", metavar="FILE")

args = parser.parse_args()

env = Env5gAirSim(args.read, args.write, debug=True)

while True:
    env.step(180000)

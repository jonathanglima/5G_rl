import time
import pandas as pd

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-r", "--read", dest="read", required=True,
                    help="metrics csv to read", metavar="FILE")
parser.add_argument("-w", "--write", dest="write", required=True,
                    help="weight csv to write", metavar="FILE")

args = parser.parse_args()
curr_allocation_counter = -1

open(args.write, 'w').close()

with open(args.write, "a") as text_file:
    # print(f"Purchase Amount: {TotalAmount}", file=text_file)
    print(f"0,1800000", file=text_file)
    print(f"1,1800000", file=text_file)

while True:
    df = pd.read_csv(args.read, sep=';', header=None, names=[
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
    ])

    tmp_max_allocation_counter = df['allocation_counter'].max()

    should_we_write = tmp_max_allocation_counter > curr_allocation_counter + 1

    if not should_we_write:
        print("Sleeping")
        time.sleep(0.01)
        continue

    df = df[df['allocation_counter'] == tmp_max_allocation_counter-1]
    curr_allocation_counter = tmp_max_allocation_counter-1

    print("Writing")

    with open(args.write, "a") as text_file:
        # print(f"Purchase Amount: {TotalAmount}", file=text_file)
        print(f"{curr_allocation_counter+1},1800000", file=text_file)

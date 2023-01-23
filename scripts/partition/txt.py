# Copyright 2023 MosaicML Streaming authors
# SPDX-License-Identifier: Apache-2.0

"""Command-line tool to visualize StreamingDataset sample space partitioning."""

import math
import numpy as np
from numpy.typing import NDArray
from argparse import ArgumentParser, Namespace

from streaming.base.partitioning import get_partitions_fast, get_partitions_slow


def parse_args() -> Namespace:
    """Parse command-line arguments.

    Returns:
        Namespace: Command-line arguments.
    """
    args = ArgumentParser()
    args.add_argument('-v', '--version', type=str, default='fast')
    args.add_argument('-n', '--dataset_size', type=int, default=678)
    args.add_argument('-b', '--device_batch_size', type=int, default=7)
    args.add_argument('-o', '--offset_in_epoch', type=int, default=0)
    args.add_argument('-c', '--canonical_nodes', type=int, default=6)
    args.add_argument('-p', '--physical_nodes', type=int, default=3)
    args.add_argument('-d', '--node_devices', type=int, default=4)
    args.add_argument('-w', '--device_workers', type=int, default=5)
    return args.parse_args()


def show(ids: NDArray[np.int64]) -> None:
    max_id = ids.max()
    max_digits = math.ceil(math.log10(max_id + 1))
    for i, node in enumerate(ids):
        print(f'Node {i}')
        for j, device in enumerate(node):
            print(f'    Dev {j}')
            for k, worker in enumerate(device):
                table = []
                for batch in worker:
                    row = []
                    for sample in batch:
                        if 0 <= sample:
                            cell = str(sample)
                        else:
                            cell = '-'
                        cell = cell.rjust(max_digits)
                        row.append(cell)
                    row = ' '.join(row)
                    table.append(row)
                line = '  '.join(table)
                print(' ' * 12 + line)


def main(args: Namespace) -> None:
    """Generate and display a partitioning given command-line arguments.

    Args:
        args (Namespace): Command-line arguments.
    """
    version2get_partitions = {
        'fast': get_partitions_fast,
        'slow': get_partitions_slow,
    }

    get_partitions = version2get_partitions[args.version]
    ids = get_partitions(args.dataset_size, args.canonical_nodes, args.physical_nodes,
                         args.node_devices, args.device_workers, args.device_batch_size,
                         args.offset_in_epoch)
    ids = ids.reshape(args.physical_nodes, args.node_devices, args.device_workers, -1,
                      args.device_batch_size)
    show(ids)


if __name__ == '__main__':
    main(parse_args())

import os
from pyntcloud import PyntCloud
import numpy as np
from glob import glob


def partition(path, vg_size=1024, pc_size=128):
    print(path)
    pc = PyntCloud.from_file(path)
    coords = ['x', 'y', 'z']
    N = vg_size // pc_size
    for i in range(N):
        for j in range(N):
            for k in range(N):
                # print(i, j, k)
                points = pc.points[coords].values
                u_bound = np.repeat(np.asarray([[(i+1)*pc_size,(j+1)*pc_size,(k+1)*pc_size]]), points.shape[0], axis=0)
                l_bound = np.repeat(np.asarray([[i*pc_size,j*pc_size,k*pc_size]]), points.shape[0], axis=0)
                selection = ((points < u_bound).astype('float32') + (points > l_bound).astype('float32') == 2).all(axis=1)
                pcpc = pc.points[selection]
                if len(pcpc) > 0:
                    # print(pcpc[coords].values.max())
                    pcpc[coords] = pcpc[coords].values - np.repeat(np.asarray([[i*pc_size,j*pc_size,k*pc_size]]), pcpc.shape[0], axis=0)
                    # print(pcpc[coords].values.max())
                    cloud = PyntCloud(pcpc)
                    print('{}_{}_{}_{}.ply'.format(path[:-4], i, j, k))
                    cloud.to_file('{}_{}_{}_{}.ply'.format(path[:-4], i, j, k))


if __name__ == "__main__":

    pc_dir = 'D:\Downloads\PCL\Datasets\PointXR\PointXR dataset-15'
    seq_10 = glob(os.path.join(pc_dir, '**/*.ply'), recursive=True)
    partition(seq_10[0], vg_size=1024, pc_size=128)
    # if len(seq_10) > 0:
    #     for path in seq_10:
    #         partition(path, vg_size=1024, pc_size=128)

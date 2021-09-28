'''
Python wrapper to encode with MPEG G-PCC standard
Author: Haiqiang Wang
Date: 04/22/2021
Modified by Dingquan Li
Date: 09/28/2021
'''

import os
import re
from glob import glob
from argparse import ArgumentParser


def make_cfg(gpcc_bin_path, ref_path, cfg_dir, output_dir, g, c):

    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    _, file_name = os.path.split(ref_path)
    src_name = re.split('/|\.', file_name)[-2]
    recon_name = '{src}_g_{g}_c_{c}'.format(src=src_name, g=g, c=c)
    recon_path = os.path.join(output_dir, '{}.ply'.format(recon_name))
    bin_path = os.path.join(output_dir, '{}.bin'.format(recon_name))
    log_path = os.path.join(output_dir, '{}.log'.format(recon_name))
    cfg_path = os.path.join(cfg_dir, '{}.cfg'.format(recon_name))

    rst = []
    rst.append('mode: 0')
    rst.append('trisoupNodeSizeLog2: 0')
    rst.append('mergeDuplicatedPoints: 1')
    rst.append('neighbourAvailBoundaryLog2: 8')
    rst.append('intra_pred_max_node_size_log2: 6')
    rst.append('positionQuantizationScale: {}'.format(g))  #
    rst.append('maxNumQtBtBeforeOt: 4')
    rst.append('minQtbtSizeLog2: 0')
    rst.append('planarEnabled: 1')
    rst.append('planarModeIdcmUse: 0')
    rst.append('convertPlyColourspace: 1')
    rst.append('transformType: 2')
    rst.append('numberOfNearestNeighborsInPrediction: 3')
    rst.append('levelOfDetailCount: 12')
    rst.append('lodDecimator: 0')
    rst.append('adaptivePredictionThreshold: 64')
    rst.append('qp: {}'.format(c)) #
    rst.append('qpChromaOffset: 0')
    rst.append('bitdepth: 8')
    rst.append('attrOffset: 0')
    rst.append('attrScale: 1') 
    rst.append('attribute: color')
    rst.append('uncompressedDataPath: {}'.format(ref_path))
    rst.append('reconstructedDataPath: {}'.format(recon_path))
    rst.append('compressedStreamPath: {}'.format(bin_path))

    with open(cfg_path, 'w') as f:
        for line in rst:
            f.write("%s\n" % line)

    cmd = "\"{exec_path}\" --config=\"{cfg_path}\" >> \"{log_path}\"".format(exec_path=gpcc_bin_path, cfg_path=cfg_path, log_path=log_path)
    # print(cmd)

    return cmd


def process_one_depth(gpcc_bin_path, ref_dir, cfg_dir, output_dir, seq, g, c):
    cmd = []
    for _seq in seq:
        ref_path = os.path.join(ref_dir, _seq)
        for _g in g:
            for _c in c:
                _cmd = make_cfg(gpcc_bin_path, ref_path, cfg_dir, output_dir, _g, _c)
                cmd.append(_cmd)

    return cmd


if __name__ == "__main__":

    dir_path = os.path.dirname(os.path.realpath(__file__))
    gpcc_bin_path = os.path.abspath(os.path.join(dir_path, '../../mpeg-pcc-tmc13/build/tmc3/Release/tmc3.exe'))
    ref_dir = 'D:\Downloads\PCL\Datasets\pointcloud\PointXR\PointXR-dataset-15'
    cfg_dir = os.path.abspath(os.path.join(dir_path, '../../cfg'))
    codec = 'octree-liftt-ctc-lossy-geom-lossy-attrs'
    output_dir = 'D:\Downloads\PCL\Datasets\pointcloud\PointXR\PointXR-dataset-15'

    parser = ArgumentParser(description='G-PCC')
    parser.add_argument('--gpcc_bin_path', default=gpcc_bin_path, type=str,
                        help='')
    parser.add_argument('--ref_dir', default=ref_dir, type=str,
                        help='')
    parser.add_argument('--cfg_dir', default=cfg_dir, type=str,
                        help='')
    parser.add_argument('--codec', default=codec, type=str,
                        help='')
    parser.add_argument('--output_dir', default=os.path.join(output_dir, codec), type=str,
                        help='')
    args = parser.parse_args()

    
    # seq_15p = []
    # g_15p = [1.0/512, 1.0/256, 1.0/64, 1.0/32, 1.0/8, 1.0/4]

    # seq_14 = []
    # g_14 = [1.0/256, 1.0/128, 1.0/64, 1.0/16, 1.0/8, 1.0/4]

    # seq_13 = []
    # g_13 = [1.0/64, 1.0/32, 1.0/16, 1.0/8, 1.0/4, 1.0/2]

    # seq_12 = []
    # g_12 = [1.0/32, 1.0/16, 1.0/8, 1.0/4, 1.0/2, 3.0/4]

    # seq_11 = []
    # g_11 = [1.0/16, 1.0/8, 1.0/4, 1.0/2, 3.0/4, 7.0/8]

    seq_10 = glob(os.path.join(args.ref_dir, '*.ply'))
    g_10 = [1.0/8, 1.0/4, 1.0/2, 3.0/4, 7.0/8, 15.0/16] #

    
    c = [22, 28, 34, 40, 46, 51] #

    cmd_all = []
    # if len(seq_15p) > 0:
    #     cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_15p, g_15p, c)
    #     cmd_all.extend(cmd)
    
    # if len(seq_14) > 0:
    #     cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_14, g_14, c)
    #     cmd_all.extend(cmd)

    # if len(seq_13) > 0:
    #     cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_13, g_13, c)
    #     cmd_all.extend(cmd)

    # if len(seq_12) > 0:
    #     cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_12, g_12, c)
    #     cmd_all.extend(cmd)

    # if len(seq_11) > 0:
    #     cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_11, g_11, c)
    #     cmd_all.extend(cmd)
    
    print(len(seq_10))
    if len(seq_10) > 0:
        seq_10 = [os.path.split(path)[1] for path in seq_10]
        cmd = process_one_depth(args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_10, g_10, c)
        cmd_all.extend(cmd) 


    with open('run_{}_encode.sh'.format(args.codec), 'w') as f:
        f.write('#!/bin/bash \n')
        for item in cmd_all:
            # print(item)
            f.write('%s & \n' % item)

    with open('clear_{}_bin_and_log.sh'.format(args.codec), 'w') as f:
        f.write('#!/bin/bash \n')
        clear_cmd = "del \"{log_path}\" \"{bin_path}\"".format(log_path=os.path.join(args.output_dir, '*.log'), bin_path=os.path.join(args.output_dir, '*.bin'))
        f.write('%s \n' % clear_cmd)

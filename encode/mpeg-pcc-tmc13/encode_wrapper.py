'''
Python wrapper to encode with MPEG G-PCC standard
Author: Haiqiang Wang
Date: 04/22/2021
Modified by Dingquan Li
Date: 09/28/2021

python encode_wrapper.py --codec octree-liftt-ctc-lossless-geom-lossy-attrs
python encode_wrapper.py --codec octree-liftt-ctc-lossy-geom-lossy-attrs
python encode_wrapper.py --codec octree-predt-ctc-lossless-geom-lossless-attrs
python encode_wrapper.py --codec octree-predt-ctc-lossless-geom-nearlossless-attrs
python encode_wrapper.py --codec octree-raht-ctc-lossless-geom-lossy-attrs
python encode_wrapper.py --codec octree-raht-ctc-lossy-geom-lossy-attrs

python encode_wrapper.py --codec predgeom-liftt-ctc-lossless-geom-lossy-attrs
python encode_wrapper.py --codec predgeom-liftt-ctc-lossy-geom-lossy-attrs
python encode_wrapper.py --codec predgeom-predt-ctc-lossless-geom-lossless-attrs
python encode_wrapper.py --codec predgeom-predt-ctc-lossless-geom-nearlossless-attrs
python encode_wrapper.py --codec predgeom-raht-ctc-lossless-geom-lossy-attrs
python encode_wrapper.py --codec predgeom-raht-ctc-lossy-geom-lossy-attrs

# Options for Trisoup are much different from the other settings, which we currently not consider.
# inferredDirectCodingMode: 0
# trisoupNodeSizeLog2: 5 # r01-r04 -> 5,4,3,2
# qp: 40 # r01-r04 -> 40, 34, 28, 22
# positionQuantizationScale: # one specific value per PC
python encode_wrapper.py --codec trisoup-liftt-ctc-lossy-geom-lossy-attrs # TO BE ADDED
python encode_wrapper.py --codec trisoup-raht-ctc-lossy-geom-lossy-attrs # TO BE ADDED
'''

import os
import re
import math
import subprocess
import multiprocessing
from multiprocessing import Pool
import threading
from glob import glob
from argparse import ArgumentParser


def make_cfg(codec, gpcc_bin_path, ref_path, cfg_dir, output_dir, g, c):

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
    if 'lossy-geom' in codec:
        rst.append('mergeDuplicatedPoints: 1')
    else:
        rst.append('mergeDuplicatedPoints: 0')
    rst.append('neighbourAvailBoundaryLog2: 8')
    rst.append('intra_pred_max_node_size_log2: 6')
    rst.append('positionQuantizationScale: {}'.format(g))  #
    if g==1:
        rst.append('inferredDirectCodingMode: 1')
    rst.append('maxNumQtBtBeforeOt: 4')
    rst.append('minQtbtSizeLog2: 0')
    rst.append('planarEnabled: 1')
    rst.append('planarModeIdcmUse: 0')
    if 'nearlossless-attrs' in codec:
        rst.append('convertPlyColourspace: 0')
    else:
        rst.append('convertPlyColourspace: 1')
    if 'predt' in codec:
        rst.append('transformType: 1')
    elif 'liftt' in codec:
        rst.append('transformType: 2')
    else: # raht
        rst.append('transformType: 0')
    if 'predt' in codec:
        rst.append('numberOfNearestNeighborsInPrediction: 3')
        rst.append('levelOfDetailCount: 12')
        rst.append('intraLodPredictionSkipLayers: 0')
        if 'nearlossless-attrs' in codec:
            rst.append('interComponentPredictionEnabled: 1')
            rst.append('predWeightBlending: 1')
        else: # lossless-attrs
            rst.append('interComponentPredictionEnabled: 0')
        rst.append('adaptivePredictionThreshold: 64')
    if 'liftt' in codec:
        rst.append('numberOfNearestNeighborsInPrediction: 3')
        rst.append('levelOfDetailCount: 12')
        rst.append('lodDecimator: 0')
        rst.append('adaptivePredictionThreshold: 64')
    
    rst.append('qp: {}'.format(c)) #
    rst.append('qpChromaOffset: 0')
    rst.append('bitdepth: 8')
    rst.append('attrOffset: 0')
    rst.append('attrScale: 1') 
    if 'predt' in codec:
        if 'nearlossless-attrs' in codec:
            rst.append('colourMatrix: 0')
        else:
            rst.append('colourMatrix: 8')
    rst.append('attribute: color')
    if 'predgeom' in codec:
        rst.append('sortInputByAzimuth: 0')
        rst.append('geomTreeType: 1')
        rst.append('predGeomSort: 2')
        rst.append('predGeomAzimuthSortPrecision: 8')
    rst.append('uncompressedDataPath: {}'.format(ref_path))
    rst.append('reconstructedDataPath: {}'.format(recon_path))
    rst.append('compressedStreamPath: {}'.format(bin_path))

    with open(cfg_path, 'w') as f:
        for line in rst:
            f.write("%s\n" % line)

    cmd = "{exec_path} --config={cfg_path} >> {log_path}".format(exec_path=gpcc_bin_path, cfg_path=cfg_path, log_path=log_path)
    # print(cmd)

    return cmd


def process_one_depth(codec, gpcc_bin_path, ref_dir, cfg_dir, output_dir, seq, g, c):
    cmd = []
    for _seq in seq:
        ref_path = os.path.join(ref_dir, _seq)
        for _g in g:
            for _c in c:
                _cmd = make_cfg(codec, gpcc_bin_path, ref_path, cfg_dir, output_dir, _g, _c)
                cmd.append(_cmd)

    return cmd


def run_command(cmds):
    os.system(cmds)
#     for cmd in cmds:
#         os.system(cmd)
    
    
if __name__ == "__main__":

    dir_path = os.path.dirname(os.path.realpath(__file__))
    gpcc_bin_path = os.path.abspath(os.path.join(dir_path, '../../../mpeg-pcc-tmc13/build/tmc3/tmc3')) # '../../mpeg-pcc-tmc13/build/tmc3/Release/tmc3.exe'
    ref_dir = '/userhome/Codes/RankPCQA/PointXR15' # '/mnt/d/Downloads/PCL/Datasets/pointcloud/PointXR/PointXR-dataset-15' # 'D:\Downloads\PCL\Datasets\pointcloud\PointXR\PointXR-dataset-15'
    codec = 'octree-liftt-ctc-lossy-geom-lossy-attrs' #
    parser = ArgumentParser(description='G-PCC')
    parser.add_argument('--gpcc_bin_path', default=gpcc_bin_path, type=str,
                        help='')
    parser.add_argument('--ref_dir', default=ref_dir, type=str,
                        help='')
    parser.add_argument('--codec', default=codec, type=str,
                        help='octree-liftt-ctc-lossy-geom-lossy-attrs, \
                              octree-liftt-ctc-lossless-geom-lossy-attrs, \
                              octree-predt-ctc-lossless-geom-lossless-attrs, \
                              octree-predt-ctc-lossless-geom-nearlossless-attrs')
    parser.add_argument('--output_dir', default=ref_dir, type=str,
                        help='')
    args = parser.parse_args()
    args.output_dir = os.path.join(args.output_dir, args.codec)
    args.cfg_dir = os.path.join(args.output_dir, 'cfg')
    args.output_dir = os.path.join(args.output_dir, 'output')

    
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
    
    if 'lossless-geom' in args.codec:
        g_10 = [1]
        # g_11 = [1]
        # g_12 = [1]
        # g_13 = [1]
        # g_14 = [1]
        # g_15 = [1]

    if 'lossy-attrs' in args.codec:
        c = [22, 28, 34, 40, 46, 51] #
    elif 'nearlossless-attrs' in args.codec:
        c = [10, 16, 22, 28, 34]
    else: # lossless-attrs
        c = [4]
    print(g_10, c)

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
        cmd = process_one_depth(args.codec, args.gpcc_bin_path, args.ref_dir, args.cfg_dir, args.output_dir, seq_10, g_10, c)
        cmd_all.extend(cmd) 


#     with open('run_{}_encode.sh'.format(args.codec), 'w') as f:
#         f.write('#!/bin/bash \n')
# #         threads = []
#         m = 36
#         for i, item in enumerate(cmd_all):
#             # print(item)
#             if i % m == m-1:
#                 f.write('%s \n' % item)
#             else:
#                 f.write('%s & \n' % item)
# #             th = threading.Thread(target=run_command, args=(item, ))
# #             th.start()
# #             threads.append(th)
        
# #         for th in threads:
# #             th.join()
            

#     with open('clear_{}_bin_and_log.sh'.format(args.codec), 'w') as f:
#         f.write('#!/bin/bash \n')
#         clear_cmd = "find {} -type f ! -name '*.ply' -delete".format(args.output_dir)
#         f.write('%s \n' % clear_cmd)
    
    m = 36 if len(cmd_all)>36 else len(cmd_all)
    n = int(math.ceil(len(cmd_all)/m))
    print(m, n)
    pool = Pool(m)
    pool.map(func=run_command, iterable=cmd_all, chunksize=n)
#     results = []
#     for i in range(0, len(cmd_all), n):
#         results.append(pool.apply_async(run_command, (cmd_all[i:i+n], )))
    pool.close()
    pool.join()
    
    clear_cmd = "find {} -type f ! -name '*.ply' -delete".format(args.output_dir)
    os.system(clear_cmd)
            
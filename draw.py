import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2

import h5py
import numpy as np
import os
import copy
import operator

def check_dir(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            print('Create directory :\n' + d)
            os.makedirs(d)

def gen_path(data_dir):
    path_dir = os.path.join(data_dir, 'Final_Path/')
    path = os.listdir(path_dir)
    path.sort()

    position_path = os.path.join(data_dir,"position.txt")

    with open(position_path) as position:
        position_info = position.readlines()

    lines = len(position_info)

    print("lines = ", lines)

    # Dikruangi dua soale position.txt mulaine dari 1 sampe 98 (aslinya 0 sampe 99)
    for frame_id in range(len(path)-2):
        nama_file = str(frame_id).zfill(4)

        # Read the path trajectory
        with h5py.File(path_dir+nama_file+'.h5','r') as ra:
            final_path = ra['final_path'].value
            check_pos = ra['check_pos'].value
            range_const = ra['range_const'].value
            list_save = ra['list_save'].value
            tengah = ra['tengah'].value

        # Read the ego movement
        info = position_info[frame_id].strip().split()

        ego_x = info[1]
        ego_y = info[2]

        print("ego_x = ", ego_x)
        print("ego_y = ", ego_y)
        print("final_path = ", final_path)

        lebar = list_save

        print("lebar = ", lebar)

        row = len(final_path)
        col = len(final_path[0])

        flag_y = 0
        simpan_x = []
        simpan_y = []
        for i in range(row, 0, -1):
            if i == row:
                weightedy = 3
            elif i == row-1:
                weightedy = 13
            elif i == row-2:
                weightedy = 16

            if flag_y == 0:
                for j in range(0, col):
                    # add weighted
                    if j == tengah-3:
                        weighted = -10.5
                    elif j == tengah-2:
                        weighted = -7
                    elif j == tengah-1:
                        weighted = -3.5
                    elif j == tengah:
                        weighted = 0
                    elif j == tengah+1:
                        weighted = 3.5
                    elif j == tengah+2:
                        weighted = 7
                    elif j == tengah+3:
                        weighted = 10.5

                    if final_path[i, j] == 1:
                        ano_x = ego_x + weighted
                        ano_y = ego_y + weightedy
                        simpan_x.append(ano_x)
                        simpan_y.append(ano_y)
                        flag_y += 1

            elif flag_y != 0:
                continue



        print("")

if __name__ == '__main__':
    data_dir = "/media/ferdyan/LocalDiskE/Hasil/dataset/New/X_ooc14/"
    gen_path(data_dir)

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

import matplotlib.pyplot as plt

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

    save = os.path.join(data_dir, 'pseudo_trajectory.txt')
    position_pseudo = open(save, 'w+')

    # Untuk gambar di matplotlib
    gambar_ego_x = []
    gambar_ego_y = []
    gambar_pseu_x = {}
    gambar_pseu_y = {}

    adder = 0
    tanda = 0

    # Dikruangi dua soale position.txt mulaine dari 1 sampe 98 (aslinya 0 sampe 99)
    for frame_id in range(len(path)-2):
        nama_file = str(frame_id).zfill(4)

        print("frame = ", nama_file)

        # Read the path trajectory
        with h5py.File(path_dir+nama_file+'.h5','r') as ra:
            final_path = ra['final_path'].value
            check_pos = ra['check_pos'].value
            range_const = ra['range_const'].value
            list_save = ra['list_save'].value
            tengah = ra['tengah'].value

        # Read the ego movement
        info = position_info[frame_id].strip().split()

        nomor_frame = info[0]
        ego_x = float(info[1])
        ego_y = float(info[2])

        tulis_1 = info[0] + " " + info[1] + " " +info[2] + " "
        position_pseudo.write(tulis_1)

        print("ego_x = ", ego_x)
        print("ego_y = ", ego_y)
        print("final_path = ", final_path)

        # Untuk gambar ego di matplotlib
        gambar_ego_x.append(ego_x)
        gambar_ego_y.append(ego_y)

        lebar = list_save

        row = len(final_path)
        col = len(final_path[0])

        flag_y = 0
        simpan_x = []
        simpan_y = []
        simpan_id = []
        kesamaan = np.zeros(lebar)

        for i in range(row-1, 0, -1):
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

                    # Check same id
                    # Kalau == 0 --> objek sama --> kasih tanda 1
                    # Kalau != 0 --> objek beda --> kasih tanda 0
                    if frame_id != 0:
                        if final_path[i, j] == check_lama[i, j] and final_path[i, j] == 1:
                            kesamaan[j] = -1
                            tanda = 1
                        else:
                            tanda = 0
                    elif frame_id == 0:
                        kesamaan[j] = final_path[i, j]

                    if final_path[i, j] == 1:
                        ano_x = ego_x + weighted
                        ano_y = ego_y + weightedy
                        simpan_x.append(ano_x)
                        simpan_y.append(ano_y)
                        simpan_id.append(tanda)
                        flag_y += 1

            elif flag_y != 0:
                continue

        print("kesamaan = ", kesamaan)
        print("simpan_x = ", simpan_x)
        print("simpan_y = ", simpan_y)
        print("simpan_id = ", simpan_id)
        print("")

        # Save the peudo position
        default_id = 0
        ngehe = []

        for b in range(len(simpan_x)):



            tanda = simpan_id[b]
            # 1 --> sama
            # 0 --> beda
            if frame_id == 0:
                id_objek = default_id + b
                for t in range(len(kesamaan)):
                    if kesamaan[t] == 1:
                        kesamaan[t] = id_objek
            else:
                if tanda == 1:
                    # objek sama
                    for t in range(len(kesamaan_old)):
                        if kesamaan_old[t] != 0:
                            ngehe.append(t)
                else:
                    # objek beda
                    print("objek beda")
                    id_objek = default_id + b + adder


            if frame_id == 0:
                id_objek = default_id + b
                for t in range(len(kesamaan)):
                    if kesamaan[t] == 1:
                        kesamaan[t] = id_objek
            else:
                




            
            pseudo_x = simpan_x[b]
            pseudo_y = simpan_y[b]

            print("pseudo_x = ", pseudo_x)
            print("pseudo_y = ", pseudo_y)
            print("id_objek = ", id_objek)
            print("kesamaan = ", kesamaan)

            # Untuk gambar pseudo car di matplotlib
            if id_objek in gambar_pseu_x:
                gambar_pseu_x[id_objek].append(pseudo_x)
                gambar_pseu_y[id_objek].append(pseudo_y)
            else:
                gambar_pseu_x[id_objek] = [pseudo_x]
                gambar_pseu_y[id_objek] = [pseudo_y]

            tulis_2 = str(id_objek) + " " + str(pseudo_x) + " " + str(pseudo_y) + " "
            position_pseudo.write(tulis_2)
            kesamaan_old = kesamaan.copy()
            print("")
            
        adder += 2

        position_pseudo.write("\n")
        check_lama = final_path.copy()
        print("")

    position_pseudo.close()

    plt.figure(figsize = (12.8,12.8))
    plt.title("Pseudo Car Trajectory Path", fontsize = 30)
    plt.xlabel("X(m)",fontsize = 20)
    plt.ylabel("Y(m)",fontsize = 20)
    plt.xlim(-100,100)

    plt.plot(gambar_ego_x,gambar_ego_y,label = "Ego-motion",color='green',linewidth = 3)

    all_colors = ['b', 'r', 'm', 'y', 'k', 'w']

    print("gambar_pseu_y = ", gambar_pseu_y)

    for i,id in enumerate(gambar_pseu_x):
        plt.plot(gambar_pseu_x[id],gambar_pseu_y[id],label = id, color=all_colors[id], linewidth = 2)

    plt.legend(loc = "lower left")
    plt.savefig(os.path.join(data_dir, "pseudo_path.png"))

if __name__ == '__main__':
    data_dir = "/media/ferdyan/LocalDiskE/Hasil/dataset/New/X_ooc14/"
    gen_path(data_dir)

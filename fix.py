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

    konter_id = 2

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
        print("final_path = \n", final_path)

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
        kesamaan_x = np.zeros(lebar)
        kesamaan_y = np.zeros(lebar)
        kesamaan_id = np.zeros(lebar)

        if frame_id == 0:
            kesamaan_id_lama = np.zeros(lebar)

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
                            ano_x = ego_x + weighted
                            ano_y = ego_y + weightedy
                            kesamaan_x[j] = ano_x
                            kesamaan_y[j] = ano_y
                        else:
                            tanda = 0
                    elif frame_id == 0:
                        if final_path[i, j] == 1:
                            kesamaan[j] = final_path[i, j]
                            ano_x = ego_x + weighted
                            ano_y = ego_y + weightedy
                            kesamaan_x[j] = ano_x
                            kesamaan_y[j] = ano_y

                    if final_path[i, j] == 1:
                        simpan_x.append(ano_x)
                        simpan_y.append(ano_y)
                        simpan_id.append(tanda)

                        flag_y += 1

            elif flag_y != 0:
                continue

        print("kesamaan = ", kesamaan)
        print("kesamaan_x = ", kesamaan_x)
        print("kesamaan_y = ", kesamaan_y)
        print("kesamaan = ", kesamaan)
        print("kesamaan_id_lama = ", kesamaan_id_lama)

        # Buat objek ID
        if frame_id == 0:
            konter_ids = 1
            for q in range(len(kesamaan)):
                if kesamaan[q] == 1:
                    kesamaan_id[q] = konter_ids
                    konter_ids += 1
        elif frame_id != 0:
            for q in range(len(kesamaan_x)):
                # Check kalo objeknya sama
                if kesamaan[q] != 0 and kesamaan_id_lama[q] != 0:
                    kesamaan_id[q] = kesamaan_id_lama[q]
                # Check kalo objeknya berubah
                if kesamaan[q] != 0 and kesamaan_id_lama[q] == 0:
                    kesamaan_id[q] = konter_ids
                    konter_ids += 1

        print("kesamaan_id = ", kesamaan_id)

        # Untuk draw
        for w in range(len(kesamaan_id)):
            if kesamaan_id[w] != 0:
                pseudo_x = kesamaan_x[w]
                pseudo_y = kesamaan_y[w]
                id_objek = kesamaan_id[w]

                if id_objek in gambar_pseu_x:
                    gambar_pseu_x[id_objek].append(float(pseudo_x))
                    gambar_pseu_y[id_objek].append(float(pseudo_y))
                else:
                    gambar_pseu_x[id_objek] = [float(pseudo_x)]
                    gambar_pseu_y[id_objek] = [float(pseudo_y)]

                tulis_2 = str(id_objek) + " " + str(pseudo_x) + " " + str(pseudo_y) + " "
                position_pseudo.write(tulis_2)

        position_pseudo.write("\n")
        check_lama = final_path.copy()
        kesamaan_id_lama = kesamaan_id.copy()
        print("")
        print("")

    position_pseudo.close()

    plt.figure(figsize = (12.8,12.8))
    plt.title("Pseudo Car Trajectory Path", fontsize = 30)
    plt.xlabel("X(m)",fontsize = 20)
    plt.ylabel("Y(m)",fontsize = 20)
    plt.xlim(-100,100)

    plt.plot(gambar_ego_x,gambar_ego_y,label = "Ego-motion",color='green',linewidth = 3)

    all_colors = ['blue', 'blue', 'red', 'magenta', 'yellow', 'k', 'w', 'b']

    print("gambar_pseu_y = ", gambar_pseu_y)

    print(set([ type(x) for x in all_colors ]))

    for i,id in enumerate(gambar_pseu_x):
        print("id = ", id)
        print("x = ", type(gambar_pseu_x[id]))
        print("y = ", type(gambar_pseu_y[id]))
        #print("color = ", type(all_colors[id]))

        plt.plot(gambar_pseu_x[id],gambar_pseu_y[id],label = id, color='blue', linewidth = 2)

    plt.legend(loc = "lower left")
    plt.savefig(os.path.join(data_dir, "pseudo_path.png"))
        

if __name__ == '__main__':
    data_dir = "H:\sabtu\X_ooc14"
    gen_path(data_dir)

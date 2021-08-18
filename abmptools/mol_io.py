import sys
import os
scrdir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(scrdir)

from multiprocessing import Pool
import copy
import random
import numpy as np
import math
import re
import subprocess
from ctypes import *


class mol_io():

    def __init__(self):
        # print('## load mol io')
        return

    def read_mol_name(self, fname):
        molname, ext = os.path.splitext(fname)
        # lines = [l.rstrip() for l in open(filename, "U")]
        # text = lines[1]
        # molname = re.sub(' {1,}', '', text).split('@@')
        # molname = molname[1]
        return molname

    def read_xyz(self, filename):
        lines = [l.rstrip() for l in open(filename, "U")]
        atom = []
        coord = []
        for l in range(2, len(lines)):
            temp = []
            temp.append(re.sub(' {1,}', ' ', lines[l]).split())
            atom.append(temp[0][0])
            temp[0].pop(0)
            temp2 = []
            for ll in range(len(temp[0])):
                temp2.append(float(temp[0][ll]))
            coord.append(temp2)
        return [atom, coord]

    def getatoms(self, fname):
        f = open(fname, "r", newline="\n")
        text = f.readlines()

        atom = []
        pos = []

        atoms = []
        atomnums = []
        poss = []
        skipflag = False
        for i in range(len(text)):
            if skipflag:
                skipflag = False
                continue

            itemList = text[i][:-1].split()
            if len(itemList) == 1:
                if i != 0:
                    atoms.append(atom)
                    poss.append(pos)
                    atomnums.append(atomnum)
                    atom = []
                    pos = []

                atomnum = itemList[0]
                skipflag = True
            else:
                atom.append([i-1, itemList[0]])
                pos.append(itemList[1:4])
            if i == (len(text) -1):
                atoms.append(atom)
                poss.append(pos)
                atomnums.append(atomnum)


        return atoms, atomnums, poss

    def convert_xyzs_pdb(self, fname, dirname, tgtnum=0):
        atoms, atomnums, poss = self.getatoms(fname)
        head, ext = os.path.splitext(fname)
        for i in range(len(atoms)):
            oname = dirname + '/' + str(i+1).zfill(5) + ".pdb"
            # print(atoms[i])
            # print(atomnums[i])
            # print(poss[i])
            if tgtnum != 0:
                if i+1 == tgtnum:
                    print(oname)
                    self.Exportpospdb(atoms[i], atomnums[i], poss[i], oname)
            else:
                    print(oname)
                    self.Exportpospdb(atoms[i], atomnums[i], poss[i], oname)

    def getatom(self, fname):
        atom = []
        pos = []
        f = open(fname, "r", newline="\n")
        text = f.readlines()
        for i in range(len(text)):
            itemList = text[i][:-1].split()
            if i == 0:
                atomnum = itemList[0]
                # print(fname, atomnum)
            if i >= 2:
                atom.append([i-2, itemList[0]])
                pos.append(itemList[1:4])
        return atom, atomnum, pos

    def convert_xyz_pdb(self, fname):
        atom, atomnum, pos = self.getatom(fname)
        head, ext = os.path.splitext(fname)
        oname = str(head) + ".pdb"
        self.Exportpospdb(atom, atomnum, pos, oname)

    def Exportpospdb(self, atom, atomnum, pos, out_file):
        # # Export position of mol
        # head, ext = os.path.splitext(str(iname))

        # header
        # print(out_file)
        f = open(out_file, "w", newline = "\n")
        print("COMPND    " + out_file, file=f)
        print("AUTHOR    " + "GENERATED BY python script in FCEWS", file=f)
        f.close()

        # aaa = [0.8855]
        # print '{0[0]:.3f}'.format(aaa)
        # print pos[0]
        f = open(out_file, "a+", newline = "\n")
        for i in range(len(pos)):
            for j in range(3):
                pos[i][j] = float(pos[i][j])

        # print pos[0]

        for i in range(len(atom)):
            l1_head='HETATM'
            l2_lab=str(i+1)
            l3_atom=atom[i][1]
            l3atom2="  "
            l4_alt=" "
            l5_res="UNK"
            l6_chain=" "
            l7_labres="  "
            l8_code=" "
            l9_x='{:.3f}'.format(pos[i][0])
            l10_y='{:.3f}'.format(pos[i][1])
            l11_z='{:.3f}'.format(pos[i][2])
            l12_occ='1.00'
            l13_temp="0.00"
            l14_ele=atom[i][1]
            l15_cha='  '
            list = [l1_head, l2_lab, l3_atom, l3atom2, l4_alt, l5_res, l6_chain, l7_labres,  l8_code, l9_x, l10_y, l11_z, l12_occ, l13_temp, l14_ele, l15_cha]
            print('{0[0]:<6}{0[1]:>5} {0[2]:>2}{0[3]:<2}{0[4]:>1}{0[5]:>3} {0[6]:>1}{0[7]:>4}{0[8]:>1}   {0[9]:>8}{0[10]:>8}{0[11]:>8}{0[12]:>6}{0[13]:>6}          {0[14]:>2}{0[15]:>2}'.format(list), file=f)
        # ATOM      1  H   UNK     1     -12.899  32.293   3.964  1.00  0.00           H
        print("END", file=f)

#1 1 – 6  HETATM
#2 7 – 11 原子の通し番号
# blank 1
#3 13 – 16    原子名
#4 17  Alternate location識別子
#5 18 - 20 残基名
# blank 1
#6 22  鎖名
#7 23 - 26 残基番号
#8 27  残基の挿入コード
# blank 3
#9 31 - 38 原子のX座標の値（Å単位）
#10 39 - 46 原子のY座標の値（Å単位）
#11 47 - 54 原子のZ座標の値（Å単位）
#12 55 - 60 占有率
#13 61 - 66 温度因子
#14 77 - 78 元素記号
#15 79 - 80 原子の電荷



import numpy as np
import sys
import os
import math
import subprocess
import re
import time
import copy
import abmptools as ampt
import collections
import argparse
# Matrix operation


if __name__ == "__main__":
    ## -- user setting --
    parser = argparse.ArgumentParser(
                prog='addsolvfrag.py', # program name
                usage='''e.g.)
                python addsolvfrag.py -temp 6lu7-covneu-nowat-hinagata0514.ajf -solv HOH WAT NA -i *.pdb
                ''', # program usage
                description='description',
                epilog='end',
                add_help=True,
                )

    # add args
    parser.add_argument('-i', '--input',
                        help='input frag info',
                        nargs='*',
                        # action='append',
                        required=True)

    parser.add_argument('-temp', '--template',
                        help='template file',
                        required=True)

    parser.add_argument('-solv', '--solvmol',
                        help='output config file',
                        nargs='*',
                        default=['HOH', 'WAT', 'NA'])

    parser.add_argument('-nocpf', '--nocpf',
                        help='cpfflag',
                        action='store_false'
                        )

    parser.add_argument('-cmm', '--cmm',
                        help='cmm',
                        action='store_true'
                        )

    args = parser.parse_args()
    print('input =', args.input)
    # print('output =', args.output)

    ajfname = args.template
    solvname = args.solvmol

    ## -- setting end --
    # read info
    mode = 'resnum' #rfile, resnum
    assignmolname = False
    refreshatmtype = False
    refreshresid = False

    aobj = ampt.setfmo()
    aobj.getmode = mode
    aobj.assignmolname = assignmolname
    aobj.refreshatmtype = refreshatmtype
    aobj.refreshresid = refreshresid
    aobj.cpfflag = args.nocpf
    aobj.cmmflag = args.cmm

    # main
    pdbnames = []
    for argv in sys.argv:
        if os.path.splitext(argv)[-1] == '.pdb':
            pdbnames.append(argv)

    for pdbname in pdbnames:

        print('infile:', pdbname)
        print('inajf', ajfname)

        # get pdbinfo
#         totalMol, atomnameMol, self.resnames, anummols, posMol, heads, labs, chains ,resnums ,codes ,occs ,temps ,amarks ,charges = aobj.getpdbinfowrap(pdbname)
        aobj = aobj.getpdbinfowrap(pdbname)

        # get tgt solvate mol info
        molname = solvname
        atomnumsets = []
        tgtmolsets = []
        for i in range(len(molname)):
            for j in range(aobj.totalRes):
            # for j in range(1):
                # print (molname[i], molnamelist_orig[j])
                if molname[i] == aobj.resnames[j]:
                    atomnumsets.append(len(aobj.posRes[j]))
                    tgtmolsets.append(aobj.resnames[j])
                    break
        print ('atomnumsets', atomnumsets)
        print('tgtmolsets', tgtmolsets)

        # get ajfinfo
        # fatomnumsets, fchgs, fbaas, fatminfos, connects = aobj.getajfinfo(ajfname)
        # get fraginfo
        aobj.getfragdict([ajfname], 'segment_data.dat')

        nameidMol = []
        for i in range(len(aobj.resnames)):
            for j in range(len(tgtmolsets)):
                if aobj.resnames[i] == tgtmolsets[j]:
                    nameidMol.append(j)
        # print(nameidMol)

        # add solute info
        tgtmolsets.append(os.path.splitext(ajfname)[0].split('/')[-1])
        nameidMol.insert(0, len(tgtmolsets)-1)
        atomnumsets.append(0)

        # fatomnums, fchgs, fbaas, fatminfos, connects = aobj.getfragtable(tgtmolsets, atomnumsets, nameidMol)
        aobj = aobj.getfragtable(tgtmolsets, atomnumsets, nameidMol)
        # print (frag_atoms, frag_charges)

        # gen ajf file
        aobj.ajf_method = "MP2"
        aobj.ajf_basis_set = "6-31G*"
        aobj.abinit_ver = 'rev15'
        aobj.piedaflag = True
        aobj.npro = 1
        aobj.para_job = 1
        ohead = os.path.splitext(pdbname)[0].split('/')[-1] + '_forabmp'
        aobj.readgeom = ohead + '.pdb'
        aobj.writegeom = os.path.splitext(pdbname)[0].split('/')[-1] + '-' + aobj.ajf_method + '-' + aobj.ajf_basis_set.replace('*', 'd') + ".cpf'"

        opath = 'for_abmp'
        if os.path.exists(opath) is False:
            print(opath)
            subprocess.call(["mkdir", opath])

        ajf_oname = opath + '/' + ohead + '.ajf'
        aobj.saveajf(ajf_oname)

        # exportpdb
        index = [i for i in range(len(aobj.posRes))]
        aobj.exportardpdbfull(opath + '/' + ohead, index)



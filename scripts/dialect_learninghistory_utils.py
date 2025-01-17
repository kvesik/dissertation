import io
import os
import pandas as pd
import re
import statistics
from itertools import product

HISTORYFILES = [
    # "../sim_outs/20240507_GLA_outputs/T_M100_sg20_Fi894_python_OTSoft-PDDP-Fin_GLA/Fi894 - OTSoft-PDDP-Fin_GLA_HISTORY5000.txt",
    "../sim_outs/20240507_GLA_outputs/T_Mgen4.100.100fs_mg2_fs_sg20_Fi894_python_OTSoft-PDDP-Fin_GLA/Fi894 - OTSoft-PDDP-Fin_GLA_HISTORY5000.txt",
    "../sim_outs/20240507_GLA_outputs/T_Mgen4.100.100fs_mg2_fs_sg20_NE894_python_OTSoft-PDDP-NEst_GLA/NE894 - OTSoft-PDDP-NEst_GLA_HISTORY5000.txt",
    "../sim_outs/20240507_GLA_outputs/T_Mgen4.100.100fs_mg2_fs_sg20_NS894_python_OTSoft-PDDP-NSeto_GLA/NS894 - OTSoft-PDDP-NSeto_GLA_HISTORY5000.txt",
    # "../sim_outs/20240507_GLA_outputs/T_M100_sg20_NS894_python_OTSoft-PDDP-NSeto_GLA/NS894 - OTSoft-PDDP-NSeto_GLA_HISTORY5000.txt",
    # "K407p - OT_Soft_KE_iFBfb_forGLA_cat_starBQP2cons_no2xcounts_HISTORY50000.txt",
    # "../sim_outs/20240507_GLA_outputs/T_M100_sg20_NE894_python_OTSoft-PDDP-NEst_GLA/NE894 - OTSoft-PDDP-NEst_GLA_HISTORY5000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg1_gr_sg20_Fi993_python_OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn/Fi993 - OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg3_gr_sg20_Fi993_python_OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn/Fi993 - OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTgr_sg20_NE993_python_OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn/NE993 - OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg1_gr_sg20_NE993_python_OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn/NE993 - OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg3_gr_sg20_NE993_python_OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn/NE993 - OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTgr_sg20_NS993_python_OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn/NS993 - OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg1_gr_sg20_NS993_python_OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn/NS993 - OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "../sim_outs/20240119_GLA_outputs/NTmg3_gr_sg20_NS993_python_OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn/NS993 - OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn_HISTORY1000.txt",
    # "sim_outs/20240104_Magri_outputs/Fi153_python_OTSoft-PDDP-Fin_GLA/Fi153 - OTSoft-PDDP-Fin_GLA_HISTORY1000.txt",
    # "sim_outs/20240104_Magri_outputs/NE153_python_OTSoft-PDDP-NEst_GLA/NE153 - OTSoft-PDDP-NEst_GLA_HISTORY1000.txt"
]


def main():

    stackedformat = True
    # convert history files to transposed, sorted format for tracking re-ranking per error
    if stackedformat:
        for hpath in HISTORYFILES:
            outputpath = hpath.replace(" - ", "_").replace(".txt", "_horiztraj.xls")
            convert_historyfile_horiztraj(hpath, outputpath)

    rformat = False
    # convert history files to R-friendly format
    if rformat:  
        for hpath in HISTORYFILES:
            outputpath = hpath.replace(" - ", "_").replace(".txt", "_forR.txt")
            convert_historyfile_forR(hpath, outputpath)


def convert_historyfile_horiztraj(sourcepath, destpath):
    pairsofcolumnstowrite = []
    with io.open(sourcepath, "r") as src:
        # read constraint names from header and adapt/store them for repeated use in constructing the transposed dataframe
        ln1 = src.readline()
        firstlinevalues = ln1.rstrip("\n").split("\t")
        labels = [label for label in firstlinevalues if label != "now"]
        constraints = labels[3:]

        ln2 = src.readline()
        secondlinevalues = [val for val in ln2.rstrip("\n").split("\t") if val]
        running_values = [float(val) for val in secondlinevalues]

        ln = src.readline()
        trialnum = "0"
        generated = ""
        heard = ""
        while ln != "":
            ln_list = ln.rstrip("\n").split("\t")
            if ln_list[0] != trialnum:  # we're moving on to a new trial
                # add the current running values to the main trajectory list
                cons_and_vals = list(zip(constraints, running_values))
                cons_and_vals.sort(key=lambda x: x[1], reverse=True)
                cons_and_vals = [('trialnum', trialnum), ('Generated', generated), ('Heard', heard)] + cons_and_vals
                pairsofcolumnstowrite.append(cons_and_vals)

                # start a new trial
                trialnum = ln_list[0]
                generated = ln_list[1]
                heard = ln_list[2]

            # else:  # we're continuing to update the current trial; don't add to the main trajectory list yet

            # either way, update the running values
            updates = [float(update) for update in get_updates(ln_list)]
            running_values = [running + update for running, update in zip(running_values, updates)]

            ln = src.readline()

    with io.open(destpath, "w") as dest:
        for pair_idx in range(len(pairsofcolumnstowrite[0])):
            listofpairstowrite = [colpair[pair_idx] for colpair in pairsofcolumnstowrite]
            flattened = [simplify_numstring(item) for pair in listofpairstowrite for item in pair]
            dest.write("\t".join(flattened) + "\n")


def simplify_numstring(num):
    numstring = str(num)
    if re.match('\.0+$', numstring):
        numstring = numstring[:numstring.index(".0")]
    return numstring


def get_updates(listfromrow):
    # trialnum = listfromrow[0]
    # generated = listfromrow[1]
    # heard = listfromrow[2]
    updateindices = range(3, len(listfromrow), 2)
    updates = [listfromrow[i] or "0" for i in updateindices]
    return updates


def convert_historyfile_forR(sourcepath, destpath):
    replacementpairs = {
        # "õ":"7",
        # "trial num":"trialnum",
        "*":"star_",
        "(":"",
        ")":""
    }
    with io.open(sourcepath, "r") as src:
        with io.open(destpath, "w", encoding='utf-8') as dest:

            sline = src.readline()

            while len(sline) != 0:
                if "TOTAL" not in sline:
                    dline = sline
                    for target in replacementpairs.keys():
                        dline = dline.replace(target, replacementpairs[target])
                    dest.write(dline)
                sline = src.readline()


if __name__ == "__main__":
    main()

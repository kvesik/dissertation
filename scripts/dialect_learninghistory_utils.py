import io
import os
import pandas as pd
import re
import statistics
from itertools import product

HISTORYFILES = [
    # "K407p - OT_Soft_KE_iFBfb_forGLA_cat_starBQP2cons_no2xcounts_HISTORY50000.txt",
    "sim_outs/20240104_Magri_outputs/Fi153_python_OTSoft-PDDP-Fin_GLA/Fi153 - OTSoft-PDDP-Fin_GLA_HISTORY1000.txt",
    "sim_outs/20240104_Magri_outputs/NE153_python_OTSoft-PDDP-NEst_GLA/NE153 - OTSoft-PDDP-NEst_GLA_HISTORY1000.txt"
]


def convert_historyfile(sourcepath, destpath):
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


def main():
    for hfile in HISTORYFILES:
        hpath = os.path.join("..", hfile)
        outputfile = hpath.replace(" - ", "_").replace(".txt", "_forR.txt")

        convert_historyfile(hpath, outputfile)


if __name__ == "__main__":
    main()

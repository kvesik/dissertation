import io
import pandas as pd
import re
import random
import numpy as np
from datetime import datetime


def main(relfilepath=None):
    if relfilepath is None:
        relfilepath = input("Enter relative filepath whose formatting to fix: ")

    with io.open(relfilepath, "r") as rf:
        with io.open(relfilepath.replace(".xls", "_fixed.xls"), "w") as wf:

            rline = rf.readline()
            while len(rline) > 0:
                if rline.startswith("Generated"):
                    wf.write(rline.replace("Adj. Num\t", ""))
                elif rline.startswith("Apriori"):
                    wf.write(rline.replace("Apriori\t", "Apriori:"))
                elif rline.startswith("(Initial)"):
                    wf.write(rline.replace("(Initial)\t\t", "(Initial)\t"))
                else:
                    cellcontents = rline.split("\t")
                    if cellcontents[1] == cellcontents[2] + cellcontents[0] and len(cellcontents[2]) > 0:
                        wf.write(rline.replace(cellcontents[1] + "\t", ""))
                    else:
                        wf.write(rline)
                rline = rf.readline()


if __name__ == "__main__":
    main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/NE304 - FilesForOTSoft_wdel_NEst_GLA_PDDP/OTSoft_wdel_NEst_GLA_PDDPFullHistory.xls")
    # main("OTSoft2.6old - using this location as of 20230413 - see Program Files for previous files/R03 - FilesForOTSoft_NEst_GLA_PDDP_nodia/OTSoft_NEst_GLA_PDDP_nodiaFullHistory.xls")
    # main("OTSoft2.6old - using this location as of 20230413 - see Program Files for previous files/R03 - FilesForOTSoft_SSeto_GLA_PDDP_nodia/OTSoft_SSeto_GLA_PDDP_nodiaFullHistory.xls")
    # main("OTSoft2.6old - using this location as of 20230413 - see Program Files for previous files/R03 - FilesForOTSoft_NSeto_GLA_PDDP_nodia/OTSoft_NSeto_GLA_PDDP_nodiaFullHistory.xls")

    # asks for user to input file path
    # main()
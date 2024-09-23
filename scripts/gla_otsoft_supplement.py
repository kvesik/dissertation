import io
import sys

import pandas as pd
import re
import os
import random
import numpy as np
from fractions import Fraction
from datetime import datetime
from generate_tableaux_otsoft_specifylang import langnames


INIT_WEIGHTS = {}
INIT_F = 0
INIT_M = 100

WORKING_DIR = "../sim_ins/20240507 on - OTSoft inputs"  # "OTSoft2.6old"
OUTPUTS_DIR = "../sim_outs/20240507_GLA_outputs"
DATA_DIR = WORKING_DIR + "/20240507_OTS" #  + "_wdel-gen-ne_ixn"  # "/20240117_forOTS"  # "/20231107MagriRuns"

DEMOTEONLYUNDOMINATEDLOSERS = False
MAGRI = True
# magritype =
    #   1 if original "calibrated" update rule from Magri 2012: numdemotions / (1 + numpromotions)
    #   2 if 1 / numpromotions
    #   3 if numdemotions / (numdemotions + numpromotions)
    #   4 if update rule mentioned in Magri & Kager 2015: 1 / (1 + numpromotions)
MAGRITYPE = 3
SPECGENBIAS = 0  # 20  # 20 is OTSoft default; -1 means don't bother; 0 means spec must be >= gen
EXPANDINGBIAS = True
EXPANDSLOWLY = True
EXPANDSLOWLYDECREASINGRATE = True
INITRANKINGSWMGEN = "0"
RELU = False
GRAVITY = False
GRAVITYCONST = 2
PREFERSPECIFICITY = True
SPECGENCONS = [
    ("Id(Bk)Syl1", "Id(Bk)"),
    # ("Id(Bk)Ft1", "Id(Bk)"), TODO
    ("MaxIOSyl1", "MaxIO"),
    ("Id(Hi,Lo,Rd)Syl1", "Id(Hi,Lo,Rd)"),
    ("Id(Hi)Syl1", "Id(Hi)"),
    ("Id(Lo)Syl1", "Id(Lo)"),
    ("Id(Rd)Syl1", "Id(Rd)")
    ]

LEARNING_TRIALS_DICT = {
    # 0: [10, 10, 10, 10],
    1: [100, 100, 100, 100],
    2: [500, 500, 500, 500],
    3: [1000, 1000, 1000, 1000],
    4: [5000, 5000, 5000, 5000],
    5: [10000, 10000, 10000, 10000]
}

LEARNING_R_F = [2, 0.2, 0.02, 0.002]
LEARNING_R_M = [2, 0.2, 0.02, 0.002]
LEARNING_NOISE_F = [2, 2, 2, 2]  # [2, 0.2, 0.02, 0.002]
LEARNING_NOISE_M = [2, 2, 2, 2]  # [2, 0.2, 0.02, 0.002]

m = "markedness"
f = "faithfulness"
ctype = "constraint type"
g1 = "group 1 strings"
g2 = "group 2 strings"

M_generality_omniscient = {  # for 2-grams only vs 3-grams only; combined can be calculated via (100a+1000b)/1100
    "*F1": (0.2, 0.3),
    "*F3": (0.6, 0.9),
    "*F4": (0.8, 1.2),
    "*F5": (1, 1.5),
    "*B1": (0.2, 0.3),
    "*B2": (0.4, 0.6),
    "*B3": (0.6, 0.9),
    "*B5": (1, 1.5),
    "*F1_B1": (0.01, 0.02),
    "*F1..._B1": (0.01, 0.029),
    "*F1_B2": (0.02, 0.04),
    "*F1..._B2": (0.02, 0.058),
    "*F1_B3": (0.03, 0.06),
    "*F1..._B3": (0.03, 0.087),
    "*F1_B5": (0.05, 0.1),
    "*F1..._B5": (0.05, 0.145),
    "*F3_B1": (0.03, 0.06),
    "*F3..._B1": (0.03, 0.081),
    "*F3_B2": (0.06, 0.12),
    "*F3..._B2": (0.06, 0.162),
    "*F3_B3": (0.09, 0.18),
    "*F3..._B3": (0.09, 0.243),
    "*F3_B5": (0.15, 0.3),
    "*F3..._B5": (0.15, 0.405),
    "*F4_B1": (0.04, 0.08),
    "*F4..._B1": (0.04, 0.104),
    "*F4_B2": (0.08, 0.16),
    "*F4..._B2": (0.08, 0.208),
    "*F4_B3": (0.12, 0.24),
    "*F4..._B3": (0.12, 0.312),
    "*F4_B5": (0.2, 0.4),
    "*F4..._B5": (0.2, 0.52),
    "*F5_B1": (0.05, 0.1),
    "*F5..._B1": (0.05, 0.125),
    "*F5_B2": (0.1, 0.2),
    "*F5..._B2": (0.1, 0.25),
    "*F5_B3": (0.15, 0.3),
    "*F5..._B3": (0.15, 0.375),
    "*F5_B5": (0.25, 0.5),
    "*F5..._B5": (0.25, 0.625),
    "*_B1F1": (0.01, 0.02),
    "*_B1...F1": (0.01, 0.029),
    "*_B1F3": (0.03, 0.06),
    "*_B1...F3": (0.03, 0.081),
    "*_B1F4": (0.04, 0.08),
    "*_B1...F4": (0.04, 0.104),
    "*_B1F5": (0.05, 0.1),
    "*_B1...F5": (0.05, 0.125),
    "*_B2F1": (0.02, 0.04),
    "*_B2...F1": (0.02, 0.058),
    "*_B2F3": (0.06, 0.12),
    "*_B2...F3": (0.06, 0.162),
    "*_B2F4": (0.08, 0.16),
    "*_B2...F4": (0.08, 0.208),
    "*_B2F5": (0.1, 0.2),
    "*_B2...F5": (0.1, 0.25),
    "*_B3F1": (0.03, 0.06),
    "*_B3...F1": (0.03, 0.087),
    "*_B3F3": (0.09, 0.18),
    "*_B3...F3": (0.09, 0.243),
    "*_B3F4": (0.12, 0.24),
    "*_B3...F4": (0.12, 0.312),
    "*_B3F5": (0.15, 0.3),
    "*_B3...F5": (0.15, 0.375),
    "*_B5F1": (0.05, 0.1),
    "*_B5...F1": (0.05, 0.145),
    "*_B5F3": (0.15, 0.3),
    "*_B5...F3": (0.15, 0.405),
    "*_B5F4": (0.2, 0.4),
    "*_B5...F4": (0.2, 0.52),
    "*_B5F5": (0.25, 0.5),
    "*_B5...F5": (0.25, 0.625),
}


class Learner:

    # magritype =
    #   1 if original "calibrated" update rule from Magri 2012: numdemotions / (1 + numpromotions)
    #   2 if 1 / numpromotions
    #   3 if numdemotions / (numdemotions + numpromotions)
    #   4 if update rule mentioned in Magri & Kager 2015: 1 / (1 + numpromotions)
    # initrankingswMgen_type =
    #   0   if not used
    #   1.yyy.sss   if application rate calculated from inputs
    #       where yyy% is the y-intercept multiplier
    #       and sss% is the slope multiplier
    #       e.g. the application rate gets *INIT_M*y.yy + INIT_M*s.ss
    #   2.n   if strata are determined greedily by all items containing B5 or F5, then 4, then 3, 2, 1
    #       2.1 with 5s at 180, 4s at 160, 3 at 140, 2 at 120, 1 at 100
    #   3.n   if strata are determed by all single segmental constraints, then long-distance harmony, then local harmony
    #       3.1 with singles at 140, LD at 120, local at 100
    #   4.n   if strata are determined greedily by all items containing B1 or F1, then 2, 3, 4, 5 (like option 2 but starting at bottom)
    #       4.1 with 1s at 100, 2s at 120, 3 at 140, 4 at 160, 5 at 180
    def __init__(self, srcfilepath, destdir, expnum, demoteunlyundominatedlosers=False, magri=True, magritype=1, specgenbias=0, gravity=False, gravityconst=2, preferspecificity=False, expandingbias=False, expandslowly=False, expandslowlydecreasingrate=False, initrankingswMgen_type="0", initMrankings_whichcand="faithful", initMrankings_calchow="sum", relu=False):
        numtrials_id = int(expnum[-1])
        self.learning_trials = LEARNING_TRIALS_DICT[numtrials_id]
        self.file = srcfilepath
        srcfilename = srcfilepath[srcfilepath.rfind("/") + 1:]
        destfiletemplate = destdir + "/" + expnum + " - " + srcfilename
        self.historyfile = destfiletemplate.replace(".txt", "_HISTORY" + str(self.learning_trials[0]) + ".txt")
        self.resultsfile = destfiletemplate.replace(".txt", "_RESULTS" + str(self.learning_trials[0]) + ".txt")

        # if expnum is not None and expnum != "":
        #     afterlastslash = self.file.rfind("/") + 1
        #     self.historyfile = self.historyfile[0:afterlastslash] + expnum + " - " + self.historyfile[afterlastslash:]
        #     self.resultsfile = self.resultsfile[0:afterlastslash] + expnum + " - " + self.resultsfile[afterlastslash:]
        self.demoteunlyundominatedlosers = demoteunlyundominatedlosers
        self.magri = magri
        self.magritype = magritype
        self.constraints = []
        self.weights = {}
        self.tableaux_list = []
        self.training_tableaux_list = []
        self.specgenbias = specgenbias
        self.expandingbias = expandingbias
        self.expandslowly = expandslowly
        self.expandslowlydecreasingrate = expandslowlydecreasingrate
        self.gravity = gravity
        self.gravityconst = gravityconst
        self.preferspecificity = preferspecificity
        self.errorcounter = 0
        self.initrankingswMgen_type = initrankingswMgen_type
        self.initrankingswMgen_int = int(self.initrankingswMgen_type[0])
        self.initMrankings_whichcand = initMrankings_whichcand
        self.initMrankings_calchow = initMrankings_calchow
        self.relu = relu

    def set_tableaux(self, tableaux_list):
        self.tableaux_list = tableaux_list
        # only try and learn from the tableaux that have input frequency information
        self.training_tableaux_list = [t for t in tableaux_list if sum(t["frequency"].values) > 0]

    def read_input(self):
        with io.open(self.file, "r") as infile:
            df = pd.read_csv(infile, sep="\t", header=1, keep_default_na=False)
            df.rename(
                columns=({'Unnamed: 0': 'input', 'Unnamed: 1': 'candidate', 'Unnamed: 2': 'frequency'}),
                inplace=True,
            )

            rules = {}
            for colname in df.columns[3:]:
                contents = list(df[colname].values)

                if contents[0] == "Group1":
                    # faithfulness constraint
                    grp2idx = contents.index("Group2")
                    emptyidx = contents.index("")
                    grp1 = contents[1:grp2idx]
                    grp2 = contents[grp2idx + 1:emptyidx]
                    rules[colname] = {
                        ctype: f,
                        g1: list(grp1),
                        g2: list(grp2)
                    }
                elif contents[0] == "" or re.match("\d+", str(contents[0])):
                    # violations listed explicitly
                    pass
                else:
                    # markedness constraint
                    emptyidx = contents.index("")
                    grp1 = contents[:emptyidx]
                    rules[colname] = {
                        ctype: m,
                        g1: list(grp1)
                    }

            tableaux = {}

            cur_input = ""
            cur_tableau = {}
            for idx, row in df.iterrows():
                if row["input"] != "":
                    if len(cur_tableau.keys()) > 0:
                        # save previous input's tableau
                        tableaux[cur_input] = cur_tableau
                    # start a new tableau
                    cur_input = row["input"]
                    cur_tableau = {}
                cur_candidate = row["candidate"]
                cur_frequency = row["frequency"]
                if cur_frequency == "":
                    cur_frequency = 0
                else:
                    cur_frequency = float(cur_frequency)

                cur_violations = getviolations(cur_input, cur_candidate, list(df.columns[3:]), row[3:], rules)
                cur_tableau[cur_candidate] = {}
                cur_tableau[cur_candidate]["frequency"] = cur_frequency
                cur_tableau[cur_candidate]["violations"] = cur_violations

            # save the final input's tableau
            tableaux[cur_input] = cur_tableau

        # return tableaux, list(df.columns[3:])
        self.constraints = list(df.columns[3:])
        self.weights = {c:0 for c in self.constraints}

        # initialize constraint set and weights
        if len(INIT_WEIGHTS.keys()) > 0:
            # initial weights have been specified; use them
            for con in self.constraints:
                self.weights[con] = INIT_WEIGHTS[con]
                # in theory could just assign the dictionary wholesale but order could be relevant somewhere else...
        # # elif self.initrankingswMgen_int > 0:
        # #     # start F constraints from 0 and markedness weights distributed by degree of generality
        # #     if self.initrankingswMgen_int == 1:
        # #         # with 0.0 generality at bottom end of M range, and 1.0 generality at top end of M range
        # #         for con in self.constraints:
        # #             if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
        # #                 # it's a faith constraint
        # #                 self.weights[con] = INIT_F
        # #             else:
        # #                 # it's a markedness constraint
        # #                 combined2and3gram_generality = ((100*M_generality_omniscient[con][0]) + (1000*M_generality_omniscient[con][1])) / 1100
        # #                 yint_multiplier = int(self.initrankingswMgen[2:5])/100
        # #                 slope_multiplier = int(self.initrankingswMgen[6:])/100
        # #                 self.weights[con] = INIT_M*yint_multiplier + combined2and3gram_generality*INIT_M*slope_multiplier
        # #                 # if self.initrankingswMgen == 1.1:
        # #                 #     # M range from 50 to 100
        # #                 #     self.weights[con] = INIT_M/2 + (combined2and3gram_generality*INIT_M/2)
        # #                 # elif self.initrankingswMgen == 1.2:
        # #                 #     # M range from 100 to 200
        # #                 #     self.weights[con] = INIT_M + (combined2and3gram_generality*INIT_M)
        # #                 # elif self.initrankingswMgen == 1.3:
        # #                 #     # M range from 150 to 300
        # #                 #     self.weights[con] = INIT_M*1.5 + (combined2and3gram_generality*INIT_M*1.5)
        # #                 # elif self.initrankingswMgen == 1.4:
        # #                 #     # M range from 25 to 50
        # #                 #     self.weights[con] = INIT_M/4 + (combined2and3gram_generality*INIT_M/4)
        # #                 # elif self.initrankingswMgen == 1.5:
        # #                 #     # M range from 25 to 75
        # #                 #     self.weights[con] = INIT_M/4 + (combined2and3gram_generality*INIT_M/2)
        # #                 # elif self.initrankingswMgen == 1.6:
        # #                 #     # M range from 25 to 125
        # #                 #     self.weights[con] = INIT_M/4 + (combined2and3gram_generality*INIT_M)
        # #                 # elif self.initrankingswMgen == 1.7:
        # #                 #     # M range from 200 to 225
        # #                 #     self.weights[con] = INIT_M*2 + (combined2and3gram_generality*INIT_M/4)
        # #                 # elif self.initrankingswMgen == 1.8:
        # #                 #     # M range from 50 to 150
        # #                 #     self.weights[con] = INIT_M/2 + (combined2and3gram_generality*INIT_M)
        # #                 # elif self.initrankingswMgen == 1.9:
        # #                 #     # M range from 50 to 250
        # #                 #     self.weights[con] = INIT_M/2 + (combined2and3gram_generality*INIT_M*2)
        # #                 # elif self.initrankingswMgen == 1.11:
        # #                 #     # M range from 50 to 75
        # #                 #     self.weights[con] = INIT_M/2 + (combined2and3gram_generality*INIT_M/4)  # was written wrong as /2 *2
        # #                 # elif self.initrankingswMgen == 1.12:
        # #                 #     # M range from 100 to 125
        # #                 #     self.weights[con] = INIT_M*1.0 + (combined2and3gram_generality*INIT_M/4)  # was written wrong as /2 *2
        # #                 # elif self.initrankingswMgen == 1.13:
        # #                 #     # M range from 75 to 100
        # #                 #     self.weights[con] = INIT_M*.75 + (combined2and3gram_generality*INIT_M/4)
        # #                 # elif self.initrankingswMgen == 1.14:
        # #                 #     # M range from 75 to 125
        # #                 #     self.weights[con] = INIT_M*.75 + (combined2and3gram_generality*INIT_M/2)
        # #                 # elif self.initrankingswMgen == 1.15:
        # #                 #     # M range from 100 to 150
        # #                 #     self.weights[con] = INIT_M + (combined2and3gram_generality*INIT_M/2)
        # #                 # elif self.initrankingswMgen == 1.16:
        # #                 #     # M range from 25 to 100
        # #                 #     self.weights[con] = INIT_M*.25 + (combined2and3gram_generality*INIT_M*.75)
        # #                 # elif self.initrankingswMgen == 1.17:
        # #                 #     # M range from 50 to 125
        # #                 #     self.weights[con] = INIT_M*.50 + (combined2and3gram_generality*INIT_M*.75)
        # #                 # elif self.initrankingswMgen == 1.18:
        # #                 #     # M range from 75 to 150
        # #                 #     self.weights[con] = INIT_M*.75 + (combined2and3gram_generality*INIT_M*.75)
        # #                 # elif self.initrankingswMgen == 1.19:
        # #                 #     # M range from 100 to 175
        # #                 #     self.weights[con] = INIT_M*1.0 + (combined2and3gram_generality*INIT_M*.75)
        # #                 # elif self.initrankingswMgen == 1.21:
        # #                 #     # M range from 75 to 175
        # #                 #     self.weights[con] = INIT_M*.75 + (combined2and3gram_generality*INIT_M*1.0)
        # #                 #
        # #                 # elif self.initrankingswMgen == 1.22:
        # #                 #     # M range from 40 to 80
        # #                 #     self.weights[con] = INIT_M * .40 + (combined2and3gram_generality * INIT_M * .40)
        # #                 # elif self.initrankingswMgen == 1.23:
        # #                 #     # M range from 60 to 100
        # #                 #     self.weights[con] = INIT_M*.60 + (combined2and3gram_generality*INIT_M*.40)
        # #                 # elif self.initrankingswMgen == 1.24:
        # #                 #     # M range from 40 to 90
        # #                 #     self.weights[con] = INIT_M*.40 + (combined2and3gram_generality*INIT_M*.50)
        # #                 # elif self.initrankingswMgen == 1.25:
        # #                 #     # M range from 60 to 110
        # #                 #     self.weights[con] = INIT_M*.60 + (combined2and3gram_generality*INIT_M*.50)
        # #                 # elif self.initrankingswMgen == 1.26:
        # #                 #     # M range from 40 to 100
        # #                 #     self.weights[con] = INIT_M*.40 + (combined2and3gram_generality*INIT_M*.60)
        # #                 # elif self.initrankingswMgen == 1.27:
        # #                 #     # M range from 60 to 120
        # #                 #     self.weights[con] = INIT_M*.60 + (combined2and3gram_generality*INIT_M*.60)
        # #                 # elif self.initrankingswMgen == 1.28:
        # #                 #     # M range from 50 to 90
        # #                 #     self.weights[con] = INIT_M*.50 + (combined2and3gram_generality*INIT_M*.40)
        # #                 # elif self.initrankingswMgen == 1.29:
        # #                 #     # M range from 50 to 135
        # #                 #     self.weights[con] = INIT_M*.50 + (combined2and3gram_generality*INIT_M*.85)
        # #
        # #     elif self.initrankingswMgen_int == 2:
        # #         # with strata determined by all items containing B5 or F5, then 4, then 3, 2, 1
        # #         lowestvalue = 100 if self.initrankingswMgen == "2.1" else 100
        # #         intervalsize = 20 if self.initrankingswMgen == "2.1" else 20
        # #         for con in self.constraints:
        # #             if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
        # #                 # it's a faith constraint
        # #                 self.weights[con] = INIT_F
        # #             else:
        # #                 # it's a markedness constraint
        # #                 self.weights[con] = lowestvalue + (getmaxdigit(con)-1) * intervalsize
        # #     elif self.initrankingswMgen_int == 3:
        # #         # with strata determined by all single segmental cons, then LD harmony, then local harmony
        # #         lowestvalue = 100 if self.initrankingswMgen == "3.1" else 100
        # #         intervalsize = 20 if self.initrankingswMgen == "3.1" else 20
        # #         for con in self.constraints:
        # #             if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
        # #                 # it's a faith constraint
        # #                 self.weights[con] = INIT_F
        # #             else:
        # #                 # it's a markedness constraint
        # #                 if "F" in con and "B" in con:
        # #                     if "..." in con:
        # #                         # it's a long-distance harmony constraint
        # #                         self.weights[con] = lowestvalue + intervalsize*1
        # #                     else:
        # #                         # it's a local harmony constraint
        # #                         self.weights[con] = lowestvalue + intervalsize*0
        # #                 elif "F" in con or "B" in con:
        # #                     # it's a segmental markedness constraint
        # #                     self.weights[con] = lowestvalue + intervalsize*2
        # #     elif self.initrankingswMgen_int == 4:
        # #         # with strata determined by all items containing B1 or F1, then 2, then 3, 4, 5
        # #         lowestvalue = 100 if self.initrankingswMgen == "4.1" else 100
        # #         intervalsize = 20 if self.initrankingswMgen == "4.1" else 20
        # #         for con in self.constraints:
        # #             if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
        # #                 # it's a faith constraint
        # #                 self.weights[con] = INIT_F
        # #             else:
        # #                 # it's a markedness constraint
        # #                 self.weights[con] = lowestvalue + (getmindigit(con)-1) * intervalsize
        # #     print(self.weights)
        # else:
        #     # no initial weights have been specified; start from scratch
        #     for con in self.constraints:
        #         if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
        #             # it's a faith constraint
        #             self.weights[con] = INIT_F
        #         else:
        #             # it's a markedness constraint
        #             self.weights[con] = INIT_M

        return tableaux

    def observe(self, numbatches):
        numinputsseen = 0
        numrowsseen = 0
        running_sums = {c:0 for c in self.constraints}
        running_nums = {c:0 for c in self.constraints}
        batchsize = self.learning_trials[0]  # always use the size of the first learning batch

        for bnum in range(numbatches):
            sampled_tableaux = random.choices(self.training_tableaux_list, k=batchsize)
            print("number of sampled tableaux in observation batch", bnum, "is", len(sampled_tableaux))
            for t in sampled_tableaux:
                thistable_numrows = t.shape[0]
                numrowsseen += thistable_numrows

                numinputsseen += 1
                if numinputsseen % 5000 == 0:
                    print("observation trial #", numinputsseen)

                # observe one input and update running values
                if self.initMrankings_whichcand == "faithful":
                    faithfulrow = t.head(1)  # faithful row is always the first one
                    violns = faithfulrow.sum(numeric_only=True, axis=0)
                elif self.initMrankings_whichcand == "random":
                    randomrow = t.sample(n=1)
                    violns = randomrow.sum(numeric_only=True, axis=0)
                else:  # all
                    violns = t.sum(numeric_only=True, axis=0)

                thisinput_violncounts = {c: (0 if (c.startswith("Id") or c.startswith("Max")) else violns[c]) for c in self.constraints}

                for c in self.constraints:
                    running_nums[c] += thisinput_violncounts[c]
                    if self.initMrankings_whichcand == "all":
                        running_sums[c] += Fraction(Fraction(thisinput_violncounts[c]), thistable_numrows)
                    else:  # just one candidate, whether faithful or random
                        running_sums[c] += thisinput_violncounts[c]

            print(batchsize, " observation trials complete")

        # calculate application rates
        if self.initMrankings_calchow == "average":
            M_generality = {c: float(running_sums[c] / numinputsseen) for c in self.constraints}
        else:  # sum
            if self.initMrankings_whichcand == "all":
                M_generality = {c: (running_nums[c] / numrowsseen) for c in self.constraints}
            else:  # single candidate each time, whether faithful or random
                M_generality = {c: (running_nums[c] / numinputsseen) for c in self.constraints}

        return M_generality

    def train(self):
        Fcons = [c for c in self.constraints if c.startswith("Id") or c.startswith("Max")]  # or a bunch of other stuff, but this is the only kind relevant to me
        Mcons = [c for c in self.constraints if c not in Fcons]

        if self.initrankingswMgen_int >= 1:
            print("--------------- BEGIN M GENERALITY CALCULATIONS ---------------------")

            if self.initrankingswMgen_int == 1:
                Mgen_bycon = self.observe(1)  # do one batch of observation, to figure out markedness application rates

                # yint_multiplier = 1
                # slope_multiplier = 0

                yint_multiplier = int(self.initrankingswMgen_type[2:5]) / 100
                slope_multiplier = int(self.initrankingswMgen_type[6:]) / 100

                # if self.initrankingswMgen in [1.4, 1.5, 1.6, 1.16]:
                #     yint_multiplier = 0.25
                # elif self.initrankingswMgen in [1.22, 1.24, 1.26]:
                #     yint_multiplier = 0.40
                # elif self.initrankingswMgen in [1.1, 1.8, 1.9, 1.11, 1.12, 1.17, 1.28, 1.29]:
                #     yint_multiplier = 0.50
                # elif self.initrankingswMgen in [1.23, 1.25, 1.27]:
                #     yint_multiplier = 0.60
                # elif self.initrankingswMgen in [1.13, 1.14, 1.18, 1.21]:
                #     yint_multiplier = 0.75
                # elif self.initrankingswMgen in [1.2, 1.15, 1.19]:
                #     yint_multiplier = 1.0
                # elif self.initrankingswMgen in [1.3]:
                #     yint_multiplier = 1.5
                # elif self.initrankingswMgen in [1.7]:
                #     yint_multiplier = 2.0
                #
                # if self.initrankingswMgen in [1.4, 1.7, 1.13]:
                #     slope_multiplier = 0.25
                # elif self.initrankingswMgen in [1.22, 1.23, 1.28]:
                #     slope_multiplier = 0.40
                # elif self.initrankingswMgen in [1.1, 1.5, 1.14, 1.15, 1.24, 1.25]:
                #     slope_multiplier = 0.50
                # elif self.initrankingswMgen in [1.26, 1.27]:
                #     slope_multiplier = 0.60
                # elif self.initrankingswMgen in [1.16, 1.17, 1.18, 1.19]:
                #     slope_multiplier = 0.75
                # elif self.initrankingswMgen in [1.29]:
                #     slope_multiplier = 0.85
                # elif self.initrankingswMgen in [1.2, 1.6, 1.8, 1.21]:
                #     slope_multiplier = 1.0
                # elif self.initrankingswMgen in [1.3]:
                #     slope_multiplier = 1.5
                # elif self.initrankingswMgen in [1.9, 1.11, 1.12]:
                #     slope_multiplier = 2.0

                for con in Mcons:
                    self.weights[con] = (INIT_M * yint_multiplier) + (Mgen_bycon[con] * INIT_M * slope_multiplier)

            elif self.initrankingswMgen_int == 2:
                # with strata determined by all items containing B5 or F5, then 4, then 3, 2, 1
                lowestvalue = 100 if self.initrankingswMgen_type == "2.1" else 100
                intervalsize = 20 if self.initrankingswMgen_type == "2.1" else 20
                for con in Mcons:
                    self.weights[con] = lowestvalue + (getmaxdigit(con) - 1) * intervalsize

            elif self.initrankingswMgen_int == 3:
                # with strata determined by all single segmental cons, then LD harmony, then local harmony
                lowestvalue = 100 if self.initrankingswMgen_type == "3.1" else 100
                intervalsize = 20 if self.initrankingswMgen_type == "3.1" else 20
                for con in Mcons:
                    if "F" in con and "B" in con:
                        if "..." in con:
                            # it's a long-distance harmony constraint
                            self.weights[con] = lowestvalue + intervalsize * 1
                        else:
                            # it's a local harmony constraint
                            self.weights[con] = lowestvalue + intervalsize * 0
                    elif "F" in con or "B" in con:
                        # it's a segmental markedness constraint
                        self.weights[con] = lowestvalue + intervalsize * 2

            elif self.initrankingswMgen_int == 4:
                # with strata determined by all items containing B1 or F1, then 2, then 3, 4, 5
                lowestvalue = 100 if self.initrankingswMgen_type == "4.1" else 100
                intervalsize = 20 if self.initrankingswMgen_type == "4.1" else 20
                for con in Mcons:
                    self.weights[con] = lowestvalue + (getmindigit(con) - 1) * intervalsize
        else:
            # no initial weights have been specified; start from scratch
            for con in Mcons:
                self.weights[con] = INIT_M

        for Fcon in Fcons:
            self.weights[Fcon] = INIT_F

        print("--------------- BEGIN TRAIN ---------------------")
        # put headers into history file
        # headertowrite = "lap num" + "\t" + "generated" + "\t" + "heard"
        headertowrite = "trialnum" + "\t" + "Generated" + "\t" + "Heard"
        startvalstowrite = "" + "\t" + "" + "\t" + ""
        headertowrite += "".join(["\t" + c + "\tnow" for c in self.constraints]) + "\n"
        startvalstowrite += "".join(["\t\t" + str(self.weights[c]) for c in self.constraints]) + "\n"
        with io.open(self.historyfile, "w") as history:
            history.write(headertowrite)
            history.write(startvalstowrite)

            # do any necessary shuffling re a priori rankings right away
            for speccon, gencon in [pairofcons for pairofcons in SPECGENCONS if pairofcons[0] in self.weights.keys() and pairofcons[1] in self.weights.keys()]:  # SPECGENCONS:
                if self.specgenbias >= 0 and round(self.weights[speccon], 10) < round(self.weights[gencon] + self.specgenbias, 10):
                    apriori_adjust = self.weights[gencon] + self.specgenbias - self.weights[speccon]
                    self.weights[speccon] = self.weights[gencon] + self.specgenbias

                    linetowrite = "0" + "\t" + "Apriori" + "\t" + speccon + ">>" + gencon + "\t"
                    for con in self.constraints:
                        if con != speccon or self.specgenbias == -1:
                            linetowrite += "\t\t"
                        else:  # SPEC_GEN_BIAS != -1
                            linetowrite += str(apriori_adjust) + "\t" + str(self.weights[speccon])
                    linetowrite += "\n"
                    history.write(linetowrite)
            linetowrite = "0" + "\t\t"
            for con in self.constraints:
                linetowrite += "\t\t" + str(self.weights[con])

            learningtrial = 0  # lap_count = 0
            for batchnum in range(len(self.learning_trials)):
                print("batch #", batchnum)

                # # the commented-out section below is not aligned with OTSoft in that
                # # (a) it assumes "learning trials" is the number of times through ALL of the data,
                # #   rather than the number of individual learning trials
                # # (b) it samples without replacement (ie, ensures that every data point gets seen), rather than
                # #   sampling with replacement (ie, learning proportions might be different from input file frequencies)
                # for learningtrial in range(LEARNING_TRIALS[batchnum]):
                #     lap_count += 1
                #     if learningtrial % 1000 == 0:
                #         print("trial #", learningtrial)
                #     shuffled_tableaux = random.sample(self.training_tableaux_list, len(self.training_tableaux_list))
                #     for t in shuffled_tableaux:
                #         self.learn(t, LEARNING_R_F[batchnum], LEARNING_R_M[batchnum], LEARNING_NOISE_F[batchnum], LEARNING_NOISE_M[batchnum], lap_count, history)

                # the section below replaces the one from above
                # in this version, I sample with replacement AND use the "learning trials" parameter to refer
                # to individual trials rather than number of loops through all data... so, more like OTSoft behaviour
                sampled_tableaux = random.choices(self.training_tableaux_list, k=self.learning_trials[batchnum])

                # and this is "use exact proportions"-ish
                # timestouselist = LEARNING_TRIALS[batchnum] / len(self.training_tableaux_list)
                # timesthrough = 1
                # sampled_tableaux = []
                # while timesthrough < timestouselist:
                #     sampled_tableaux += random.sample(self.training_tableaux_list, len(self.training_tableaux_list))
                #     timesthrough += 1
                # remainingsamples = LEARNING_TRIALS[batchnum] - len(sampled_tableaux)
                # sampled_tableaux += random.sample(self.training_tableaux_list, remainingsamples)

                print("number of sampled tableaux in batch", batchnum, "is", len(sampled_tableaux))
                for t in sampled_tableaux:
                    learningtrial += 1  # lap_count += 1
                    if learningtrial % 5000 == 0:  # if lap_count % 1000 == 0:
                        print("trial #", learningtrial)  # print("trial #", lap_count)
                    # self.learn(t, LEARNING_R_F[batchnum], LEARNING_R_M[batchnum], LEARNING_NOISE_F[batchnum], LEARNING_NOISE_M[batchnum], lap_count, history)
                    self.learn(t, LEARNING_R_F[batchnum], LEARNING_R_M[batchnum], LEARNING_NOISE_F[batchnum], LEARNING_NOISE_M[batchnum], learningtrial, history)

                print(self.learning_trials[batchnum], " trials complete")

            summarytowrite = "TOTAL\t" + "\t" + "".join(["\t\t" + str(self.weights[c]) for c in self.constraints]) + "\n"
            history.write(summarytowrite)

    def getevalweights(self, noise_f, noise_m):
        evalweights = {}
        for con in self.constraints:
            noise = 0
            if con.startswith("Id") or con.startswith("Max"):
                noise = noise_f
            else:
                noise = noise_m
            evalweights[con] = np.random.normal(loc=self.weights[con], scale=noise)
        return evalweights

    def updateweights(self, tableau_df, intendedwinner, generatedoutput, cur_R_F, cur_R_M, learningtrial_num, historystream):
        winner_df = tableau_df[tableau_df[tableau_df.columns[0]] == intendedwinner]
        optimal_df = tableau_df[tableau_df[tableau_df.columns[0]] == generatedoutput]

        adjustments = {}
        promotion_ratio = 1

        # demotion amount as usual
        # promotion amount = (# constraints demoted)/(1 + # constraints promoted)
        # TODO supplanted by lines below, 'erc = {}' to '# else erc[c] == "e" and we don't need to do anything'
        # numwinnerpreferrers = 0
        # numloserpreferrers = 0

        erc = {}
        maxwinnerpreferringweight = 0
        for c in self.constraints:
            w = winner_df[c].values[0]
            o = optimal_df[c].values[0]
            if w > o:
                erc[c] = "L"  # in this ERC, this is a loser-preferring constraint
            elif o > w:
                erc[c] = "W"  # in this ERC, this is a winner-preferring constraint
                maxwinnerpreferringweight = max(maxwinnerpreferringweight, self.weights[c])
            else:
                erc[c] = "e"  # in this ERC, this constraint prefers neither winner nor loser
            # if w > 0 and o > 0:
            #     # cancel out violations - just look at relative difference
            #     overlap = min([w, o])
            #     w -= overlap
            #     o -= overlap
            # if w > 0:
            #     erc[c] = "L"  # in this ERC, this is a loser-preferring constraint
            # elif o > 0:
            #     erc[c] = "W"  # in this ERC, this is a winner-preferring constraint
            #     maxwinnerpreferringweight = max(maxwinnerpreferringweight, self.weights[c])
            # else:
            #     erc[c] = "e"  # in this ERC, this constraint prefers neither winner nor loser
        numloserpreferrers = (list(erc.values())).count("L")
        numwinnerpreferrers = (list(erc.values())).count("W")
        undominatedloserpreferrers = [con for (con, pref) in erc.items() if pref == "L" and self.weights[con] >= maxwinnerpreferringweight]

        for c in self.constraints:
            if erc[c] == "L":
                if not self.demoteunlyundominatedlosers:
                    adjustments[c] = -1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
                elif c in undominatedloserpreferrers:
                    adjustments[c] = -1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
                else:
                    # no undominated, but I want to see it visually marked in the output, so
                    adjustments[c] = 0
            elif erc[c] == "W":
                adjustments[c] = 1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
            # else erc[c] == "e" and we don't need to do anything

        # TODO supplanted by lines above, 'erc = {}' to '# else erc[c] == "e" and we don't need to do anything'
        # for c in self.constraints:
        #     w = winner_df[c].values[0]
        #     o = optimal_df[c].values[0]
        #     if w > 0 and o > 0:
        #         # cancel out violations - just look at relative difference
        #         overlap = min([w, o])
        #         w -= overlap
        #         o -= overlap
        #     if w > 0:
        #         numloserpreferrers += 1  # for Magri update
        #         if self.isLundominated():
        #             adjustments[c] = -1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
        #     elif o > 0:
        #         numwinnerpreferrers += 1  # for Magri update
        #         adjustments[c] = 1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)


        # if we're doing "prefer specificity," make sure that if a specific faithfulness constraint is getting promoted,
        # its general counterpart stays where it is
        if self.preferspecificity:
            for speccon, gencon in [pairofcons for pairofcons in SPECGENCONS]:
                if speccon in self.constraints and speccon in adjustments.keys():
                    specadjustment = adjustments[speccon]
                    adjustments[gencon] = 0
                    if specadjustment > 0:
                        numwinnerpreferrers -= 1
                    elif specadjustment < 0:
                        numloserpreferrers -= 1
        if self.magri:
            # magritype =
            #   1 if original "calibrated" update rule from Magri 2012: numdemotions / (1 + numpromotions)
            #   2 if 1 / numpromotions
            #   3 if numdemotions / (numdemotions + numpromotions)
            #   4 if update rule mentioned in Magri & Kager 2015: 1 / (1 + numpromotions)
            if self.magritype == 1:
                promotion_ratio = numloserpreferrers / (1 + numwinnerpreferrers)
            elif self.magritype == 2:
                promotion_ratio = 1 / numwinnerpreferrers
            elif self.magritype == 3:
                promotion_ratio = numloserpreferrers / (numloserpreferrers + numwinnerpreferrers)
            elif self.magritype == 4:
                promotion_ratio = 1 / (1 + numwinnerpreferrers)
            if numloserpreferrers == 0:
                pass
                # print(winner_df)
                # print(optimal_df)

        linetowrite = str(learningtrial_num) + "\t" + generatedoutput + "\t" + intendedwinner
        for con in self.constraints:
            if con in adjustments.keys():
                adjustment_amount = adjustments[con]
                if adjustment_amount > 0:
                    adjustment_amount *= promotion_ratio
                linetowrite += "\t" + str(adjustment_amount)
                self.weights[con] = self.weights[con] + adjustment_amount
                if self.relu and self.weights[con] < 0:
                    self.weights[con] = 0
                linetowrite += "\t" + str(self.weights[con])
            else:
                linetowrite += "\t\t"
        linetowrite += "\n"

        historystream.write(linetowrite)

        for speccon, gencon in [pairofcons for pairofcons in SPECGENCONS if pairofcons[0] in self.weights.keys() and pairofcons[1] in self.weights.keys()]:  # SPECGENCONS:

            if self.specgenbias >= 0 and round(self.weights[speccon], 10) < round(self.weights[gencon] + self.specgenbias, 10):
                # # did the lower one come up too high, or did the upper one come down too low?
                # specconadjustment = adjustments[speccon] if speccon in adjustments.keys() else 0
                # genconadjustment = adjustments[gencon] if gencon in adjustments.keys() else 0
                apriori_adjust = self.weights[gencon] + self.specgenbias - self.weights[speccon]
                self.weights[speccon] = self.weights[gencon] + self.specgenbias

                linetowrite = str(learningtrial_num) + "\t" + "Apriori" + "\t" + speccon + ">>" + gencon + "\t"
                for con in self.constraints:
                    if con != speccon or self.specgenbias == -1:
                        linetowrite += "\t\t"
                    else:  # SPEC_GEN_BIAS != -1
                        linetowrite += str(apriori_adjust) + "\t" + str(self.weights[speccon]) + "\t"
                linetowrite += "\n"
                historystream.write(linetowrite)

            # themagicalconstant = 2
            if self.gravity and self.errorcounter % self.gravityconst == 0:  # completely arbitrarily, apply gravitational drift every k errors
                specvioln = optimal_df[speccon].values[0]
                genvioln = optimal_df[gencon].values[0]
                # confirm that this kind of faithfulness constraint was involved in the current error
                # if not, they should not be adjusted
                if genvioln > 0:
                    # spec_proportion = specvioln / (genvioln * themagicalconstant)  #  * themagicalconstant))
                    spec_adjust = 0  # - (spec_proportion * cur_R_F)
                    gen_adjust = -cur_R_F
                    self.weights[speccon] += spec_adjust
                    self.weights[gencon] += gen_adjust

                    linetowrite = str(learningtrial_num) + "\t" + "Gravity" + "\t" + gencon + "\t"  # speccon + "&" + gencon + "\t"
                    for con in self.constraints:
                        if con == speccon:
                            linetowrite += str(spec_adjust) + "\t" + str(self.weights[speccon]) + "\t"
                        elif con == gencon:
                            linetowrite += str(gen_adjust) + "\t" + str(self.weights[gencon]) + "\t"
                        else:  # it's not a (paired) faith constraint
                            linetowrite += "\t\t"
                    linetowrite += "\n"
                    historystream.write(linetowrite)

            # if applying the expanding-bias bias, check now (after all other adjustments) if there is more space than before
            if self.expandingbias:
                currentdiff = self.weights[speccon] - self.weights[gencon]
                if currentdiff > self.specgenbias:
                    if self.expandslowly:
                        rawincrease = currentdiff - self.specgenbias
                        if self.expandslowlydecreasingrate:  # attempt to asymptotically taper off the expansion
                            # # make sure we start at a rate of 0.5 and decrease from there as per the learning rate - this still makes really big changes
                            # temperedincrease = rawincrease * cur_R_F / (2 * LEARNING_R_F[0])
                            # alternate approach - start at a rate of 1.0 and decrease from there inverse to the number of... errors? trials? let's go with errors for now
                            temperedincrease = rawincrease / learningtrial_num  #  self.errorcounter
                        else:  # expansion rate is slow but remains constant
                            temperedincrease = rawincrease / 2  # halfway only, always
                        print("trial #", learningtrial_num, ": specgenbias increased by", temperedincrease, ", from", self.specgenbias, "to", (self.specgenbias + temperedincrease))
                        self.specgenbias = self.specgenbias + temperedincrease
                    else:
                        print("trial #", learningtrial_num, ": specgenbias increased by", (currentdiff - self.specgenbias), ", from", self.specgenbias, "to", currentdiff)
                        self.specgenbias = currentdiff

    def learn(self, tableau_df, cur_R_F, cur_R_M, cur_noise_F, cur_noise_M, learningtrial_num, historystream):
        # select a learning datum from distribution (which could just be all one form)
        ur = tableau_df.columns[0]
        datum = ""
        candidates = tableau_df[ur].values
        frequencies = tableau_df["frequency"].values
        frequencysum = sum(frequencies)
        frequencies = [f/frequencysum for f in frequencies]
        sample = random.uniform(0, 1)
        cumulative_freq = 0
        idx = 0
        while idx < len(frequencies) and datum == "":
            cumulative_freq += frequencies[idx]
            if sample <= cumulative_freq:
                datum = candidates[idx]
            idx += 1

        usemethod1 = True
        if usemethod1:
            # Method 1 for selecting the loser of interest: current hypothesized grammar's optimal output (standard GLA)
            #
            # generate the optimal candidate based on current constraint weights (ranking), with or without noise
            evalweights = self.getevalweights(cur_noise_F, cur_noise_M)
            optimal_cand = evaluate_one(tableau_df, evalweights)
            #
            # if the optimal candidate matches the intended winner, do nothing
            #
            # if the optimal candidate does not match the intended winner, update the weights
            if datum != optimal_cand:
                self.errorcounter += 1
                self.updateweights(tableau_df, datum, optimal_cand, cur_R_F, cur_R_M, learningtrial_num, historystream)
            #
            # end of Method 1.
        else:
            # Method 2 for selecting the loser of interest: Magri & Kager 2015 strategy using ERCs ("closest" to winner)
            #
            # the row of the tableau where the candidate (ie, the value in the ur column) is the winner
            winnerviolationprofile_df = tableau_df[tableau_df[ur] == datum]
            erc_df = tableau_df.copy(deep=True)
            erc_df.drop(erc_df.index[(erc_df[ur] == ur)], axis=0, inplace=True)  # don't need the winner row for a table of ERCs
            candidate_contenders = [cand for cand in tableau_df[ur].values]  # may not be necessary to know their names... except maybe to compare to intended winner(s)?
            for candidate in candidate_contenders:
                # the row of the tableau where the candidate (ie, the value in the ur column) is the one we're focused on in this iteration
                candidateviolationprofile_df = tableau_df[tableau_df[ur] == candidate]
                for con in self.constraints:
                    preference_string = "e"
                    first = candidateviolationprofile_df[con].iloc[0]
                    second = winnerviolationprofile_df[con].iloc[0]
                    if candidateviolationprofile_df[con].iloc[0] > winnerviolationprofile_df[con].iloc[0]:
                        preference_string = "W"
                    elif candidateviolationprofile_df[con].iloc[0] < winnerviolationprofile_df[con].iloc[0]:
                        preference_string = "L"
                    # else if they're equal:
                        # then leave preference_string = "e"
                    erc_df.loc[erc_df[ur] == candidate, con] = preference_string
            # now the table of ERCs should be correctly loaded with W/L/e entries for each potential-loser's row
            #
            # check for, and remove, superset rows
            numrowseliminated = self.removesupersets(erc_df)
            # TODO split multi-L ERCs into multiple single-L ERCs
            erc_df = self.splitERCswithmultipleLs(erc_df)
            # TODO find n, the least number of Ws in a row
            fewestW = self.findfewestWs(erc_df)
            # TODO choose a row randomly from all of those with n Ws
            selectedloser = self.chooserandomrow(erc_df, fewestW)
            # TODO make updates based on that row
            #
            # end of Method 2.

    def splitERCswithmultipleLs(self, erc_df):
        cols = erc_df.columns
        ur = cols[0]
        numrows = len(erc_df.index)
        rowindicestoremove = []
        rowstoadd = []

        for row_idx in range(numrows):
            cons_with_Ls = []
            for con in self.constraints:
                if erc_df[con].iloc[row_idx] == "L":
                    cons_with_Ls.append(con)

            if len(cons_with_Ls) > 1:
                rowindicestoremove.append(row_idx)
                therow = erc_df.iloc[[row_idx]].copy()

                # split into multiple lines, each with only one L (and candidate name suffixed with counter)
                for counter, con_with_L in enumerate(cons_with_Ls):
                    other_cons_with_Ls = [c for c in cons_with_Ls if c != con_with_L]

                    suffixedloser = erc_df[ur].values[row_idx] + str(counter)
                    therow.at[row_idx, cols[0]] = suffixedloser
                    for othercon in other_cons_with_Ls:
                        therow.at[row_idx, othercon] = ""

                    # erc_df.loc[len(erc_df.index)] = therow
                    rowstoadd.append(therow)

        new_erc_df = pd.concat([erc_df] + rowstoadd)
        # remove the rows with multiple Ls
        new_erc_df.drop(new_erc_df.index[rowindicestoremove], axis=0, inplace=True)
        return new_erc_df

    def removesupersets(self, erc_df):
        numrows = erc_df.shape[0]
        rowstoeliminate = []

        for i in range(numrows):
            for j in range(numrows):
                if i != j and i not in rowstoeliminate and j not in rowstoeliminate:  # so we don't make unecessary comparisons
                    superrow = []
                    for con in self.constraints:
                        if erc_df[con].iloc[i] == erc_df[con].iloc[j]:
                            superrow.append("equal")
                        elif erc_df[con].iloc[i] == "e" and erc_df[con].iloc[j] in ["W", "L"]:
                            superrow.append("j")
                        elif erc_df[con].iloc[j] == "e" and erc_df[con].iloc[i] in ["W", "L"]:
                            superrow.append("i")
                        else:  # one is "W" and the other is "L"
                            superrow.append("conflict")
                    if [result for result in superrow if result in ["equal", "i"]] == superrow:
                        # comparison list only contains "equal" and "i" results; this means "i" is a superset of "j"
                        rowstoeliminate.append(i)
                    elif [result for result in superrow if result in ["equal", "j"]] == superrow:
                        # comparison list only contains "equal" and "j" results; this means "j" is a superset of "i"
                        rowstoeliminate.append(j)
                    # else the comparison list contains conflicts,
                    # either at a single constraint (ie a "conflict" entry),
                    # or across constraints (ie "j" in one spot and "i" somewhere else):
                        # neither row can be eliminated
        erc_df.drop(rowstoeliminate, axis=0, inplace=True)
        return len(rowstoeliminate)

    def testgrammar(self, numtimes):
        forms = {}  # ur --> dict of [ candidate --> frequency ]
        for t in self.tableaux_list:
            # set up UR keys to track frequency of each output
            ur = t.columns[0]
            forms[ur] = {}
            for candidate in t[ur].values:
                forms[ur][candidate] = 0
        for i in range(numtimes):
            if i % 10 == 0:
                print("test lap ", i)
            shuffled_tableaux = random.sample(self.tableaux_list, len(self.tableaux_list))

            for tableau in shuffled_tableaux:
                evalweights = self.getevalweights(LEARNING_NOISE_F[-1], LEARNING_NOISE_M[-1])
                optimalout = evaluate_one(tableau, evalweights)
                ur = tableau.columns[0]
                forms[ur][optimalout] += 1
        forms_normalized = {}
        for ur in forms.keys():
            cands, freqs = zip(*list(forms[ur].items()))
            freqsum = sum(freqs)
            freqs = [f/freqsum for f in freqs]
            forms_normalized[ur] = freqs

        results_tableaux_list =[]
        for t in self.tableaux_list:
            results_t = t.copy()
            results_t.insert(2, "outputfrequency", forms_normalized[t.columns[0]])
            results_tableaux_list.append(results_t)

        return results_tableaux_list


# end of class Learner #


def getmaxdigit(conname):
    if "5" in conname: return 5
    elif "4" in conname: return 4
    elif "3" in conname: return 3
    elif "2" in conname: return 2
    elif "1" in conname: return 1
    else: return 0


def getmindigit(conname):
    if "1" in conname: return 1
    elif "2" in conname: return 2
    elif "3" in conname: return 3
    elif "4" in conname: return 4
    elif "5" in conname: return 5
    else: return 0


def getviolations(ur, candidate, cons, cellvalues, rules):
    violations = []
    for idx, cell in enumerate(cellvalues):
        numviolations = 0
        if re.match("\d+", str(cell)):
            # number of violations was explicitly assigned
            numviolations = int(cell)
        else:  # violation mark(s) hasn't been explicitly assigned
            constraint = cons[idx]
            if constraint in rules.keys():
                if rules[constraint][ctype] == f:
                    # do this twice: group1 --> group2, and then reverse
                    for direction in [0, 1]:
                        grp1 = rules[constraint][g1]
                        grp2 = rules[constraint][g2]
                        if direction == 1:
                            grp2 = rules[constraint][g1]
                            grp1 = rules[constraint][g2]
                        for in_substr in grp1:
                            numinstances = ur.count(in_substr)
                            i = -1
                            while numinstances > 0:
                                i = ur.index(in_substr, i+1)
                                cand_substr = candidate[i:i+len(in_substr)]
                                if cand_substr in grp2:
                                    numviolations += 1
                                numinstances -= 1
                else:  # it's m
                    numviolations = 0
                    for substring in rules[constraint][g1]:
                        numviolations += candidate.count(substring)
            else:
                # it's just empty
                numviolations = 0
        violations.append(numviolations)
    return violations


# tableax = dictionary of inputstring --> { dictionary of candidate --> list of violations }
def get_tableaux(tableaux, constraints):
    list_of_dfs = []
    for ur in tableaux.keys():
        list_of_dfs.append(get_tableau(ur, tableaux[ur], constraints))
    return list_of_dfs


# tableau = dictionary of candidate --> list of violations
def get_tableau(ur, tableau, constraints):
    df_lists = []
    for cand in tableau.keys():
        df_lists.append([cand]+[tableau[cand]["frequency"]]+tableau[cand]["violations"])
    df = pd.DataFrame(df_lists, columns=[ur]+["frequency"]+constraints)
    return df


# evalweights is a dictionary of constraint names --> evaluation weights
def evaluate_one(tableau_df, evalweights):

    ur = tableau_df.columns[0]
    candidate_contenders = [cand for cand in tableau_df[ur].values]

    wts = list(evalweights.items())  # make it a list of key-value pairs (tuples)
    wts.sort(key=lambda x: x[1], reverse=True)
    ranking = [c for (c, w) in wts]

    winner = ""
    idx = 0
    while winner == "" and idx < len(ranking):
        c = ranking[idx]
        violns = {}
        for bla, row in tableau_df.iterrows():
            viol = row[c]
            if viol not in violns.keys():
                violns[viol] = []
            violns[viol].append(row[ur])

        violations_category = 0
        existing_violn_numbers = sorted(list(violns.keys()))
        reduced = False
        while violations_category <= max(existing_violn_numbers) and winner == "" and not reduced:
            if violations_category in existing_violn_numbers:
                successful_cands = violns[violations_category]
                reduced_contenders = [c for c in candidate_contenders if c in successful_cands]
                if len(reduced_contenders) > 0:
                    candidate_contenders = reduced_contenders
                    reduced = True
                    if len(candidate_contenders) == 1:
                        # we have a winner!
                        winner = candidate_contenders[0]
            violations_category += 1
        idx += 1
    return winner

def sort_files_exps_list(files_exps):
    new_files_exps = []
    # for now, I want to sort by ones place (# trials/batch), then hundreds (which constraint set), then language
    for ones_digit in range(1, 6):
        for hundreds_digit in range(1, 7):
            for lang_code in ["NE", "Fi", "NS", "SS"]:
                new_files_exps.extend([fe for fe in files_exps if fe[1] == lang_code+str(hundreds_digit)+"0"+str(ones_digit)])
    return new_files_exps

def make_files_exps_list():
    files_exps = []
    ft = [False, True]
    for DEL in ft:
        for TRANSP in ft:
            for FTGRP in ft:
                for IXN in ft:
                    for IDFT in ft:
                        customizations = ""
                        customizations += "_widft" if IDFT else ""
                        customizations += "_wdel" if DEL else ""
                        if TRANSP:
                            customizations += "_wtr" + ("-grp" if FTGRP else "-ind")
                        customizations += "_ixn" if IXN else ""

                        for numtrials_id in LEARNING_TRIALS_DICT.keys():
                            ones_place = str(numtrials_id)

                            hundreds_place = "x"
                            if not DEL and not TRANSP and not FTGRP and not IXN:
                                hundreds_place = "1"
                            elif DEL and not TRANSP and not FTGRP and IXN:
                                hundreds_place = "2"
                            elif not DEL and TRANSP and FTGRP and IXN:
                                hundreds_place = "3"
                            elif not DEL and TRANSP and not FTGRP and IXN:
                                hundreds_place = "4"
                            elif DEL and TRANSP and FTGRP and IXN:
                                hundreds_place = "5"
                            elif DEL and TRANSP and not FTGRP and IXN:
                                hundreds_place = "6"
                            if hundreds_place != "x":
                                tens_place = "0"

                                for lang in langnames:
                                    lang_code = lang[:2]

                                    filename = "OTSoft-PDDP-" + lang + "_GLA" + customizations + ".txt"
                                    files_exps.append((filename, lang_code+hundreds_place+tens_place+ones_place))
    return files_exps


def justtests(skipifalreadydone=True):
    files_exps = {
        'NE': ('OTSoft-PDDP-NEst_GLA.txt', 'NE894'),
        'Fi': ('OTSoft-PDDP-Fin_GLA.txt', 'Fi894'),
        'NS': ('OTSoft-PDDP-NSeto_GLA.txt', 'NS894'),
    }

    resultsfolders = os.listdir(OUTPUTS_DIR)
    resultsfolders = [fol for fol in resultsfolders if os.path.isdir(os.path.join(OUTPUTS_DIR, fol))]   #  if "testycopy" in fol]  # if fol.startswith("T_Mgen")]
    numfolders = len(resultsfolders)

    for idx, fol in enumerate(resultsfolders):
        print("folder", idx+1, "of", numfolders)
        resultsfile = os.listdir(os.path.join(OUTPUTS_DIR, fol))
        resultsfile = [fi for fi in resultsfile if "RESULTS" in fi][0]
        if "Fin" in resultsfile:
            inputsfile = files_exps['Fi'][0]
        elif "NEst" in resultsfile:
            inputsfile = files_exps['NE'][0]
        elif 'NSeto' in resultsfile:
            inputsfile = files_exps['NS'][0]

        testresultsfilename = os.path.join(fol, resultsfile.replace("RESULTS", "TESTS"))
        if os.path.exists(os.path.join(OUTPUTS_DIR, testresultsfilename)) and skipifalreadydone:
            print("skipping; already done:", testresultsfilename)
            continue

        learner = Learner(srcfilepath=DATA_DIR + "/" + inputsfile, destdir="", expnum="xx123")
        tableaux = learner.read_input()
        learner.set_tableaux(get_tableaux(tableaux, learner.constraints))

        # read weights from grammar file
        finalweights = readfinalweightsfromgrammar(os.path.join(OUTPUTS_DIR, fol, resultsfile))
        if not finalweights:
            print("skipping; file not found (probably name is too long):", testresultsfilename)
            continue

        learner.weights = finalweights

        with io.open(os.path.join(OUTPUTS_DIR, testresultsfilename), "w") as testresultsfile:
            starttime = datetime.now()

            testresultsfile.write("\n--------------- RESULTS ---------------------\n\n")
            for con in learner.weights.keys():
                testresultsfile.write(con + "\t" + str(learner.weights[con]) + "\n")

            print("\n--------------- BEGIN TEST ---------------------")
            print(testresultsfilename + "\n")
            testresultsfile.write("\n--------------- BEGIN TEST ---------------------\n\n")
            testresults = learner.testgrammar(100)  # 100
            for results_t in testresults:
                ordered_t = results_t.reindex([results_t.columns[0]]+list(results_t.columns[1:3])+list(finalweights.keys()), axis=1)
                testresultsfile.write(ordered_t.to_string(index=False) + "\n\n")

            endtime = datetime.now()
            print("time elapsed", endtime-starttime)
            testresultsfile.write("time elapsed: " + str(endtime-starttime))


def readfinalweightsfromgrammar(filepath):
    finalweights = {}
    try:
        with io.open(filepath, "r") as grammarfile:
            inresults = False
            done = False
            ln = grammarfile.readline()
            while ln != "" and not done:
                ln = ln.strip()
                if not inresults:
                    if "--------------- RESULTS ----------------" in ln:
                        inresults = True
                    else:
                        pass  # just go on to the next line
                else:  # we're in the results section; read a constraint name and its final ranking value
                    if ln != "":
                        if "rounded" in ln:
                            # we're done with results
                            done = True
                        else:
                            items = ln.split()
                            conname = items[0]
                            conweight = items[-1]
                            finalweights[conname] = float(conweight)
                    else:
                        pass  # just go on to the next line

                ln = grammarfile.readline()
    except FileNotFoundError:
        pass
    return finalweights


def main(prefix="", argstuple=None):
    # files_exps = make_files_exps_list()
    # files_exps = sort_files_exps_list(files_exps)
    files_exps = [
        ('OTSoft-PDDP-NEst_GLA.txt', 'NE894'),
        ('OTSoft-PDDP-Fin_GLA.txt', 'Fi894'),
        ('OTSoft-PDDP-NSeto_GLA.txt', 'NS894'),

        # ('OTSoft-PDDP-NEst_GLA.txt', 'NE893'),
        # ('OTSoft-PDDP-Fin_GLA.txt', 'Fi893'),
        # ('OTSoft-PDDP-NSeto_GLA.txt', 'NS893'),
        # ('OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn.txt', 'Fi994'),
        # ('OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn.txt', 'NE994'),
        # ('OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn.txt', 'NE883'),
        # ('OTSoft-PDDP-Fin_GLA_wdel-gen-ne_ixn.txt', 'Fi883'),
        # ('OTSoft-PDDP-NEst_GLA_wdel-gen-ne_ixn.txt', 'NE993'),
        # ('OTSoft-PDDP-NSeto_GLA_wdel-gen-ne_ixn.txt', 'NS993'),
        # ('OTSoft-PDDP-SSeto_GLA_wdel-gen-ne_ixn.txt', 'SS993')
    ]
    for fe in files_exps:
        print(fe)

    for fname, expnum in files_exps:
        # DATA_DIR  # firstdir = fname[:fname.index("\\")]
        # fname   # datafilename = fname[fname.index("\\")+1:]
        resultsdir = prefix + expnum + "_python_" + fname.replace(".txt", "")

        print("running " + expnum + " simulation for file", fname)
        resultsdirpath = WORKING_DIR + "/" + resultsdir
        if os.path.exists(resultsdirpath):
            print("results folder for " + expnum + " already exists; skipping!")
        else:
            os.mkdir(resultsdirpath)
            # DATA_DIR = WORKING_DIR + "/20240117_forOTS"  # + "_wdel-gen-ne_ixn"
            onesimulation(srcfilepath=DATA_DIR + "/" + fname, destdir=resultsdirpath, expnum=expnum, argstuple=argstuple)

        # DATA_DIR = WORKING_DIR + "/20240117_forOTS" + ("_wdel-gen-ne_ixn" if "ixn" in resultsdirpath else "")
        # onesimulation(srcfilepath=DATA_DIR + "/" + fname, destdir=resultsdirpath, expnum=expnum)


def onesimulation(srcfilepath, destdir, expnum, argstuple=None):
    starttime = datetime.now()
    if argstuple is None:
        learner = Learner(srcfilepath, destdir, expnum, demoteunlyundominatedlosers=DEMOTEONLYUNDOMINATEDLOSERS, magri=MAGRI, magritype=MAGRITYPE, specgenbias=SPECGENBIAS, gravity=GRAVITY, gravityconst=GRAVITYCONST, preferspecificity=PREFERSPECIFICITY, expandingbias=EXPANDINGBIAS, expandslowly=EXPANDSLOWLY, expandslowlydecreasingrate=EXPANDSLOWLYDECREASINGRATE, initrankingswMgen_type=INITRANKINGSWMGEN, initMrankings_whichcand="faithful", initMrankings_calchow="sum", relu=RELU)
    else:
        learner = Learner(srcfilepath, destdir, expnum, *argstuple)

    tableaux = learner.read_input()
    learner.set_tableaux(get_tableaux(tableaux, learner.constraints))

    # testweights = {}
    # for c in constraints:
    #     testweights[c] = random.randint(0, 1000000)
    # print(tableaux_list[46])
    # print(sorted(testweights.items(), key=lambda x: x[1], reverse=True))
    # print(evaluate_one(tableaux_list[46], testweights))
    #
    # if learner.initrankingswMgen > 0:
    #     print("--------------- BEGIN M GENERALITY CALCULATIONS ---------------------")
    #
    #     if 0 < learner.initrankingswMgen < 1:
    #         pass
    #     elif 1 <= learner.initrankingswMgen < 2:
    #         pass
    #     elif 2 <= learner.initrankingswMgen < 3:
    #         pass
    #     elif 3 <= learner.initrankingswMgen < 4:
    #         pass
    #     elif 4 <= learner.initrankingswMgen < 5:
    #         pass



    # print("--------------- BEGIN TRAIN ---------------------")
    learner.train()

    with io.open(learner.resultsfile, "w") as rf:
        datestring = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        rf.write(datestring + "\n")
        rf.write("input file: " + srcfilepath + "\n")

        rf.write("\n--------------- PARAMETERS ---------------------\n")
        rf.write("Magri update used: " + (("yes (type " + str(learner.magritype) + ")") if learner.magri else "no") + "\n")
        rf.write("Gravity used: " + (("yes (every " + str(learner.gravityconst) + " errors)") if learner.gravity else "no") + "\n")
        rf.write("Prefer specificity: " + ("yes" if learner.preferspecificity else "no") + "\n")
        rf.write("specific > general bias: " + (str(learner.specgenbias) if learner.specgenbias >= 0 else "no") + "\n")
        rf.write("*expanding* specific > general bias: " + (("yes (" + (("slowly" + ("/decreasing" if learner.expandslowlydecreasingrate else "/constant")) if learner.expandslowly else "regular speed") + ")") if learner.expandingbias else "no") + "\n")
        rf.write("demote " + ("only undominated" if learner.demoteunlyundominatedlosers else "all") + " losers\n")
        rf.write("learning trials, listed by batch: " + str(learner.learning_trials) + "\n")
        rf.write("markedness plasticity, listed by batch: " + str(LEARNING_R_M) + "\n")
        rf.write("markedness noise, listed by batch: " + str(LEARNING_NOISE_M) + "\n")
        rf.write("faithfulness plasticity, listed by batch: " + str(LEARNING_R_F) + "\n")
        rf.write("faithfulness noise, listed by batch: " + str(LEARNING_NOISE_F) + "\n")
        if len(INIT_WEIGHTS.keys()) > 0:
            rf.write("initial weights: " + str(INIT_WEIGHTS) + "\n")
        elif learner.initrankingswMgen_int > 0:
            initwtstr = "initial markedness weights based on generality (type "
            initwtstr += learner.initrankingswMgen_type
            initwtstr += " - calc by " + learner.initMrankings_calchow
            initwtstr += " of " + learner.initMrankings_whichcand + " candidates); "
            initwtstr += "initial faithfulness weights = " + str(INIT_F)
            rf.write(initwtstr)
            # rf.write("initial markedness weights based on generality (type " + str(learner.initrankingswMgen) + "); initial faithfulness weights = " + str(INIT_F))
        else:
            rf.write("initial markedness weights = " + str(INIT_M) + "; initial faithfulness weights = " + str(INIT_F))

        rf.write("\n")

        print("\n--------------- RESULTS ---------------------\n")
        rf.write("\n--------------- RESULTS ---------------------\n\n")
        finalweights = list(learner.weights.items())
        finalweights.sort(key=lambda x: x[1], reverse=True)
        cons, weights = zip(*finalweights)
        for idx, con in enumerate(cons):
            rf.write(con + "\t" + str(weights[idx]) + "\n")
        print("\nrounded:")
        rf.write("\nrounded:\n")
        for idx, con in enumerate(cons):
            roundedstring = str(round(weights[idx], 3))
            print(con + "\t" + roundedstring)
            rf.write(con + "\t" + roundedstring + "\n")


        # print("\n--------------- OMIT TEST ---------------------")
        print("\n--------------- BEGIN TEST ---------------------\n")
        rf.write("\n--------------- BEGIN TEST ---------------------\n\n")
        testresults = learner.testgrammar(10)  # 100
        for results_t in testresults:
            ordered_t = results_t.reindex([results_t.columns[0]]+list(results_t.columns[1:3])+list(cons), axis=1)
            rf.write(ordered_t.to_string(index=False) + "\n\n")

        endtime = datetime.now()
        print("time elapsed", endtime-starttime)
        rf.write("time elapsed: " + str(endtime-starttime))


def may2024combinations():
    for demoteonlyundominatedlosers in [False]:  # , True]:  # , True]:
        for magri in [False, True]:
            for magritype in [2, 3, 4] if magri else [0]:  # [1, 2, 3]
                for gravity in [False]:  # [True]:  # , False]:
                    for gravityconst in [2] if gravity else [0]:
                        for preferspecificity in [True]:
                            for specgenbias in [20, 35]:  # , 20, 30]:  # -1, 0, 20, 30]:
                                for expandingbias in [False]:  # , True] if specgenbias >= 0 else [False]:
                                    for expandingslowly in [True] if expandingbias else [False]:  # [False, True]
                                        for expandslowlydecreasingrate in [True] if expandingslowly else [False]:
                                            for initrankingswMgen in [1.2, 2.1, 3.1]:  # [1.1, 1.2, 2.1, 3.1]:  # [True]:
                                                for initMrankingscalcbysums in [True, False] if initrankingswMgen > 0 else [True]:
                                                    abbrevstr = "T_"  # tested  # "NIT_"  # no inputs with initial-syl transparent vowels
                                                    abbrevstr += "UnL_" if demoteonlyundominatedlosers else ""
                                                    if initrankingswMgen > 0:
                                                        abbrevstr += "Mgen" + initrankingswMgen + ("s" if initMrankingscalcbysums else "a") + "_"
                                                    else:
                                                        abbrevstr += "M" + str(INIT_M) + "_"
                                                    # abbrevstr += "Mgen" + initrankingswMgen + "_" if initrankingswMgen > 0 else ""
                                                    abbrevstr += ("mg" + str(magritype) + "_") if magri else ""
                                                    abbrevstr += "gr_" if gravity else ""
                                                    abbrevstr += "fs_" if preferspecificity else ""
                                                    if specgenbias >= 0:
                                                        abbrevstr += "sg" + str(specgenbias) + "_"
                                                        if expandingbias:
                                                            abbrevstr += "ex" + (("-s" + ("-d" if expandslowlydecreasingrate else "")) if expandingslowly else "-r") + "_"
                                                    print(abbrevstr)
                                                    # fs_sg20_ex - r
                                                    main(prefix=abbrevstr, argstuple=(demoteonlyundominatedlosers, magri, magritype, specgenbias, gravity, gravityconst, preferspecificity, expandingbias, expandingslowly, expandslowlydecreasingrate, initrankingswMgen, initMrankingscalcbysums, True))


def onespecificthing():
    for demoteonlyundominatedlosers in [False, True]:  # , True]:  # , True]:
        for magri in [False, True]:  # , True]:
            for magritype in [1, 2, 3, 4] if magri else [0]:  # [1, 2, 3]
                for gravity in [False]:  # [True]:  # , False]:
                    for gravityconst in [2] if gravity else [0]:
                        for preferspecificity in [False, True]:  # , True]:
                            for specgenbias in [-1, 0, 20, 30, 40]:  # [20, 25, 30, 35, 40]:  # , 20, 30]:  # -1, 0, 20, 30]:
                                for expandingbias in [False]:  # , True] if specgenbias >= 0 else [False]:
                                    for expandingslowly in [True] if expandingbias else [False]:  # [False, True]
                                        for expandslowlydecreasingrate in [True] if expandingslowly else [False]:
                                            for initrankingswMgen_type in ["1.050.050", "1.050.100", "1.100.050", "1.100.100", "1.150.050", "1.150.100"]:
                                                for initMrankings_whichcand in ["faithful", "random", "all"]:
                                                    for initMrankings_calchow in ["sum", "average"] if initMrankings_whichcand == "all" else ["sum"]:
                                                        for ReLU in [False, True]:
                                                            abbrevstr = "N_"  # not tested
                                                            abbrevstr += "UnL_" if demoteonlyundominatedlosers else ""
                                                            if int(initrankingswMgen_type[0]) > 0:
                                                                abbrevstr += "Mgen" + initrankingswMgen_type
                                                                abbrevstr += initMrankings_whichcand[0] + initMrankings_calchow[0] + "_"
                                                            else:
                                                                abbrevstr += "M" + str(INIT_M) + "_"
                                                            # abbrevstr += "Mgen" + initrankingswMgen + "_" if initrankingswMgen > 0 else ""
                                                            abbrevstr += ("mg" + str(magritype) + "_") if magri else ""
                                                            abbrevstr += "gr_" if gravity else ""
                                                            abbrevstr += "fs_" if preferspecificity else ""
                                                            if specgenbias >= 0:
                                                                abbrevstr += "sg" + str(specgenbias) + "_"
                                                                if expandingbias:
                                                                    abbrevstr += "ex" + (("-s" + ("-d" if expandslowlydecreasingrate else "")) if expandingslowly else "-r") + "_"
                                                            if ReLU:
                                                                abbrevstr += "ReLU_"
                                                            print(abbrevstr)
                                                            # fs_sg20_ex - r
                                                            main(prefix=abbrevstr, argstuple=(demoteonlyundominatedlosers, magri, magritype, specgenbias, gravity, gravityconst, preferspecificity, expandingbias, expandingslowly, expandslowlydecreasingrate, initrankingswMgen_type, initMrankings_whichcand, initMrankings_calchow, ReLU))


def startwithMgen():
    gravity = False
    gravityconst = 0
    for initrankingswMgen in ["TODO these have to be strings now"]:
        for initMrankingscalcbysums in [True, False] if int(initrankingswMgen[0]) > 0 else [True]:
            for specgenbias in [-1, 0, 10, 20, 30, 40]:
                for favourspecificity in [False, True]:
                    for magri in [False, True]:
                        for magritype in [1, 2, 3, 4] if magri else [0]:
                            for expandingbias in [False, True] if specgenbias >= 0 else [False]:
                                for expandingslowly in [False, True] if expandingbias else [False]:
                                    for expandslowlydecreasingrate in [False, True] if expandingslowly else [False]:
                                        for demoteonlyundominatedlosers in [False, True]:
                                            for ReLU in [True]:
                                                abbrevstr = "T_"  # tested  # "NIT_"  # no inputs with initial-syl transparent vowels
                                                abbrevstr += "UnL_" if demoteonlyundominatedlosers else ""
                                                if int(initrankingswMgen[0]) > 0:
                                                    abbrevstr += "Mgen" + initrankingswMgen + ("s" if initMrankingscalcbysums else "a") + "_"
                                                else:
                                                    abbrevstr += "M" + str(INIT_M) + "_"
                                                # abbrevstr += "Mgen" + initrankingswMgen + "_" if initrankingswMgen > 0 else ""
                                                abbrevstr += ("mg" + str(magritype) + "_") if magri else ""
                                                # abbrevstr += "gr_" if gravity else ""
                                                abbrevstr += "fs_" if favourspecificity else ""
                                                if specgenbias >= 0:
                                                    abbrevstr += "sg" + str(specgenbias) + "_"
                                                    if expandingbias:
                                                        abbrevstr += "ex" + (("-s" + (
                                                            "-d" if expandslowlydecreasingrate else "")) if expandingslowly else "-r") + "_"
                                                if ReLU:
                                                    abbrevstr += "ReLU_"
                                                print(abbrevstr)
                                                # fs_sg20_ex - r
                                                main(prefix=abbrevstr,
                                                     argstuple=(demoteonlyundominatedlosers, magri, magritype, specgenbias,
                                                                gravity, gravityconst, favourspecificity, expandingbias,
                                                                expandingslowly, expandslowlydecreasingrate,
                                                                initrankingswMgen, initMrankingscalcbysums, ReLU)
                                                     )


if __name__ == "__main__":
    # main()
    # may2024combinations()
    onespecificthing()
    # justtests(skipifalreadydone=True)

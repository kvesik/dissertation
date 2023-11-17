import io
import pandas as pd
import re
import os
import random
import numpy as np
from datetime import datetime
from generate_tableaux_otsoft_specifylang import langnames


# star_F = "*F"
# star_7 = "*õ"
# IdBkSyl1 = "Id(Bk)Syl1"
# IdBkRt = "Id(Bk)"
# AgrBk = "Agr(Bk)"
# # CMHF = "CMHF"
# GMHF = "GMHF"
# # GMHF_wd = "GMHF(wd)"
# # GMHF_subwd = "GMHF(subwd)"
# star_e = "*e"
# # CMHe = "CMHe"
# GMHe = "GMHe"
# # GMHe_wd = "GMHe(wd)"
# # GMHe_subwd = "GMHe(subwd)"
# # CMH7 = "CMHõ"
# GMH7 = "GMHõ"
# # GMH7_wd = "GMHõ(wd)"
# # GMH7_subwd = "GMHõ(subwd)"


INIT_WEIGHTS = {}
INIT_F = 0
INIT_M = 100

# FILE = "C:\Program Files\OTSoft2.6\KE_iFBfb_posonly_negtest_cat_KPplus_wd_noC.txt"
# FILE = "C:\Program Files\OTSoft2.6\KE_iFBfb_posonly_negtest_var_KPplus_wd_noC.txt"
# FILE = "C:\Program Files\OTSoft2.6\SE_iFBfb_posonly_negtest_KPplus_wd_noC.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OTSoft_KE_iFBfb_forGLA_cat_QP2cons.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OTSoft_SE_iFBfb_forGLA_cat_QP2cons_flat.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OT_Soft_SE_iFBfb_forGLA_cat_QP2cons_no2xcounts.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OT_Soft_KE_iFBfb_forGLA_cat_starBQP2cons_no2xcounts.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OTSoft_SE_iFBfb_forLFCD_cat_removeGMHQP2cons_no2xcounts.txt"
# FILE = "C:\Program Files\OTSoft2.6old\OTSoft_SE_GLA_stringencycons3.txt"
# FILES = [
#     "OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files\OTSoft_simpleFin_GLA_PDDP_nodia.txt",
#     "OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files\OTSoft_simpleNEst_GLA_PDDP_nodia.txt",
#     "OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files\OTSoft_simpleSSeto_GLA_PDDP_nodia.txt",
#     "OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files\OTSoft_simpleNSeto_GLA_PDDP_nodia.txt",
# ]
WORKING_DIR = "OTSoft2.6old"
DATA_DIR = WORKING_DIR + "/20231107MagriRuns"

# FILES_EXPS = [
#     ("OTSoft-PDDP-NEst_GLA_wdel_wtr-grp_ixn.txt", ""),
#     ("OTSoft_Fin_GLA_PDDP_nodia.txt", "Fi153"),
#     ("OTSoft_NEst_GLA_PDDP_nodia.txt", "NE153"),
#     ("OTSoft_NSeto_GLA_PDDP_nodia.txt", "NS153"),
#     ("OTSoft_SSeto_GLA_PDDP_nodia.txt", "SS153"),
# ]
MAGRI = True
# magritype =
    #   1 if original update rule from Magri 2012: numdemotions / (1 + numpromotions)
    #   2 if 1 / numpromotions
    #   3 if numdemotions / (numdemotions + numpromotions)
MAGRITYPE = 1
SPECGENBIAS = 20
# SPECGENCONS = [("Id(Bk)Syl1", "Id(Bk)")]
SPECGENCONS = [
    ("Id(Bk)Syl1", "Id(Bk)"),
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

# SPECCON = "Id(Bk)Syl1"
# GENCON = "Id(Bk)"
# LEARNING_TRIALS = [10,10,10,10]  #, 100, 100, 100]
# LEARNING_TRIALS = [1000, 1000, 1000, 1000]  # [5000, 5000, 5000, 5000]
# EXPNUM = "R003"
# LEARNING_R_F = [2, 2, 2, 2]  # 0.2, 0.02, 0.002]
# LEARNING_R_M = [2, 2, 2, 2]  # 0.2, 0.02, 0.002]
# LEARNING_R_F = [1, 0.215, 0.046, 0.010]  # [2, 0.2, 0.02, 0.002]
# LEARNING_R_M = [1, 0.215, 0.046, 0.010]  # [2, 0.2, 0.02, 0.002]
LEARNING_R_F = [2, 0.2, 0.02, 0.002]
LEARNING_R_M = [2, 0.2, 0.02, 0.002]
# LEARNING_R_F = [3, 0.3, 0.03, 0.003]
# LEARNING_R_M = [0.2, 0.02, 0.002, 0.0002]
# LEARNING_R_F = [0.2, 0.02, 0.002, 0.0002]
# LEARNING_R_M = [3, 0.3, 0.03, 0.003]
# LEARNING_R_F = [1, 0.1, 0.01, 0.001]
# LEARNING_R_M = [1, 0.1, 0.01, 0.001]
# LEARNING_R_F = [0.2,0.2,0.2,0.2]
# LEARNING_R_M = [2,2,2,2]
LEARNING_NOISE_F = [2, 2, 2, 2]  # [2, 0.2, 0.02, 0.002]  # [2, 2, 2, 2]
LEARNING_NOISE_M = [2, 2, 2, 2]  # [2, 0.2, 0.02, 0.002]  # [2, 2, 2, 2]

m = "markedness"
f = "faithfulness"
ctype = "constraint type"
g1 = "group 1 strings"
g2 = "group 2 strings"


class Learner:

    # magritype =
    #   1 if original update rule from Magri 2012: numdemotions / (1 + numpromotions)
    #   2 if 1 / numpromotions
    #   3 if numdemotions / (numdemotions + numpromotions)
    def __init__(self, srcfilepath, destdir, expnum, magri=True, magritype=1, specgenbias=0):
        numtrials_id = int(expnum[-1])
        self.learning_trials = LEARNING_TRIALS_DICT[numtrials_id]
        self.file = srcfilepath
        srcfilename = srcfilepath[srcfilepath.rfind("/") + 1:]
        destfiletemplate = destdir + "/" + expnum + " - " + srcfilename
        # self.historyfile = destfiletemplate.replace(".txt", "_HISTORY" + str(LEARNING_TRIALS[0]) + ".txt")
        # self.resultsfile = destfiletemplate.replace(".txt", "_RESULTS" + str(LEARNING_TRIALS[0]) + ".txt")
        self.historyfile = destfiletemplate.replace(".txt", "_HISTORY" + str(self.learning_trials[0]) + ".txt")
        self.resultsfile = destfiletemplate.replace(".txt", "_RESULTS" + str(self.learning_trials[0]) + ".txt")

        # if expnum is not None and expnum != "":
        #     afterlastslash = self.file.rfind("/") + 1
        #     self.historyfile = self.historyfile[0:afterlastslash] + expnum + " - " + self.historyfile[afterlastslash:]
        #     self.resultsfile = self.resultsfile[0:afterlastslash] + expnum + " - " + self.resultsfile[afterlastslash:]
        self.magri = magri
        self.magritype = magritype
        self.constraints = []
        self.weights = {}
        self.tableaux_list = []
        self.training_tableaux_list = []
        self.specgenbias = specgenbias

    def set_tableaux(self, tableaux_list):
        self.tableaux_list = tableaux_list
        # only try and learn from the tableaux that have input frequency information
        self.training_tableaux_list = [t for t in tableaux_list if sum(t["frequency"].values) > 0]

    def read_input(self):
        with io.open(self.file, "r") as infile:
            df = pd.read_csv(infile, sep="\t", header=1, keep_default_na=False)
            # print(df.columns)
            df.rename(
                columns=({'Unnamed: 0': 'input', 'Unnamed: 1': 'candidate', 'Unnamed: 2': 'frequency'}),
                inplace=True,
            )

            rules = {}
            # print(df.columns)
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
                # if row["input"] != "" and len(cur_tableau.keys()) > 0:
                #     # save previous input's tableau
                #     tableaux[cur_input] = cur_tableau
                #
                #     # # start a new tableau
                #     # cur_input = row["input"]
                #     # cur_tableau = {}

                cur_violations = getviolations(cur_input, cur_candidate, list(df.columns[3:]), row[3:], rules)
                cur_tableau[cur_candidate] = {}
                cur_tableau[cur_candidate]["frequency"] = cur_frequency
                cur_tableau[cur_candidate]["violations"] = cur_violations

            # save the final input's tableau
            tableaux[cur_input] = cur_tableau

        # return tableaux, list(df.columns[3:])
        self.constraints = list(df.columns[3:])

        # initialize constraint set and weights
        if len(INIT_WEIGHTS.keys()) > 0:
            # initial weights have been specified; use them
            for con in self.constraints:
                self.weights[con] = INIT_WEIGHTS[con]
                # in theory could just assign the dictionary wholesale but order could be relevant somewhere else...
        else:
            # no initial weights have been specified; start from scratch
            for con in self.constraints:
                if con.startswith("Id") or con.startswith("Max"):  # or a bunch of other stuff, but this is the only kind relevant to me
                    # it's a faith constraint
                    self.weights[con] = INIT_F
                else:
                    # it's a markedness constraint
                    self.weights[con] = INIT_M

        return tableaux

    def train(self):
        # put headers into history file
        # headertowrite = "lap num" + "\t" + "generated" + "\t" + "heard"
        headertowrite = "trial num" + "\t" + "generated" + "\t" + "heard"
        startvalstowrite = "" + "\t" + "" + "\t" + ""
        headertowrite += "".join(["\t" + c + "\tnow" for c in self.constraints]) + "\n"
        startvalstowrite += "".join(["\t\t" + str(self.weights[c]) for c in self.constraints]) + "\n"
        # for c in self.constraints:
        #     headertowrite += "\t" + c + "\t" + "now"
        #     startvalstowrite += "\t" + "\t" + str(self.weights[c])
        # headertowrite += "\n"
        # startvalstowrite += "\n"
        with io.open(self.historyfile, "w") as history:
            history.write(headertowrite)
            history.write(startvalstowrite)

            # do any necessary shuffling re a priori rankings right away
            for speccon, gencon in [pairofcons for pairofcons in SPECGENCONS if pairofcons[0] in self.weights.keys() and pairofcons[1] in self.weights.keys()]:  # SPECGENCONS:
                if self.specgenbias > 0 and round(self.weights[speccon], 10) < round(self.weights[gencon] + self.specgenbias, 10):
                    # print("updating a priori-- syl1 weight ", self.weights[IdBkSyl1], "; rt weight ", self.weights[IdBkRt], "; sum ", self.weights[IdBkRt] + self.specgenbias)
                    apriori_adjust = self.weights[gencon] + self.specgenbias - self.weights[speccon]
                    self.weights[speccon] = self.weights[gencon] + self.specgenbias

                    linetowrite = "" + "\t" + "a priori" + "\t" + speccon + ">>" + gencon + "\t"
                    for con in self.constraints:
                        if con != speccon or self.specgenbias == 0:
                            linetowrite += "\t\t"
                        else:  # SPEC_GEN_BIAS != 0
                            linetowrite += str(apriori_adjust) + "\t" + str(self.weights[speccon])
                    linetowrite += "\n"
                    history.write(linetowrite)

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

    def updateweights(self, tableau_df, intendedwinner, generatedoutput, cur_R_F, cur_R_M, lap_count, historystream):
        winner_df = tableau_df[tableau_df[tableau_df.columns[0]] == intendedwinner]
        optimal_df = tableau_df[tableau_df[tableau_df.columns[0]] == generatedoutput]

        adjustments = {}
        promotion_ratio = 1

        # demotion amount as usual
        # promotion amount = (# constraints demoted)/(1 + # constraints promoted)
        numpromoted = 0
        numdemoted = 0
        for c in self.constraints:
            w = winner_df[c].values[0]
            o = optimal_df[c].values[0]
            if w > 0 and o > 0:
                # cancel out violations - just look at relative difference
                overlap = min([w, o])
                w -= overlap
                o -= overlap
            if w > 0:
                # if self.magri:
                #     numdemoted += 1
                numdemoted += 1  # for Magri update
                adjustments[c] = -1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
            elif o > 0:
                # if self.magri:
                #     numpromoted += 1
                numpromoted += 1  # for Magri update
                adjustments[c] = 1 * (cur_R_F if (c.startswith("Id") or c.startswith("Max")) else cur_R_M)
        if self.magri:
            # magritype =
            #   1 if original update rule from Magri 2012: numdemotions / (1 + numpromotions)
            #   2 if 1 / numpromotions
            #   3 if numdemotions / (numdemotions + numpromotions)
            if self.magritype == 1:
                promotion_ratio = numdemoted / (1 + numpromoted)
            elif self.magritype == 2:
                promotion_ratio = 1 / numpromoted
            elif self.magritype == 3:
                promotion_ratio = numdemoted / (numdemoted + numpromoted)
            if numdemoted == 0:
                # print("numdemoted == 0. intended winner is ", intendedwinner, " and optimal loser is ", generatedoutput, "adjustments are ", adjustments)
                print(winner_df)
                print(optimal_df)

        linetowrite = str(lap_count) + "\t" + generatedoutput + "\t" + intendedwinner
        for con in self.constraints:
            if con in adjustments.keys():
                adjustment_amount = adjustments[con]
                if adjustment_amount > 0:
                    adjustment_amount *= promotion_ratio
                linetowrite += "\t" + str(adjustment_amount)
                self.weights[con] = self.weights[con] + adjustment_amount
                linetowrite += "\t" + str(self.weights[con])
            else:
                linetowrite += "\t\t"
        linetowrite += "\n"

        # with io.open(self.historyfile, "a") as history:
        historystream.write(linetowrite)

        for speccon, gencon in [pairofcons for pairofcons in SPECGENCONS if pairofcons[0] in self.weights.keys() and pairofcons[1] in self.weights.keys()]:  # SPECGENCONS:
            if self.specgenbias > 0 and round(self.weights[speccon], 10) < round(self.weights[gencon] + self.specgenbias, 10):
                # print("updating a priori-- syl1 weight ", self.weights[IdBkSyl1], "; rt weight ", self.weights[IdBkRt], "; sum ", self.weights[IdBkRt] + self.specgenbias)
                apriori_adjust = self.weights[gencon] + self.specgenbias - self.weights[speccon]
                self.weights[speccon] = self.weights[gencon] + self.specgenbias

                linetowrite = "" + "\t" + "a priori" + "\t" + speccon + ">>" + gencon + "\t"
                for con in self.constraints:
                    if con != speccon or self.specgenbias == 0:
                        linetowrite += "\t\t"
                    else:  # SPEC_GEN_BIAS != 0
                        linetowrite += str(apriori_adjust) + "\t" + str(self.weights[speccon])
                linetowrite += "\n"
                historystream.write(linetowrite)

    def learn(self, tableau_df, cur_R_F, cur_R_M, cur_noise_F, cur_noise_M, lap_count, historystream):
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

        # generate the optimal candidate based on current constraint weights (ranking), with or without noise
        evalweights = self.getevalweights(cur_noise_F, cur_noise_M)
        optimal_cand = evaluate_one(tableau_df, evalweights)

        # if the optimal candidate matches the intended winner, do nothing

        # if the optimal candidate does not match the intended winner, update the weights
        if datum != optimal_cand:
            self.updateweights(tableau_df, datum, optimal_cand, cur_R_F, cur_R_M, lap_count, historystream)

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
            # print(results_t)

        return results_tableaux_list


# end of class Learner #


def getviolations(ur, candidate, cons, cellvalues, rules):
    violations = []
    for idx, cell in enumerate(cellvalues):
        numviolations = 0
        # print(cell)
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
    # df = make_tableau_df(tableau)
    df_lists = []
    for cand in tableau.keys():
        df_lists.append([cand]+[tableau[cand]["frequency"]]+tableau[cand]["violations"])
    df = pd.DataFrame(df_lists, columns=[ur]+["frequency"]+constraints)
    return df


# evalweights is a dictionary of constraint names --> evaluation weights
def evaluate_one(tableau_df, evalweights):

    ur = tableau_df.columns[0]
    winner = ""
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

        # print(c, violns)
        violations_category = 0
        existing_violn_numbers = sorted(list(violns.keys()))
        # print("existing violn #s", existing_violn_numbers)
        reduced = False
        while violations_category <= max(existing_violn_numbers) and winner == "" and not reduced:
            if violations_category in existing_violn_numbers:
                successful_cands = violns[violations_category]
                reduced_contenders = [c for c in candidate_contenders if c in successful_cands]
                # print("reduced contenders", reduced_contenders)
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
    # for now, I want to sort by ones place, then hundreds, then language
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
                    customizations = ""
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


def main():
    # files_exps = make_files_exps_list()
    # files_exps = sort_files_exps_list(files_exps)
    files_exps = [
        ('OTSoft-PDDP-NEst_GLA.txt', 'NE153'),
        ('OTSoft-PDDP-Fin_GLA.txt', 'Fi153')
    ]
    for fe in files_exps:
        print(fe)

    for fname, expnum in files_exps:
        # DATA_DIR  # firstdir = fname[:fname.index("\\")]
        # fname   # datafilename = fname[fname.index("\\")+1:]
        resultsdir = expnum + " - python - " + fname.replace(".txt", "")

        print("running " + expnum + " simulation for file", fname)
        resultsdirpath = WORKING_DIR + "/" + resultsdir
        if os.path.exists(resultsdirpath):
            print("results folder for " + expnum + " already exists; skipping!")
        else:
            os.mkdir(resultsdirpath)
            onesimulation(srcfilepath=DATA_DIR + "/" + fname, destdir=resultsdirpath, expnum=expnum)


def onesimulation(srcfilepath, destdir, expnum):
    starttime = datetime.now()
    learner = Learner(srcfilepath, destdir, expnum, magri=MAGRI, magritype=MAGRITYPE, specgenbias=SPECGENBIAS)
    # learner = Learner(FILE, magri=MAGRI, specgenbias=SPECGENBIAS)
    tableaux = learner.read_input()
    learner.set_tableaux(get_tableaux(tableaux, learner.constraints))
    # print("learner's tableaux list", learner.tableaux_list)

    # testweights = {}
    # for c in constraints:
    #     testweights[c] = random.randint(0, 1000000)
    # print(tableaux_list[46])
    # print(sorted(testweights.items(), key=lambda x: x[1], reverse=True))
    # print(evaluate_one(tableaux_list[46], testweights))

    print("--------------- BEGIN TRAIN ---------------------")
    learner.train()

    with io.open(learner.resultsfile, "w") as rf:
        datestring = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        rf.write(datestring + "\n")

        rf.write("\n--------------- PARAMETERS ---------------------\n")
        rf.write("Magri update used: " + ("yes" if MAGRI else "no") + "\n")
        rf.write("specific > general bias: " + (str(SPECGENBIAS) if SPECGENBIAS > 0 else "no") + "\n")
        rf.write("learning trials, listed by batch: " + str(learner.learning_trials) + "\n")
        rf.write("markedness plasticity, listed by batch: " + str(LEARNING_R_M) + "\n")
        rf.write("markedness noise, listed by batch: " + str(LEARNING_NOISE_M) + "\n")
        rf.write("faithfulness plasticity, listed by batch: " + str(LEARNING_R_F) + "\n")
        rf.write("faithfulness noise, listed by batch: " + str(LEARNING_NOISE_F) + "\n")
        if len(INIT_WEIGHTS.keys()) > 0:
            rf.write("initial weights: " + str(INIT_WEIGHTS) + "\n")
        else:
            rf.write("initial markedness weights = " + str(INIT_M) + "; initial faithfulness weights = " + str(INIT_F))
        rf.write("\n")

        print("\n--------------- RESULTS ---------------------\n")
        rf.write("\n--------------- RESULTS ---------------------\n\n")
        finalweights = list(learner.weights.items())
        finalweights.sort(key=lambda x: x[1], reverse=True)
        cons, weights = zip(*finalweights)
        for idx, con in enumerate(cons):
            # print(con + "\t" + str(weights[idx]))  # takes up space/time on command line
            rf.write(con + "\t" + str(weights[idx]) + "\n")
        print("\nrounded:")
        rf.write("\nrounded:\n")
        for idx, con in enumerate(cons):
            roundedstring = str(round(weights[idx], 3))
            print(con + "\t" + roundedstring)
            rf.write(con + "\t" + roundedstring + "\n")


        print("\n--------------- BEGIN TEST ---------------------\n")
        rf.write("\n--------------- BEGIN TEST ---------------------\n\n")
        testresults = learner.testgrammar(100)
        for results_t in testresults:
            # print([results_t.columns[0]]+list(results_t.columns[1:3])+list(cons))
            ordered_t = results_t.reindex([results_t.columns[0]]+list(results_t.columns[1:3])+list(cons), axis=1)
            # print(ordered_t)  # takes up space/time on command line
            rf.write(ordered_t.to_string(index=False) + "\n\n")

        # print(learner.weights)
        endtime = datetime.now()
        print("time elapsed", endtime-starttime)
        rf.write("time elapsed: " + str(endtime-starttime))


if __name__ == "__main__":
    main()

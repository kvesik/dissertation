import io
import pandas as pd
import re
import os
import random
import lfcd_otsoft_outputfixer
import numpy as np
from datetime import datetime

NEst = "NEst"
SEst = "SEst"
SSeto = "SSeto"
NSeto = "NSeto"
Fin = "Fin"

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


DATA_DIR = "OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files"
# FILES_EXPS = [
#     ("OTSoft_Fin_GLA_PDDP_nodia.txt", "Fi153"),
#     ("OTSoft_NEst_GLA_PDDP_nodia.txt", "NE153"),
#     ("OTSoft_NSeto_GLA_PDDP_nodia.txt", "NS153"),
#     ("OTSoft_SSeto_GLA_PDDP_nodia.txt", "SS153"),
# ]

m = "markedness"
f = "faithfulness"
ctype = "constraint type"


class Grammar:

    def __init__(self, grammarfilepath, testtableauxfilepath):
        self.testtableauxfile = testtableauxfilepath
        self.grammarfile = grammarfilepath
        # testtableauxfilename = testtableauxfilepath[testtableauxfilepath.rfind("/") + 1:]
        self.resultsfile = testtableauxfilepath.replace(".txt", "_TESTED.txt")
        self.constraints = []
        self.strata = []
        self.set_strata()
        self.tableaux_list = []
        tableaux = self.read_input()
        self.set_tableaux(tableaux)

    # TODO description
    # tableaux = dictionary of inputstring --> { dictionary of candidate --> list of violations }
    def set_tableaux(self, tableaux):
        list_of_dfs = []
        for ur in tableaux.keys():
            list_of_dfs.append(get_tableau(ur, tableaux[ur], self.constraints))
        # return list_of_dfs
        self.tableaux_list = list_of_dfs

    # TODO description
    def set_strata(self):
        strata_dict = {}

        if "DraftOutput_strata" not in self.grammarfile:  # ie, just DraftOutput.txt
            # unprocessed OTSoft output
            lfcd_otsoft_outputfixer.main(self.grammarfile)
            self.grammarfile = self.grammarfile.replace("DraftOutput.txt", "DraftOutput_strata.txt")
        with io.open(self.grammarfile, "r") as infile:
            currentstratumidx = -1
            for ln in infile:
                ln = ln.strip()
                if "Stratum" in ln:
                    currentstratumidx += 1
                    strata_dict[currentstratumidx] = []
                elif currentstratumidx >= 0:
                    strata_dict[currentstratumidx].append(ln)

        self.strata = [strata_dict[i] for i in range(currentstratumidx+1)]

    # TODO description
    def read_input(self):
        with io.open(self.testtableauxfile, "r") as infile:
            df = pd.read_csv(infile, sep="\t", header=1, keep_default_na=False)
            df.rename(
                columns=({'Unnamed: 0': 'input', 'Unnamed: 1': 'candidate', 'Unnamed: 2': 'frequency'}),
                inplace=True,
            )
            # assume violations are listed explicitly
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

                cur_violations = getviolations(cur_input, cur_candidate, list(df.columns[3:]), row[3:])
                cur_tableau[cur_candidate] = {}
                cur_tableau[cur_candidate]["frequency"] = cur_frequency
                cur_tableau[cur_candidate]["violations"] = cur_violations

            # save the final input's tableau
            tableaux[cur_input] = cur_tableau

        self.constraints = list(df.columns[3:])

        return tableaux
        # self.tableaux_list = tableaux

    def getoneevalranking(self):
        evalranking = []
        for stratum in self.strata:
            randomizedstratum = random.sample(stratum, len(stratum))
            evalranking.extend(randomizedstratum)
        return evalranking

    def testgrammar(self, keepstrataintact=True, numtimes=1):
        forms = {}  # ur --> dict of [ candidate --> frequency ]
        for t in self.tableaux_list:
            # set up UR keys to track frequency of each output
            ur = t.columns[0]
            forms[ur] = {}
            for candidate in t[ur].values:
                forms[ur][candidate] = 0
        if keepstrataintact:
            numtimes = 1
        for i in range(numtimes):
            if i % 10 == 0:
                print("test lap ", i)
            # shuffled_tableaux = random.sample(self.tableaux_list, len(self.tableaux_list))

            for tableau in self.tableaux_list:
                if keepstrataintact:
                    optimalout = self.evaluate_one(tableau)
                else:  # strict ranking, where each stratum has a randomized order
                    evalranking = self.getoneevalranking()
                    optimalout = self.evaluate_one(tableau, evalranking)
                ur = tableau.columns[0]
                forms[ur][optimalout] += 1
        forms_normalized = {}
        for ur in forms.keys():
            cands, freqs = zip(*list(forms[ur].items()))
            freqsum = sum(freqs)
            freqs = [f/freqsum for f in freqs]
            forms_normalized[ur] = freqs

        results_tableaux_list = []
        for t in self.tableaux_list:
            results_t = t.copy()
            results_t.insert(2, "outputfrequency", forms_normalized[t.columns[0]])
            results_tableaux_list.append(results_t)
            # print(results_t)

        return results_tableaux_list

    # evalrankings is a list of constraint names in ranking order
    def evaluate_one(self, tableau_df, evalranking=None):
        ur = tableau_df.columns[0]
        candidate_contenders = [cand for cand in tableau_df[ur].values]

        if evalranking is None:
            # then attempt to use the strata without strict ordering
            winner = ""
            stratidx = 0
            while winner == "" and stratidx < len(self.strata):
                ur_and_stratum = [ur] + self.strata[stratidx]
                df_thisstratum = tableau_df[[ur] + self.strata[stratidx]]
                df_thisstratum['sum'] = df_thisstratum[list(df_thisstratum.columns[1:])].sum(axis=1)
                if 0 in df_thisstratum['sum']:
                    # good to go; any candidates with more than one violation in this stratum can be eliminated
                    #   without worrying about ranking within the stratum
                    reduced_contenders = []
                    for bla, row in df_thisstratum.iterrows():
                        if row['sum'] == 0 and row[ur] in candidate_contenders:
                            reduced_contenders.append(row[ur])
                    candidate_contenders = reduced_contenders
                    if len(candidate_contenders) == 1:
                        # we have a winner!
                        winner = candidate_contenders[0]
                else:
                    print("warning! there are no clear candidates to eliminate in the stratum with index="+str(stratidx))
                stratidx += 1

        else:
            # a strict ordering has been provided
            winner = ""
            idx = 0
            while winner == "" and idx < len(evalranking):
                c = evalranking[idx]
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


# end of class Grammar #


def getviolations(ur, candidate, cons, cellvalues):
    violations = []
    for idx, cell in enumerate(cellvalues):
        numviolations = 0
        # print(cell)
        if re.match("\d+", str(cell)):
            # number of violations was explicitly assigned
            numviolations = int(cell)
        else:  # violation mark(s) hasn't been explicitly assigned
            numviolations = 0
        violations.append(numviolations)
    return violations


# tableau = dictionary of candidate --> list of violations
def get_tableau(ur, tableau, constraints):
    # df = make_tableau_df(tableau)
    df_lists = []
    for cand in tableau.keys():
        df_lists.append([cand]+[tableau[cand]["frequency"]]+tableau[cand]["violations"])
    df = pd.DataFrame(df_lists, columns=[ur]+["frequency"]+constraints)
    return df


def main(relfilepath=None):
    if relfilepath is None:
        relfilepath = input("Enter relative filepath whose LFCD grammar to test: ")

    # maindir = relfilepath[:afterfirstslash]
    # testfilepath = maindir + relfilepath[afterlastslash:].replace("DraftOutput.txt", "_test.txt").replace("_nodia", "").replace("simple", "simp_")
    # resultsdir = relfilepath[:afterlastslash]
    #
    # print("relfilepath:", relfilepath)
    # print("testfilepath:", testfilepath)
    # print("resultsdir:", resultsdir)
    # return

    grammarfilepath = relfilepath
    # grammarfilename = grammarfilepath[afterlastslash:]
    grammarfilename = os.path.split(grammarfilepath)[1]
    begofcustomizationstring = grammarfilename.index("LFCD_") + 5
    endofcustomizationstring = grammarfilename.index("DraftOutput")
    customizationstring = grammarfilename[begofcustomizationstring:endofcustomizationstring]
    lang = [l for l in [NEst, Fin, NSeto, SSeto] if l in grammarfilename][0]

    testfileparentparentdir = "../simulation_inputs/20231005 onward - OTSoft inputs (max len 3)"
    for f1 in os.listdir(testfileparentparentdir):
        testfileparentdir = os.path.join(testfileparentparentdir, f1)
        if os.path.isdir(testfileparentdir) and f1.endswith(customizationstring + "_test"):
            for f2 in os.listdir(testfileparentdir):
                testtableauxfilepathmaybe = os.path.join(testfileparentdir, f2)
                if os.path.isfile(testtableauxfilepathmaybe) and lang in f2 and "LFCD" in f2:
                    testtableauxfilepath = testtableauxfilepathmaybe

    grammar = Grammar(grammarfilepath, testtableauxfilepath)
    testresults = grammar.testgrammar(True, 1)
    return


    with io.open(relfilepath, "r") as rf:
        with io.open(relfilepath.replace("DraftOutput.txt", "TestOutput.txt"), "w") as wf:
            with io.open(testfilepath, "r") as tf:
                # collect strata from OTSoft's output file for this LFCD grammar
                # load tableaux
                # test grammar on all inputs (both faithful training inputs, and unfaithful test-only inputs)
                grammar = Grammar(testfilepath, relfilepath)
                testresults = grammar.testgrammar()
                testtableauxstring = ""
                teststatementstring = ""
                for results_t in testresults:
                    ur = results_t.columns[0]
                    cands = results_t[ur].values
                    inputfrequencies = results_t["frequency"].values
                    outputfrequencies = results_t["outputfrequency"].values
                    matching = False not in (inputfrequencies == outputfrequencies)

                    stmt = "UR " + ur + ": the generated output IS " + ("" if matching else "NOT ") + "as expected."
                    teststatementstring += stmt + "\n"
                    if not matching:
                        print(stmt)
                    stratified_constraints = strata.values()
                    ordered_constraints = [c for stratum in stratified_constraints for c in stratum]
                    ordered_t = results_t.reindex(
                        [results_t.columns[0]] + list(results_t.columns[1:3]) + ordered_constraints, axis=1)
                    # print(ordered_t)
                    testtableauxstring += ordered_t.to_string(index=False) + "\n\n"
                    if not matching:
                        print(results_t)
                wf.write(teststatementstring)
                wf.write("\n\n")
                wf.write(testtableauxstring)


if __name__ == "__main__":
    filesdone = []
    firstfolder = "../simulation_outputs/20231115_LFCD_outputs"
    for fname1 in os.listdir(firstfolder):
        if os.path.isdir(os.path.join(firstfolder, fname1)) and "FilesForOTSoft" in fname1 and "LFCD" in fname1:
            secondfolder = fname1
            for fname2 in os.listdir(os.path.join(firstfolder, secondfolder)):
                if fname2.endswith("DraftOutput.txt"):
                    if len(filesdone) < 3:
                        filesdone.append(secondfolder)
                        print("testing grammar in " + secondfolder)
                        main(os.path.join(firstfolder, secondfolder, fname2))
    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_Fin_GLA_PDDP_nodia/OTSoft_Fin_GLA_PDDP_nodiaFullHistory.xls")
    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_NEst_GLA_PDDP_nodia/OTSoft_NEst_GLA_PDDP_nodiaFullHistory.xls")
    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_SSeto_GLA_PDDP_nodia/OTSoft_SSeto_GLA_PDDP_nodiaFullHistory.xls")
    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_NSeto_GLA_PDDP_nodia/OTSoft_NSeto_GLA_PDDP_nodiaFullHistory.xls")

    # asks for user to input file path
    # main()
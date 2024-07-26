import io
import pandas as pd
import re
import os
import random
import lfcd_otsoft_stratacleaner


typetoanalyze = "TESTS"  #  "RESULTS"

# EXACT COPY OF LFCD TESTER (only adapted up to here)

class Grammar:

    def __init__(self, grammarTESTSresultsfilepath, intendedtableauxfilepath):
        self.intendedtableauxfilepath = intendedtableauxfilepath
        self.TESTSfilepath = grammarTESTSresultsfilepath
        self.analysisfile = self.TESTSfilepath.replace("00.txt", "00_analysis.txt")
        self.constraints = []
        self.intendedtableaux_list = []
        self.grammarTESTStableaux_list = []

    # TODO description
    # intendedtableaux = dictionary of inputstring --> { dictionary of candidate --> list of violations }
    def set_intendedfrequencies(self, intendedtableaux):
        list_of_dfs = []
        for ur in intendedtableaux.keys():
            list_of_dfs.append(get_tableau(ur, intendedtableaux[ur], self.constraints))
        self.intendedtableaux_list = list_of_dfs

    # # TODO description
    # def set_strata(self):
    #     strata_dict = {}
    #
    #     if "DraftOutput_strata" not in self.grammarfile:  # ie, just DraftOutput.txt
    #         # unprocessed OTSoft output
    #         if "001n" in self.grammarfile:
    #             temp = 3
    #         grammarfile_processed = self.grammarfile.replace("DraftOutput", "DraftOutput_strata")
    #         if not os.path.exists(grammarfile_processed):
    #             lfcd_otsoft_stratacleaner.main(self.grammarfile)
    #         self.grammarfile = grammarfile_processed
    #     with io.open(self.grammarfile, "r") as infile:
    #         currentstratumidx = -1
    #         for ln in infile:
    #             ln = ln.strip()
    #             if "Stratum" in ln:
    #                 currentstratumidx += 1
    #                 strata_dict[currentstratumidx] = []
    #             elif currentstratumidx >= 0:
    #                 try:
    #                     strata_dict[currentstratumidx].append(ln)
    #                 except KeyError:
    #                     print(grammarfile_processed + " doesn't contain any information")
    #                     return
    #
    #     self.strata = [strata_dict[i] for i in range(currentstratumidx+1)]

    # TODO description
    def read_intendedfrequencies(self):
        with io.open(self.intendedtableauxfilepath, "r") as infile:
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

                cur_violations = getviolations(row[3:])
                # cur_violations = getviolations(cur_input, cur_candidate, list(df.columns[3:]), row[3:])
                cur_tableau[cur_candidate] = {}
                cur_tableau[cur_candidate]["frequency"] = cur_frequency
                cur_tableau[cur_candidate]["violations"] = cur_violations

            # save the final input's tableau
            tableaux[cur_input] = cur_tableau

        self.constraints = list(df.columns[3:])

        return tableaux

    # def getoneevalranking(self):
    #     evalranking = []
    #     for stratum in self.strata:
    #         randomizedstratum = random.sample(stratum, len(stratum))
    #         evalranking.extend(randomizedstratum)
    #     return evalranking

    # TODO finish this
    def collecttestresults(self):
        forms_normalized = {}  # ur --> dict of [ candidate --> normalized frequency /1 ]
        for t in self.intendedtableaux_list:
            # set up UR keys to track frequency of each output
            ur = t.columns[0]
            forms_normalized[ur] = {}
            for candidate in t[ur].values:
                forms_normalized[ur][candidate] = 0

        forms_normalized = {}
        for ur in forms.keys():
            cands, freqs = zip(*list(forms[ur].items()))
            freqsum = sum(map(abs, freqs))
            if freqsum > 0:
                freqs = [f/freqsum for f in freqs]
            forms_normalized[ur] = freqs

        results_tableaux_list = []
        for t in self.intendedtableaux_list:
            results_t = t.copy()
            results_t.insert(2, "outputfrequency", forms_normalized[t.columns[0]])
            results_tableaux_list.append(results_t)

        return results_tableaux_list

    # # evalrankings is a list of constraint names in ranking order
    # # returns a pair of lists: (winners, lastcandidatesstanding)
    # # winners:
    # #   - has one element if there's a single optimal output
    # #   - has more than one element if there's a tie
    # #   - has zero elements if the stratified ranking makes selecting the optimal output(s) ambiguous
    # # lastcandidatestanding:
    # #   - has zero elements if there was a clear winner/s
    # #   - has more than one element if the stratified ranking makes selecting the optimal output(s) ambiguous;
    # #       these are the last candidates standing before the ambiguous statum was reached
    # def evaluate_one(self, tableau_df, evalranking=None):
    #     ur = tableau_df.columns[0]
    #     candidate_contenders = [cand for cand in tableau_df[ur].values]
    #
    #     if evalranking is None:
    #         # then attempt to use the strata without strict ordering
    #
    #         stratidx = 0
    #         while stratidx < len(self.strata):
    #             current_tableauslice_df = tableau_df.copy(deep=True)
    #             current_tableauslice_df = current_tableauslice_df[current_tableauslice_df[ur].isin(candidate_contenders)]
    #
    #             thisstratum = self.strata[stratidx]
    #             # before summing violations we first remove constraints with the same # violations for each candidate
    #             thisstratum_active = [s for s in thisstratum if current_tableauslice_df[s].nunique() > 1]
    #             if len(thisstratum_active) > 0:
    #                 # there is actually at least one active constraint in this stratum
    #                 current_tableauslice_df = current_tableauslice_df[[ur] + thisstratum_active]
    #                 current_tableauslice_df['sum'] = current_tableauslice_df[list(current_tableauslice_df.columns[1:])].sum(axis=1)
    #
    #                 sumcolvalues = list(current_tableauslice_df['sum'])
    #                 if 0 in sumcolvalues:
    #                     # good to go; any candidates with more than one violation in this stratum can be eliminated
    #                     #   without worrying about ranking within the stratum
    #                     current_tableauslice_df = current_tableauslice_df[current_tableauslice_df['sum'] == 0]
    #                     reduced_contenders = list(current_tableauslice_df[ur])
    #                     candidate_contenders = reduced_contenders
    #                     if len(candidate_contenders) == 1:
    #                         # we have a winner!
    #                         winners = [candidate_contenders[0]]
    #                         lastcandidatesstanding = []
    #                         return winners, lastcandidatesstanding
    #                 elif len(thisstratum_active) == 1:
    #                     # good to go; any candidates with more than the least # of violations for this stratum's
    #                     # single constraint can be eliminated without worrying about ranking within the stratum
    #                     current_tableauslice_df = current_tableauslice_df[current_tableauslice_df['sum'] == current_tableauslice_df['sum'].min()]
    #                     reduced_contenders = list(current_tableauslice_df[ur])
    #                     candidate_contenders = reduced_contenders
    #                     if len(candidate_contenders) == 1:
    #                         # we have a winner!
    #                         winners = [candidate_contenders[0]]
    #                         lastcandidatesstanding = []
    #                         return winners, lastcandidatesstanding
    #                 else:
    #                     # remove any harmonically bounded candidates
    #                     new_tableauslice_df, reduced_contenders = self.removeharmonicallyboundedcandidates(ur, current_tableauslice_df.copy(deep=True), thisstratum_active)
    #                     if reduced_contenders != candidate_contenders:
    #                         # we did remove at least one harmonically bounded candidate
    #                         candidate_contenders = reduced_contenders
    #                         if len(candidate_contenders) == 1:
    #                             # we have a winner!
    #                             winners = [candidate_contenders[0]]
    #                             lastcandidatesstanding = []
    #                             return winners, lastcandidatesstanding
    #                         else:
    #                             # keep the same stratum, but with reduced candidate contenders
    #                             stratidx -= 1  # it's about to get incremented but we don't want it to
    #                     else:
    #                         # give up
    #                         winners = []
    #                         lastcandidatesstanding = candidate_contenders
    #                         return winners, lastcandidatesstanding
    #             stratidx += 1
    #         # if you've made it through the whole loop and haven't come out with a unique winner, then you might have a tie
    #         winners = candidate_contenders
    #         lastcandidatesstanding = []
    #         return winners, lastcandidatesstanding
    #
    #     else:
    #         # a strict ordering has been provided
    #         winner = ""
    #         idx = 0
    #         while winner == "" and idx < len(evalranking):
    #             c = evalranking[idx]
    #             violns = {}
    #             for bla, row in tableau_df.iterrows():
    #                 viol = row[c]
    #                 if viol not in violns.keys():
    #                     violns[viol] = []
    #                 violns[viol].append(row[ur])
    #
    #             violations_category = 0
    #             existing_violn_numbers = sorted(list(violns.keys()))
    #             reduced = False
    #             while violations_category <= max(existing_violn_numbers) and winner == "" and not reduced:
    #                 if violations_category in existing_violn_numbers:
    #                     successful_cands = violns[violations_category]
    #                     reduced_contenders = [c for c in candidate_contenders if c in successful_cands]
    #                     if len(reduced_contenders) > 0:
    #                         candidate_contenders = reduced_contenders
    #                         reduced = True
    #                         if len(candidate_contenders) == 1:
    #                             # we have a winner!
    #                             winner = candidate_contenders[0]
    #                 violations_category += 1
    #             idx += 1
    #
    #     return [winner], []

    # def removeharmonicallyboundedcandidates(self, ur, tableauslice_df, activecons):
    #     maxsum = max(tableauslice_df['sum'])
    #     allcands = list(tableauslice_df[ur])
    #     candswithmaxsum = list(tableauslice_df[tableauslice_df['sum'] == tableauslice_df['sum'].max()][ur])
    #     violationprofiles = [list(tableauslice_df.loc[tableauslice_df[ur] == cand, activecons]) for cand in allcands]
    #     boundedcands = []
    #     if len(candswithmaxsum) < len(allcands):
    #         # there's a chance we might be able to eliminate the maxsum row(s)
    #         maxsumindices = [allcands.index(maxsumcand) for maxsumcand in candswithmaxsum]
    #         lowsumindices = [idx for idx in range(len(allcands)) if idx not in maxsumindices]
    #         for idx1 in maxsumindices:
    #             for idx2 in lowsumindices:
    #                 cand1 = allcands[idx1]
    #                 cand2 = allcands[idx2]
    #                 vp1 = violationprofiles[idx1]
    #                 vp2 = violationprofiles[idx2]
    #
    #                 vp1_atleastasbadas_vp2 = [v1 >= v2 for (v1, v2) in zip(vp1, vp2)]
    #                 if all(vp1_atleastasbadas_vp2):
    #                     boundedcands.append(cand1)
    #
    #     for bc in boundedcands:
    #         tableauslice_df = tableauslice_df[tableauslice_df[ur] != bc]
    #     return tableauslice_df, [c for c in allcands if c not in boundedcands]





# end of class Grammar #


def getviolations(cellvalues):
    # used to be: def getviolations(ur, candidate, cons, cellvalues):
    violations = []
    for idx, cell in enumerate(cellvalues):
        if re.match("\d+", str(cell)):
            # number of violations was explicitly assigned
            numviolations = int(cell)
        else:  # violation mark(s) hasn't been explicitly assigned
            numviolations = 0
        violations.append(numviolations)
    return violations


# tableau = dictionary of candidate --> list of violations
def get_tableau(ur, tableau, constraints):
    df_lists = []
    for cand in tableau.keys():
        df_lists.append([cand]+[tableau[cand]["frequency"]]+tableau[cand]["violations"])
    df = pd.DataFrame(df_lists, columns=[ur]+["frequency"]+constraints)
    return df


def main(TESTSfilepath=None):
    if TESTSfilepath is None:
        TESTSfilepath = input("Enter relative filepath whose GLA TESTS results to analyze: ")

    TESTSfilename = os.path.split(TESTSfilepath)[1]
    begoflangstring = TESTSfilename.index("PDDP-") + 5
    endoflangstring = TESTSfilename.index("_GLA_")
    langstring = TESTSfilename[begoflangstring:endoflangstring]
    begofcustomizationstring = endoflangstring + 5
    endofcustomizationstring = TESTSfilename.index("TESTS")
    customizationstring = TESTSfilename[begofcustomizationstring:endofcustomizationstring]

    testfileparentparentdir = os.path.join("..", "sim_ins", "20240507 on - OTSoft inputs")
    testtableauxfilepath = ""
    testfileparentdirs = [os.path.join(testfileparentparentdir, fn) for fn in os.listdir(testfileparentparentdir) if fn.endswith(("OTS_" + customizationstring + "_test").replace("__", "_"))]
    for tfpdir in [fn for fn in testfileparentdirs if os.path.isdir(fn)]:
        testtableauxfilenames = [os.path.join(tfpdir, fn) for fn in os.listdir(tfpdir) if langstring in fn and "GLA" in fn]
        try:
            testtableauxfilepath = testtableauxfilenames[0]
        except IndexError:
            return

    grammar = Grammar(TESTSfilepath, testtableauxfilepath)
    if os.path.exists(grammar.analysisfile):
        # already done; skip this one
        print("    already done; skipping")
        return
    # else:
    #     grammar.set_strata()
    #
    # if not grammar.strata:
    #     print("    no strata information; skipping")
    #     return
    # else:
    grammar.set_intendedfrequencies(grammar.read_intendedfrequencies())
    testresults = grammar.collecttestresults() # GOOD UP TO HERE

    with io.open(grammar.analysisfile, "w") as wf:
        detailsstring = ""
        matchtypes = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, -1: 0}

        for results_t in testresults:
            ur = results_t.columns[0]
            inputfrequencies = results_t["frequency"].values
            outputfrequencies = results_t["outputfrequency"].values
            matchtype = getmatchtype(inputfrequencies, outputfrequencies)
            matchtypes[matchtype] += 1

            teststatementstring = "UR " + ur + ": the generated output (" + str(matchtype) + ") "
            if matchtype == 0:
                teststatementstring += "COULD NOT BE DETERMINED from this ranking."
            elif matchtype == 1:
                teststatementstring += "MATCHES what was predicted."
            elif matchtype == 2:
                teststatementstring += "is a STRICT, NONEMPTY SUBSET of what was predicted."
            elif matchtype == 3:
                teststatementstring += "COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) match what was predicted."
            elif matchtype == 4:
                teststatementstring += "COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) form a strict, nonempty subset of what was predicted."
            else:
                teststatementstring += "is a MYSTERY. ooooOOOOOOOoooooo..."

            ordered_constraints = [c for stratum in grammar.strata for c in stratum]
            ordered_t = results_t.reindex(
                [results_t.columns[0]] + list(results_t.columns[1:3]) + ordered_constraints, axis=1)
            testtableauxstring = ordered_t.to_string(index=False)
            detailsstring += teststatementstring + "\n" + testtableauxstring + "\n\n"

        wf.write("Of " + str(len(testresults)) + " inputs:\n")
        wf.write("   (1) " + str(matchtypes[1]) + " had outputs that MATCH what was predicted\n")
        wf.write("   (2) " + str(matchtypes[2]) + " had outputs that are a STRICT, NONEMPTY SUBSET of what was predicted\n")
        wf.write("   (3) " + str(matchtypes[3]) + " had outputs that COULD NOT BE DETERMINED from this ranking, but the last candidates standing match what was predicted\n")
        wf.write("   (4) " + str(matchtypes[4]) + " had outputs that COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) form a strict, nonempty subset of what was predicted\n")
        wf.write("   (0) " + str(matchtypes[0]) + " had outputs that COULD NOT BE DETERMINED from this ranking\n")
        wf.write("   (-1) " + str(matchtypes[-1]) + " had outputs that are a MYSTERY\n\n")
        wf.write(detailsstring)


def getmatchtype(inputfrequencies, outputfrequencies):
    if all([o >= 0 for o in outputfrequencies]):
        out_equals_in = all(inputfrequencies == outputfrequencies)
        out_empty = all([o == 0 for o in outputfrequencies])
        out_strictsubsetof_in = all([o <= i for (i, o) in zip(inputfrequencies, outputfrequencies)]) and not out_equals_in
        if out_equals_in:
            return 1
        elif out_empty:
            return 0
        elif out_strictsubsetof_in:
            return 2
    else:
        out_undetermined_equalsin = all([bool(i) == bool(o) for (i, o) in zip(inputfrequencies, outputfrequencies)])
        out_undetermined_subsetin = all([not(i == 0 and o < 0) for (i, o) in zip(inputfrequencies, outputfrequencies)]) and not out_undetermined_equalsin
        if out_undetermined_equalsin:
            return 3
        elif out_undetermined_subsetin:
            return 4

    # else none of the above
    return -1


if __name__ == "__main__":
    filesdone = []
    firstfolder = "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if fn.startswith("T_Mgen")]
    for secondfolder in folderstotest:
        TESTSfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "TESTS" in fn]
        if TESTSfiles:
            TESTSfilepath = os.path.join(firstfolder, secondfolder, TESTSfiles[0])
        else:
            print("can't find TESTS file in", secondfolder, " - skipping to next folder")
            continue

        if True:
            filesdone.append(secondfolder)
            print("testing grammar in " + secondfolder)
            main(TESTSfilepath)

    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_Fin_GLA_PDDP_nodia/OTSoft_Fin_GLA_PDDP_nodiaFullHistory.xls")

    # asks for user to input file path
    # main()

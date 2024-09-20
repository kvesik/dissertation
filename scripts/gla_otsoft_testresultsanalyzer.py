import io
import sys

import pandas as pd
import re
import os
# import random
# import lfcd_otsoft_stratacleaner
from generate_tableaux_otsoft_specifylang import isintendedwinner, isalternatewinner, Fin, NEst, NSeto


typetoanalyze = "TESTS"  #  "RESULTS"
OUTPUTS_DIR = "../sim_outs/20240507_GLA_outputs"


class Grammar:

    def __init__(self, language, grammarTESTSresultsfilepath, intendedtableauxfilepath):
        self.lang = language
        self.intendedtableauxfilepath = intendedtableauxfilepath
        self.TESTSfilepath = grammarTESTSresultsfilepath
        self.analysisfile = self.TESTSfilepath.replace("00.txt", "00_analysis.txt")
        self.constraints = []
        self.intendedtableaux_list = []
        self.grammarTESTStableaux_list = []

    # # TODO description
    # # intendedtableaux = dictionary of inputstring --> { dictionary of candidate --> list of violations }
    # def set_intendedfrequencies(self, intendedtableaux):
    #     list_of_dfs = []
    #     for ur in intendedtableaux.keys():
    #         list_of_dfs.append(get_tableau(ur, intendedtableaux[ur], self.constraints))
    #     self.intendedtableaux_list = list_of_dfs
    #
    # # TODO description
    # def read_intendedfrequencies(self):
    #     with io.open(self.intendedtableauxfilepath, "r") as infile:
    #         df = pd.read_csv(infile, sep="\t", header=1, keep_default_na=False)
    #         df.rename(
    #             columns=({'Unnamed: 0': 'input', 'Unnamed: 1': 'candidate', 'Unnamed: 2': 'frequency'}),
    #             inplace=True,
    #         )
    #         # assume violations are listed explicitly
    #         tableaux = {}
    #
    #         cur_input = ""
    #         cur_tableau = {}
    #         for idx, row in df.iterrows():
    #             if row["input"] != "":
    #                 if len(cur_tableau.keys()) > 0:
    #                     # save previous input's tableau
    #                     tableaux[cur_input] = cur_tableau
    #                 # start a new tableau
    #                 cur_input = row["input"]
    #                 cur_tableau = {}
    #             cur_candidate = row["candidate"]
    #             cur_frequency = row["frequency"]
    #             if cur_frequency == "":
    #                 cur_frequency = 0
    #             else:
    #                 cur_frequency = float(cur_frequency)
    #
    #             cur_violations = getviolations(row[3:])
    #             # cur_violations = getviolations(cur_input, cur_candidate, list(df.columns[3:]), row[3:])
    #             cur_tableau[cur_candidate] = {}
    #             cur_tableau[cur_candidate]["frequency"] = cur_frequency
    #             cur_tableau[cur_candidate]["violations"] = cur_violations
    #
    #         # save the final input's tableau
    #         tableaux[cur_input] = cur_tableau
    #
    #     self.constraints = list(df.columns[3:])
    #
    #     return tableaux

    def collecttestresults(self):
        results = {}
        with io.open(self.TESTSfilepath, "r") as tf:
            ln = tf.readline()
            while "BEGIN TEST" not in ln:
                ln = tf.readline()

            # one more to get down to the results tableaux section
            ln = tf.readline()
            current_ur = ""
            current_goodresultsfreq = 0
            current_badresultsfreq = 0
            # current_cand_freqs = {}
            while ln != "" and "time elapsed" not in ln:
                if ln.strip() == "":
                    # about to see a new results tableau; normalize & save the current info if it exists
                    if current_ur:
                        # summarize how good this result was
                        results[current_ur] = (current_goodresultsfreq, current_badresultsfreq)
                    # refresh info
                    current_ur = ""
                    current_goodresultsfreq = 0
                    current_badresultsfreq = 0
                    # current_cand_freqs = {}
                elif "frequency" in ln:
                    current_ur = ln.strip().split()[0]
                else:
                    first3entries = ln.strip().split()[:3]  # candidate, inputfrequency, outputfrequency
                    cand = first3entries[0]
                    infreq = float(first3entries[1])
                    outfreq = float(first3entries[2])

                    iscandintendedwinner = isintendedwinner(current_ur, cand, self.lang)
                    iscandalternatewinner = isalternatewinner(current_ur, cand, self.lang)

                    if iscandintendedwinner or iscandalternatewinner:
                        current_goodresultsfreq += outfreq
                    else:
                        current_badresultsfreq += outfreq


                ln = tf.readline()

        return results

# end of class Grammar #


# def getviolations(cellvalues):
#     # used to be: def getviolations(ur, candidate, cons, cellvalues):
#     violations = []
#     for idx, cell in enumerate(cellvalues):
#         if re.match("\d+", str(cell)):
#             # number of violations was explicitly assigned
#             numviolations = int(cell)
#         else:  # violation mark(s) hasn't been explicitly assigned
#             numviolations = 0
#         violations.append(numviolations)
#     return violations
#
#
# # tableau = dictionary of candidate --> list of violations
# def get_tableau(ur, tableau, constraints):
#     df_lists = []
#     for cand in tableau.keys():
#         df_lists.append([cand]+[tableau[cand]["frequency"]]+tableau[cand]["violations"])
#     df = pd.DataFrame(df_lists, columns=[ur]+["frequency"]+constraints)
#     return df


def main_individual(TESTSfilepath=None):
    if TESTSfilepath is None:
        TESTSfilepath = input("Enter relative filepath whose GLA TESTS results to analyze: ")

    TESTSfilename = os.path.split(TESTSfilepath)[1]
    begoflangstring = TESTSfilename.index("PDDP-") + 5
    endoflangstring = TESTSfilename.index("_GLA_")
    langstring = TESTSfilename[begoflangstring:endoflangstring]
    begofcustomizationstring = endoflangstring + 5
    try:
        endofcustomizationstring = TESTSfilename.index("TESTS")
    except ValueError:
        endofcustomizationstring = TESTSfilename.index("RESULTS")

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

    grammar = Grammar(langstring, TESTSfilepath, testtableauxfilepath)
    if os.path.exists(grammar.analysisfile):
        # already done; skip this one
        print("    already done; skipping")
        return
    # TODO do we need this??
    # grammar.set_intendedfrequencies(grammar.read_intendedfrequencies())
    testresults = grammar.collecttestresults()
    goodtestresults, badtestresults = zip(*testresults.values())
    totalresults = len(goodtestresults)
    averagegoodresults = sum(goodtestresults)/totalresults
    averagebadresults = sum(badtestresults)/totalresults
    numtestswXpercentgoodresults = {
        100: len([res for res in goodtestresults if res == 1]),
        90: len([res for res in goodtestresults if res >= 0.90]),
        80: len([res for res in goodtestresults if res >= 0.80]),
        70: len([res for res in goodtestresults if res >= 0.70]),
        60: len([res for res in goodtestresults if res >= 0.60]),
        50: len([res for res in goodtestresults if res >= 0.50]),
        40: len([res for res in goodtestresults if res >= 0.40]),
        30: len([res for res in goodtestresults if res >= 0.30]),
        20: len([res for res in goodtestresults if res >= 0.20]),
        10: len([res for res in goodtestresults if res >= 0.10]),
        0: len([res for res in goodtestresults if res == 0])
    }

    with io.open(grammar.analysisfile, "w") as wf:
        with io.open(grammar.TESTSfilepath, "r") as tf:
            wf.write("average frequency of good test results: " + str(averagegoodresults) + "\n")
            wf.write("average frequency of bad test results: " + str(averagebadresults) + "\n")
            wf.write("\n")

            writestring = "number inputs with {degree} {percent}% {goodbad} results: {num} of {total}\n"
            for percent, num in numtestswXpercentgoodresults.items():
                # default values
                degree = "at least"
                goodbad = "good"

                # exceptional values
                if percent == 100:
                    degree = "exactly"
                elif percent == 0:
                    degree = "exactly"
                    # goodbad = "bad"

                # write the summary
                wf.write(writestring.format(degree=degree, percent=percent, goodbad=goodbad, num=num, total=totalresults))
            wf.write("\n")

            tf_ln = tf.readline()
            while "BEGIN TEST" not in tf_ln:
                tf_ln = tf.readline()

            # one more to get down to the results tableaux section
            tf_ln = tf.readline()
            current_ur = ""
            while tf_ln != "" and "time elapsed" not in tf_ln:
                if tf_ln.strip() == "":
                    # about to see a new results tableau; print the current results if they exist
                    if current_ur:
                        wf.write("frequency of good test results: " + str(testresults[current_ur][0]) + "\n")
                        wf.write("frequency of bad test results: " + str(testresults[current_ur][1]) + "\n")
                        wf.write("\n")
                    current_ur = ""
                else:
                    if "frequency" in tf_ln:
                        current_ur = tf_ln.strip().split()[0]
                    wf.write(tf_ln)
                tf_ln = tf.readline()
        #
        # detailsstring = ""
        # matchtypes = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, -1: 0}
        #
        # for results_t in testresults:
        #     ur = results_t.columns[0]
        #     inputfrequencies = results_t["frequency"].values
        #     outputfrequencies = results_t["outputfrequency"].values
        #     matchtype = getmatchtype(inputfrequencies, outputfrequencies)
        #     matchtypes[matchtype] += 1
        #
        #     teststatementstring = "UR " + ur + ": the generated output (" + str(matchtype) + ") "
        #     if matchtype == 0:
        #         teststatementstring += "COULD NOT BE DETERMINED from this ranking."
        #     elif matchtype == 1:
        #         teststatementstring += "MATCHES what was predicted."
        #     elif matchtype == 2:
        #         teststatementstring += "is a STRICT, NONEMPTY SUBSET of what was predicted."
        #     elif matchtype == 3:
        #         teststatementstring += "COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) match what was predicted."
        #     elif matchtype == 4:
        #         teststatementstring += "COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) form a strict, nonempty subset of what was predicted."
        #     else:
        #         teststatementstring += "is a MYSTERY. ooooOOOOOOOoooooo..."
        #
        #     ordered_constraints = [c for stratum in grammar.strata for c in stratum]
        #     ordered_t = results_t.reindex(
        #         [results_t.columns[0]] + list(results_t.columns[1:3]) + ordered_constraints, axis=1)
        #     testtableauxstring = ordered_t.to_string(index=False)
        #     detailsstring += teststatementstring + "\n" + testtableauxstring + "\n\n"
        #
        # wf.write("Of " + str(len(testresults)) + " inputs:\n")
        # wf.write("   (1) " + str(matchtypes[1]) + " had outputs that MATCH what was predicted\n")
        # wf.write("   (2) " + str(matchtypes[2]) + " had outputs that are a STRICT, NONEMPTY SUBSET of what was predicted\n")
        # wf.write("   (3) " + str(matchtypes[3]) + " had outputs that COULD NOT BE DETERMINED from this ranking, but the last candidates standing match what was predicted\n")
        # wf.write("   (4) " + str(matchtypes[4]) + " had outputs that COULD NOT BE DETERMINED from this ranking, but the last candidates standing (neg freqs) form a strict, nonempty subset of what was predicted\n")
        # wf.write("   (0) " + str(matchtypes[0]) + " had outputs that COULD NOT BE DETERMINED from this ranking\n")
        # wf.write("   (-1) " + str(matchtypes[-1]) + " had outputs that are a MYSTERY\n\n")
        # wf.write(detailsstring)


# def getmatchtype(inputfrequencies, outputfrequencies):
#     if all([o >= 0 for o in outputfrequencies]):
#         out_equals_in = all(inputfrequencies == outputfrequencies)
#         out_empty = all([o == 0 for o in outputfrequencies])
#         out_strictsubsetof_in = all([o <= i for (i, o) in zip(inputfrequencies, outputfrequencies)]) and not out_equals_in
#         if out_equals_in:
#             return 1
#         elif out_empty:
#             return 0
#         elif out_strictsubsetof_in:
#             return 2
#     else:
#         out_undetermined_equalsin = all([bool(i) == bool(o) for (i, o) in zip(inputfrequencies, outputfrequencies)])
#         out_undetermined_subsetin = all([not(i == 0 and o < 0) for (i, o) in zip(inputfrequencies, outputfrequencies)]) and not out_undetermined_equalsin
#         if out_undetermined_equalsin:
#             return 3
#         elif out_undetermined_subsetin:
#             return 4
#
#     # else none of the above
#     return -1


def main_overall_onefolder(analysisfilepath=None):
    if analysisfilepath is None:
        analysisfilepath = input("Enter relative filepath whose GLA TESTS results to analyze: ")

    analysisfolderpath, analysisfilename = os.path.split(analysisfilepath)
    analysisfoldername = os.path.split(analysisfolderpath)[1]

    begoflangstring = analysisfilename.index("PDDP-") + 5
    endoflangstring = analysisfilename.index("_GLA_")
    langstring = analysisfilename[begoflangstring:endoflangstring]

    begofspecificationstring = 2
    endofspecificationstring = analysisfoldername.index("_python") - 6
    specificationstring = analysisfoldername[begofspecificationstring:endofspecificationstring]

    resultstext = ""
    avggoodfreq = 0
    avgbadfreq = 0
    num100pctgood = 0
    num90pctgood = 0
    num0pctgood = 0
    numtotal = 0

    with io.open(analysisfilepath, "r") as af:
        ln = af.readline()
        while ln.startswith("average") or ln.startswith("number") or ln == "\n":
            # once we're through the summary at the top of the file, we're done

            if ln.startswith("average"):
                if "Mgen1.23_mg4_fs_sg20" in analysisfilepath:
                    pause = ""
                resultstext += ln

                if "good" in ln:
                    begofgood = ln.index("results:") + 9
                    goodstring = ln[begofgood:]
                    avggoodfreq = float(goodstring)
                elif "bad" in ln:
                    begofbad = ln.index("results:") + 9
                    badstring = ln[begofbad:]
                    avgbadfreq = float(badstring)

            elif ln.startswith("number"):
                resultstext += ln

                if "good" in ln:
                    if "100%" in ln:
                        begofgood = ln.index("results:") + 9
                        endofgood = ln.index(" of ")
                        goodstring = ln[begofgood:endofgood]

                        num100pctgood = int(goodstring)

                        begoftotal = endofgood + 4
                        totalstring = ln[begoftotal:]
                        numtotal = int(totalstring)
                    elif "90%" in ln:
                        begofgood = ln.index("results:") + 9
                        endofgood = ln.index(" of ")
                        goodstring = ln[begofgood:endofgood]

                        num90pctgood = int(goodstring)
                elif "bad" in ln:
                    begofbad = ln.index("results:") + 9
                    endofbad = ln.index(" of ")
                    badstring = ln[begofbad:endofbad]

                    num0pctgood = int(badstring)
            ln = af.readline()

    return {
        "lang": langstring,
        "specs": specificationstring,
        "results_strs": resultstext,
        "results_nums": (avggoodfreq, avgbadfreq, num100pctgood, num90pctgood, num0pctgood, numtotal)
    }


def testindividualfolders():
    filesdone = []

    firstfolder = OUTPUTS_DIR  # "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn))]  #  if "testycopy" in fn]  # if fn.startswith("T_Mgen")]
    for secondfolder in folderstotest:
        deleteresultsanalysisifpossible = False
        TESTSfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "TESTS" in fn]
        if TESTSfiles:
            TESTSfilepath = os.path.join(firstfolder, secondfolder, TESTSfiles[0])
            deleteresultsanalysisifpossible = True
        else:
            print("can't find TESTS file in", secondfolder, " - looking for RESULTS instead")
            RESULTSfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn]
            if RESULTSfiles:
                TESTSfilepath = os.path.join(firstfolder, secondfolder, RESULTSfiles[0])
            else:
                print("can't find RESULTS file in", secondfolder, " - skipping to next folder")
                continue

        if True:
            filesdone.append(secondfolder)
            print("testing grammar in " + secondfolder)
            main_individual(TESTSfilepath)

            # TODO
            # if deleteresultsanalysisifpossible:
            #     RESULTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn and "_analysis" in fn]
            #     for Raf in RESULTSanalysisfiles:
            #         print("deleting RESULTS_analysis file", Raf)
            #         os.remove(Raf)


def summarizeallfolders():
    filesdone = []
    firstfolder = OUTPUTS_DIR  # "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn))]  #  if "testycopy" in fn]  # if fn.startswith("T_Mgen")]
    allresults = {}
    # highestresult = 0.0
    # highestresultspecs = []  # list of strings
    # lowestresult = 1.0
    # lowestresultspecs = []  # list of strings
    resultsbyavggoodfreq = {}  # dict of float --> list of [tuple of (str, int)]
        # freq of good results --> [(specs, lowest numover90 in these specs), ...]

    for secondfolder in folderstotest:
        TESTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "TESTS" in fn and "_analysis" in fn]
        if TESTSanalysisfiles:
            analysisfilepath = os.path.join(firstfolder, secondfolder, TESTSanalysisfiles[0])
        else:
            print("can't find TESTS_analysis file in", secondfolder, " - looking for RESULTS_analysis instead")
            RESULTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn and "_analysis" in fn]
            if RESULTSanalysisfiles:
                analysisfilepath = os.path.join(firstfolder, secondfolder, RESULTSanalysisfiles[0])
            else:
                print("can't find RESULTS_analysis file in", secondfolder, " - skipping to next folder")
                continue

        if True:
            filesdone.append(secondfolder)
            print("collecting test analysis info from " + secondfolder)

            # specification = ""
            # lang = ""
            # results = []
            onefileresults = main_overall_onefolder(analysisfilepath)
            lang = onefileresults["lang"]
            specs = onefileresults["specs"]
            results_strs = onefileresults["results_strs"]
            results_nums = onefileresults["results_nums"]
                #     "lang": langstring,
                #     "specs": specificationstring,
                #     "results_strs": resultstext,
                #     "results_nums": [avggoodfreq, avgbadfreq, num100pctgood, num90pctgood, num0pctgood, numtotal]

            if specs not in allresults.keys():
                allresults[specs] = {}
            if lang not in allresults[specs].keys():
                allresults[specs][lang] = []
            allresults[specs][lang].append((results_strs, results_nums))
            #
            # if results_nums[0] > highestresult:
            #     highestresult = results_nums[0]
            #     highestresultspecs = [specs]
            # elif results_nums[0] == highestresult:
            #     highestresultspecs.append(specs)

    with io.open(os.path.join(OUTPUTS_DIR, "summary_of_test_analysis_results.txt"), "w") as wf:
        for specs in allresults.keys():
            wf.write(specs+"\n")
            thisspec_overallavgfreqgood = 0
            thisspec_overallavgfreqbad = 0
            thisspec_numrunscounter = 0
            for lang in allresults[specs].keys():
                wf.write(lang+"\n")
                thislang_overallavgfreqgood = 0
                thislang_overallavgfreqbad = 0
                thislang_numrunscounter = 0

                printsimnum = True if len(allresults[specs][lang]) > 1 else False
                for idx, results_strs_nums in enumerate(allresults[specs][lang]):
                    results_strs, results_nums = results_strs_nums
                    if printsimnum:
                        wf.write("simulation " + str(idx+1) + "\n")
                    wf.write(results_strs)

                    thislang_overallavgfreqgood = ((thislang_overallavgfreqgood * thislang_numrunscounter) + (results_nums[0])) / (thislang_numrunscounter+1)
                    thislang_overallavgfreqbad = ((thislang_overallavgfreqbad * thislang_numrunscounter) + (results_nums[1])) / (thislang_numrunscounter+1)
                    thislang_numrunscounter += 1

                    thisspec_overallavgfreqgood = ((thisspec_overallavgfreqgood * thisspec_numrunscounter) + (results_nums[0])) / (thisspec_numrunscounter + 1)
                    thisspec_overallavgfreqbad = ((thisspec_overallavgfreqbad * thisspec_numrunscounter) + (results_nums[1])) / (thisspec_numrunscounter + 1)
                    thisspec_numrunscounter += 1
                wf.write("this lang under these specifications:\n")
                wf.write("\taverage frequency of good results = " + str(thislang_overallavgfreqgood) + "\n")
                wf.write("\taverage frequency of bad results = " + str(thislang_overallavgfreqbad) + "\n")
            wf.write("all langs under these specifications:\n")
            wf.write("\taverage frequency of good results = " + str(thisspec_overallavgfreqgood) + "\n")
            wf.write("\taverage frequency of bad results = " + str(thisspec_overallavgfreqbad) + "\n")
            wf.write("\n")
            #
            # if thisspec_overallavgfreqgood > highestresult:
            #     highestresult = thisspec_overallavgfreqgood
            #     highestresultspecs = [specs]
            # elif thisspec_overallavgfreqgood == highestresult:
            #     highestresultspecs.append(specs)
            #
            # if thisspec_overallavgfreqgood < lowestresult:
            #     lowestresult = thisspec_overallavgfreqgood
            #     lowestresultspecs = [specs]
            # elif thisspec_overallavgfreqgood == lowestresult:
            #     lowestresultspecs.append(specs)

            if thisspec_overallavgfreqgood not in resultsbyavggoodfreq.keys():
                resultsbyavggoodfreq[thisspec_overallavgfreqgood] = []
            lowestnumover90forthisspec = 1100
            for lang in allresults[specs].keys():
                for resstrs, resnums in allresults[specs][lang]:
                    if resnums[3] < lowestnumover90forthisspec:
                        lowestnumover90forthisspec = resnums[3]
            resultsbyavggoodfreq[thisspec_overallavgfreqgood].append((specs, lowestnumover90forthisspec))

        #
        # wf.write("highest average frequency of good results: " + str(highestresult) + "\n")
        # wf.write("specs with that frequency:\n")
        # for spec in highestresultspecs:
        #     wf.write("\t" + spec + "\n")
        #
        # wf.write("lowest average frequency of good results: " + str(lowestresult) + "\n")
        # wf.write("specs with that frequency:\n")
        # for spec in lowestresultspecs:
        #     wf.write("\t" + spec + "\n")

        wf.write("\n")

        resultsindescendingorder = sorted(([k for k in resultsbyavggoodfreq.keys()]), reverse=True)
        top20 = resultsindescendingorder[:20]
        bot20 = resultsindescendingorder[-20:]

        wf.write("top 20 average frequencies of good results:\n")
        for idx, freq in enumerate(top20):
            place = idx + 1
            specline = "{place:>3}) " + str(freq) + "\n"
            wf.write(specline.format(place=place))
            # wf.write(str(idx+1) + ". " + str(freq) + "\n")
            for spec, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                wf.write("\t" + spec + " (lowest num inputs above 90% good results = " + str(lowestnumabove90) + ")\n")
        wf.write("\n")
        wf.write("bottom 20 average frequencies of good results:\n")
        for idx, freq in enumerate(bot20):
            place = idx - 20
            specline = "{place:>3}) " + str(freq) + "\n"
            wf.write(specline.format(place=place))
            # wf.write(str(idx-10) + ") " + str(freq) + "\n")
            for spec, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                wf.write("\t" + spec + "\n")



if __name__ == "__main__":
    whattotest = ""
    while whattotest not in ["A", "I", "X"]:
        whattotest = input("Do you want to:\n"
                           + "\t- summarize results for each individual simulation folder (I)?\n"
                           + "\t- summarize results for all sim folders overall (A)?\n"
                           + "\t- exit (X)?\n").upper()
    if whattotest == "I":
        testindividualfolders()
    elif whattotest == "A":
        summarizeallfolders()
    elif whattotest == "X":
        sys.exit(0)

import io
import sys
from datetime import datetime

import pandas as pd
from pandasql import sqldf
# from sqlalchemy import text
import matplotlib.pyplot as plt
from itertools import product, chain, combinations
import re
import os
# import random
# import lfcd_otsoft_stratacleaner
from generate_tableaux_otsoft_specifylang import isintendedwinner, isalternatewinner, Fin, NEst, NSeto  # , KEst


typetoanalyze = "TESTS"  #  "RESULTS"
OUTPUTS_DIR = "../sim_outs/20240507_GLA_outputs"
t = "\t"
langstrings = ["Fin", "NEst", "NSeto"]

class Grammar:

    def __init__(self, language, grammarTESTSresultsfilepath, intendedtableauxfilepath):
        self.lang = language
        self.intendedtableauxfilepath = intendedtableauxfilepath
        self.TESTSfilepath = grammarTESTSresultsfilepath
        self.analysisfile = self.TESTSfilepath.replace("00.txt", "00_analysis.txt")
        self.containingfolder = os.path.split(self.TESTSfilepath)[0]
        self.constraints = []
        self.intendedtableaux_list = []
        self.grammarTESTStableaux_list = []

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

                    # if self.lang == KEst:
                    #     temp = ""
                    iscandintendedwinner = isintendedwinner(current_ur, cand, self.lang)
                    iscandalternatewinner = isalternatewinner(current_ur, cand, self.lang)

                    if iscandintendedwinner or iscandalternatewinner:
                        current_goodresultsfreq += outfreq
                    else:
                        current_badresultsfreq += outfreq


                ln = tf.readline()

        return results

# end of class Grammar #


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
        # return  # uncomment this if you only want results for settings that have been 100-sample tested

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
        # print("    already done; skipping")
        return
    testresults = grammar.collecttestresults()
    try:
        goodtestresults, badtestresults = zip(*testresults.values())
    except ValueError:
        print("ValueError on file", TESTSfilepath)
    totalresults = len(goodtestresults)
    averagegoodresults = sum(goodtestresults)/totalresults
    averagebadresults = sum(badtestresults)/totalresults
    numtestswXpercentgoodresults = {
        100: len([res for res in goodtestresults if res == 1]),
        99: len([res for res in goodtestresults if res >= 0.99]),
        95: len([res for res in goodtestresults if res >= 0.95]),
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

    # get rid of any existing results summary files
    avggoodresults_files = [fn for fn in os.listdir(grammar.containingfolder) if fn.endswith(".averagegoodresults")]
    for existing in avggoodresults_files:
        os.remove(os.path.join(grammar.containingfolder, existing))
    # set the new results summary file
    with io.open(os.path.join(grammar.containingfolder, str(averagegoodresults) + ".averagegoodresults"), "w") as rf:
        pass  # basically just want Unix "touch"

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


def main_overall_onefolder(analysisfilepath=None):
    if analysisfilepath is None:
        analysisfilepath = input("Enter relative filepath whose GLA TESTS results to analyze: ")

    analysisfolderpath, analysisfilename = os.path.split(analysisfilepath)
    analysisfoldername = os.path.split(analysisfolderpath)[1]

    begoflangstring = analysisfilename.index("PDDP-") + 5
    endoflangstring = analysisfilename.index("_GLA_")
    langstring = analysisfilename[begoflangstring:endoflangstring]

    specificationstring = analysisfoldername[:2] if analysisfoldername.startswith("c") else (analysisfoldername[:4] if analysisfoldername.startswith("redo") else "")
    reduced_analysisfoldername = analysisfoldername[len(specificationstring):]
    # begofspecificationstring = 2
    endofspecificationstring = reduced_analysisfoldername.index("_python") - 6
    specificationstring += reduced_analysisfoldername[:endofspecificationstring]  # [begofspecificationstring:endofspecificationstring]

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
                    elif "99%" in ln:
                        begofgood = ln.index("results:") + 9
                        endofgood = ln.index(" of ")
                        goodstring = ln[begofgood:endofgood]
                        num99pctgood = int(goodstring)
                    elif "95%" in ln:
                        begofgood = ln.index("results:") + 9
                        endofgood = ln.index(" of ")
                        goodstring = ln[begofgood:endofgood]
                        num95pctgood = int(goodstring)
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
        "results_nums": (avggoodfreq, avgbadfreq, num100pctgood, num99pctgood, num95pctgood, num90pctgood, num0pctgood, numtotal)
    }


def testindividualfolders():
    print("\n---------- I: summarizing results for each individual simulation folder ----------")
    filesdone = []

    firstfolder = OUTPUTS_DIR  # "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn))]  #  if "testycopy" in fn]  # if fn.startswith("T_Mgen")]
    for folder_idx, secondfolder in enumerate(folderstotest):
        if secondfolder.startswith("T_Mgen3.1.1_N"):
            temp = "pause here"
        deleteresultsanalysisifpossible = False
        TESTSfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "TESTS" in fn]
        if TESTSfiles:
            TESTSfilepath = os.path.join(firstfolder, secondfolder, TESTSfiles[0])
            deleteresultsanalysisifpossible = True
        else:
            # print("can't find TESTS file in", secondfolder, " - looking for RESULTS instead")
            RESULTSfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn]
            if RESULTSfiles:
                TESTSfilepath = os.path.join(firstfolder, secondfolder, RESULTSfiles[0])
            else:
                # print("can't find RESULTS file in", secondfolder, " - skipping to next folder")
                continue

        if True:
            filesdone.append(secondfolder)
            # print(str(folder_idx) + ". analyzing test results of grammar in " + secondfolder)
            if folder_idx % 100 == 0:
                print(str(datetime.now()) + " - analyzing test results of folder #" + str(folder_idx))
            main_individual(TESTSfilepath)

            # TODO
            # if deleteresultsanalysisifpossible:
            #     RESULTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn and "_analysis" in fn]
            #     for Raf in RESULTSanalysisfiles:
            #         print("deleting RESULTS_analysis file", Raf)
            #         os.remove(Raf)


def summarizeallfolders():
    print("\n---------- A: summarizing results for all sim folders overall ----------")
    
    filesdone = []
    firstfolder = OUTPUTS_DIR  # "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn))]  #  if "testycopy" in fn]  # if fn.startswith("T_Mgen")]
    allresults = {}
    # highestresult = 0.0
    # highestresultspecs = []  # list of strings
    # lowestresult = 1.0
    # lowestresultspecs = []  # list of strings
    resultsbyavggoodfreq = {}  # dict of float --> list of [tuple of (str, int)]
    resultsbyspec = {}  # dict of str --> float
        # freq of good results --> [(specs, lowest numover90 in these specs), ...]
    resultsbyspec_bylang = {}  # dict of str --> str --> (float, int, int, int, int)
        #  ie, specs --> lang --> (average frequency of good results, num results over 100%, over 99%, over 95%, over 90%)

    for secondfolder in folderstotest:
        TESTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "TESTS" in fn and "_analysis" in fn]
        if TESTSanalysisfiles:
            analysisfilepath = os.path.join(firstfolder, secondfolder, TESTSanalysisfiles[0])
        else:
            # print("can't find TESTS_analysis file in", secondfolder, " - looking for RESULTS_analysis instead")
            RESULTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn and "_analysis" in fn]
            if RESULTSanalysisfiles:
                analysisfilepath = os.path.join(firstfolder, secondfolder, RESULTSanalysisfiles[0])
            else:
                # print("can't find RESULTS_analysis file in", secondfolder, " - skipping to next folder")
                continue

        if True:
            filesdone.append(secondfolder)
            print("collecting test analysis info from " + secondfolder)

            onefileresults = main_overall_onefolder(analysisfilepath)
            lang = onefileresults["lang"]
            specs = onefileresults["specs"]
            results_strs = onefileresults["results_strs"]
            results_nums = onefileresults["results_nums"]
                #     "lang": langstring,
                #     "specs": specificationstring,
                #     "results_strs": resultstext,
                #     "results_nums": [avggoodfreq, avgbadfreq, num100pctgood, num99pctgood, num95pctgood, num90pctgood, num0pctgood, numtotal]

            if specs not in allresults.keys():
                allresults[specs] = {}
            if lang not in allresults[specs].keys():
                allresults[specs][lang] = []
            allresults[specs][lang].append((results_strs, results_nums))

    with io.open(os.path.join(OUTPUTS_DIR, "summary_of_test_analysis_results.txt"), "w") as wf:
        with io.open(os.path.join(OUTPUTS_DIR, "table_of_test_analysis_results.xls"), "w") as tf:
            with io.open(os.path.join(OUTPUTS_DIR, "table_of_test_analysis_results_bylang.xls"), "w") as lf:
                # header row for table
                tf.write("specs\tavg_freq_good_results\tlowest_inputs_above_100\tlowest_inputs_above_99\tlowest_inputs_above_95\tlowest_inputs_above_90\tM_string\tuniform_M\tM_value\tMgen_type\tb_3str\tm_3str\tb\tm\twhich_cand\tcalc_how\tmagri_type\tfavour_spec\tapriori_type\tReLU\n")
                lf.write("specs\tavg_freq_good_results_overall\tlang\tavg_freq_good_results_lang\tlowest_inputs_above_100\tlowest_inputs_above_99\tlowest_inputs_above_95\tlowest_inputs_above_90\tM_string\tuniform_M\tM_value\tMgen_type\tb_3str\tm_3str\tb\tm\twhich_cand\tcalc_how\tmagri_type\tfavour_spec\tapriori_type\tReLU\n")

                for specs in allresults.keys():
                    wf.write(specs+"\n")
                    thisspec_overallavgfreqgood = 0
                    # thisspec_overallavgfrqgood_bylang = {l:0 for l in langstrings}
                    resultsbyspec_bylang[specs] = {}
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

                        # thisspec_overallavgfrqgood_bylang[lang] = thislang_overallavgfreqgood
                        resultsbyspec_bylang[specs][lang] = (thislang_overallavgfreqgood, 1100, 1100, 1100, 1100)
                        wf.write("this lang under these specifications:\n")
                        wf.write("\taverage frequency of good results = " + str(thislang_overallavgfreqgood) + "\n")
                        wf.write("\taverage frequency of bad results = " + str(thislang_overallavgfreqbad) + "\n")
                    wf.write("all langs under these specifications:\n")
                    wf.write("\taverage frequency of good results = " + str(thisspec_overallavgfreqgood) + "\n")
                    wf.write("\taverage frequency of bad results = " + str(thisspec_overallavgfreqbad) + "\n")
                    wf.write("\n")

                    resultsbyspec[specs] = thisspec_overallavgfreqgood
                    if thisspec_overallavgfreqgood not in resultsbyavggoodfreq.keys():
                        resultsbyavggoodfreq[thisspec_overallavgfreqgood] = []
                    lowestnumover100forthisspec = 1100
                    lowestnumover99forthisspec = 1100
                    lowestnumover95forthisspec = 1100
                    lowestnumover90forthisspec = 1100
                    # numover100forthislang = {l:1100 for l in langstrings}
                    # numover99forthislang = {l:1100 for l in langstrings}
                    # numover95forthislang = {l:1100 for l in langstrings}
                    # numover90forthislang = {l:1100 for l in langstrings}

                    for lang in allresults[specs].keys():
                        for resstrs, resnums in allresults[specs][lang]:
                            lowestnumover100forthisspec = min(lowestnumover100forthisspec, resnums[2])
                            # numover100forthislang[lang] = resnums[2]
                            lowestnumover99forthisspec = min(lowestnumover99forthisspec, resnums[3])
                            # numover99forthislang[lang] = resnums[3]
                            lowestnumover95forthisspec = min(lowestnumover99forthisspec, resnums[4])
                            # numover95forthislang[lang] = resnums[4]
                            lowestnumover90forthisspec = min(lowestnumover99forthisspec, resnums[5])
                            # numover90forthislang[lang] = resnums[5]
                            resultsbyspec_bylang[specs][lang] = (resultsbyspec_bylang[specs][lang][0], resnums[2], resnums[3], resnums[4], resnums[5])
                    resultsbyavggoodfreq[thisspec_overallavgfreqgood].append((specs, lowestnumover100forthisspec, lowestnumover99forthisspec, lowestnumover95forthisspec, lowestnumover90forthisspec))

                wf.write("\n")

                resultsindescendingorder = sorted(([k for k in resultsbyavggoodfreq.keys()]), reverse=True)
                howmanyresults = len(allresults)
                top20 = resultsindescendingorder[:20]
                bot20 = resultsindescendingorder[-20:]
                above95percent_freqs = [fr for fr in resultsbyspec.values() if fr >= 0.95]
                above95percent_specs = [sp for sp in allresults.keys() if resultsbyspec[sp] >= 0.95]
                above99percent_freqs = [fr for fr in resultsbyspec.values() if fr >= 0.99]
                above99percent_specs = [sp for sp in allresults.keys() if resultsbyspec[sp] >= 0.99]
                below30percent_freqs = [fr for fr in resultsbyspec.values() if fr <= 0.30]
                below30percent_specs = [sp for sp in allresults.keys() if resultsbyspec[sp] <= 0.30]

                wf.write("there are " + str(len(above99percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or above 99%:\n")
                wf.write(str(sorted(above99percent_freqs, reverse=True)))
                wf.write("\n\n")
                wf.write("there are " + str(len(above95percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or above 95%:\n")
                wf.write(str(sorted(above95percent_freqs, reverse=True)))
                wf.write("\n\n")
                wf.write("there are " + str(len(below30percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or below 30%:\n")
                wf.write(str(sorted(below30percent_freqs, reverse=True)))
                wf.write("\n\n")

                wf.write("top 20 average frequencies of good results:\n")
                for idx, freq in enumerate(top20):
                    place = idx + 1
                    specline = "{place:>3}) " + str(freq) + "\n"
                    wf.write(specline.format(place=place))
                    for spec, lowestnumabove100, lowestnumabove99, lowestnumabove95, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                        wf.write("\t" + spec + "\n")
                        wf.write("\t\tlowest num inputs at 100% good results = " + str(lowestnumabove100) + "\n")
                        wf.write("\t\tlowest num inputs above 99% good results = " + str(lowestnumabove99) + "\n")
                        wf.write("\t\tlowest num inputs above 95% good results = " + str(lowestnumabove95) + "\n")
                        wf.write("\t\tlowest num inputs above 90% good results = " + str(lowestnumabove90) + "\n")
                wf.write("\n")
                wf.write("bottom 20 average frequencies of good results:\n")
                for idx, freq in enumerate(bot20):
                    place = idx - 20
                    specline = "{place:>3}) " + str(freq) + "\n"
                    wf.write(specline.format(place=place))
                    for spec, lowestnumabove100, lowestnumabove99, lowestnumabove95, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                        wf.write("\t" + spec + "\n")
                wf.write("\n")
                wf.write("ALL average frequencies of good results:\n")
                for idx, freq in enumerate(resultsindescendingorder):
                    place = idx + 1
                    specline = "{place:>3}) " + str(freq) + "\n"
                    wf.write(specline.format(place=place))
                    for spec, lowestnumabove100, lowestnumabove99, lowestnumabove95, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                        wf.write("\t" + spec + "\n")
                        wf.write("\t\tlowest num inputs at 100% good results = " + str(lowestnumabove100) + "\n")
                        wf.write("\t\tlowest num inputs above 99% good results = " + str(lowestnumabove99) + "\n")
                        wf.write("\t\tlowest num inputs above 95% good results = " + str(lowestnumabove95) + "\n")
                        wf.write("\t\tlowest num inputs above 90% good results = " + str(lowestnumabove90) + "\n")

                        # "specs\tavg_freq_good_results\tlowest_inputs_above_100\tlowest_inputs_above_99\tlowest_inputs_above_95\tlowest_inputs_above_90\tM_string\tuniform_M\tM_value\tMgen_type\tm\tb\twhich_cand\tcalc_how\tmagri_type\tfavour_spec\tapriori_type\tReLU\n"
                        tablerowstring = spec + t + str(freq) + t + str(lowestnumabove100) + t + str(lowestnumabove99) + t
                        tablerowstring += str(lowestnumabove95) + t + str(lowestnumabove90) + t

                        Mstring_start = spec.index("M") + 1
                        try:
                            Mstring_end = spec.index("_", Mstring_start)
                        except:
                            Mstring_end = len(spec)
                        Mstring = spec[Mstring_start:Mstring_end].replace("gen", "")
                        tablerowstring += Mstring + t

                        if "Mgen" in spec:
                            tablerowstring += "0" + t + t
                            Mgenidx = spec.index("Mgen")
                            Mgentype = spec[Mgenidx+4]
                            if spec[Mgenidx+4] == "3":
                                # endMgentype = spec.index("_", Mgenidx)
                                # Mgentype = spec[Mgenidx+4:endMgentype]
                                tablerowstring += Mgentype + t + t + t + t + t + t + t
                            elif spec[Mgenidx+4] in ["4", "5"]:
                                # Mgentype = spec[Mgenidx+4]
                                b_3str = spec[Mgenidx+6:Mgenidx+9]
                                b = int(b_3str)
                                m_3str = spec[Mgenidx+10:Mgenidx+13]
                                m = int(m_3str)
                                w = spec[Mgenidx+13] if Mgentype == "4" else ""
                                h = spec[Mgenidx+14] if Mgentype == "4" else ""
                                tablerowstring += Mgentype + t + b_3str + t + m_3str + t + str(b) + t + str(m) + t + w + t + h + t
                        else:
                            Midx = spec.index("M")
                            tablerowstring += "1" + t + spec[Midx+1:Midx+4] + t + "0" + t + t + t + t + t + t + t

                        if "_mg" in spec:
                            magritype = spec[spec.index("_mg")+3]
                            tablerowstring += magritype + t
                        else:
                            tablerowstring += "0" + t

                        tablerowstring += ("1" if "_fs" in spec else "0") + t

                        if "_sg" in spec:
                            apriori_idx = spec.index("_sg") + 3
                            apriori_end = spec.find("_", apriori_idx)
                            if apriori_end == -1:
                                apriori_end = len(spec)
                            aprioritype = spec[apriori_idx:apriori_end]
                            tablerowstring += aprioritype + t
                        else:
                            tablerowstring += "-1" + t

                        tablerowstring += ("1" if "ReLU" in spec else "0") + "\n"

                        tf.write(tablerowstring)

                for sp in resultsbyspec_bylang.keys():
                    for la in resultsbyspec_bylang[sp].keys():
                        # "specs\tlang\tavg_freq_good_results\tlowest_inputs_above_100\tlowest_inputs_above_99\tlowest_inputs_above_95\tlowest_inputs_above_90\tM_string\tuniform_M\tM_value\tMgen_type\tm\tb\twhich_cand\tcalc_how\tmagri_type\tfavour_spec\tapriori_type\tReLU\n"
                        # specs --> lang --> (average frequency of good results, num results over 100%, over 99%, over 95%, over 90%)
                        langtablerowstring = sp + t + str(resultsbyspec[sp]) + t
                        langtablerowstring += la + t + str(resultsbyspec_bylang[sp][la][0]) + t
                        langtablerowstring += str(resultsbyspec_bylang[sp][la][1]) + t
                        langtablerowstring += str(resultsbyspec_bylang[sp][la][2]) + t
                        langtablerowstring += str(resultsbyspec_bylang[sp][la][3]) + t
                        langtablerowstring += str(resultsbyspec_bylang[sp][la][4]) + t

                        Mstring_start = sp.index("M") + 1
                        try:
                            Mstring_end = sp.index("_", Mstring_start)
                        except:
                            Mstring_end = len(sp)
                        Mstring = sp[Mstring_start:Mstring_end].replace("gen", "")
                        langtablerowstring += Mstring + t

                        if "Mgen" in sp:
                            langtablerowstring += "0" + t + t
                            Mgenidx = sp.index("Mgen")
                            Mgentype = sp[Mgenidx+4]
                            if sp[Mgenidx+4] == "3":
                                # endMgentype = sp.index("_", Mgenidx)
                                # Mgentype = sp[Mgenidx+4:endMgentype]
                                langtablerowstring += Mgentype + t + t + t + t + t + t + t
                            elif sp[Mgenidx+4] in ["4", "5"]:
                                # Mgentype = sp[Mgenidx+4]
                                b_3str = sp[Mgenidx+6:Mgenidx+9]
                                b = int(b_3str)
                                m_3str = sp[Mgenidx+10:Mgenidx+13]
                                m = int(m_3str)
                                w = sp[Mgenidx+13] if Mgentype == "4" else ""
                                h = sp[Mgenidx+14] if Mgentype == "4" else ""
                                langtablerowstring += Mgentype + t + b_3str + t + m_3str + t + str(b) + t + str(m) + t + w + t + h + t
                        else:
                            Midx = sp.index("M")
                            langtablerowstring += "1" + t + sp[Midx+1:Midx+4] + t + "0" + t + t + t + t + t + t + t

                        if "_mg" in sp:
                            magritype = sp[sp.index("_mg")+3]
                            langtablerowstring += magritype + t
                        else:
                            langtablerowstring += "0" + t

                        langtablerowstring += ("1" if "_fs" in sp else "0") + t

                        if "_sg" in sp:
                            apriori_idx = sp.index("_sg") + 3
                            apriori_end = sp.find("_", apriori_idx)
                            if apriori_end == -1:
                                apriori_end = len(sp)
                            aprioritype = sp[apriori_idx:apriori_end]
                            langtablerowstring += aprioritype + t
                        else:
                            langtablerowstring += "-1" + t

                        langtablerowstring += ("1" if "ReLU" in sp else "0") + "\n"

                        lf.write(langtablerowstring)


def analyzebyparameter():
    print("\n---------- P: creating plots of spreadsheet results by parameter ----------")
    with io.open(os.path.join(OUTPUTS_DIR, "table_of_test_analysis_results.xls"), "r") as tf:
        df = pd.read_csv(tf, sep="\t", header=0, keep_default_na=False)

        df.plot.scatter(x="magri_type", y="avg_freq_good_results", alpha=0.5)
        plt.show()

        df.plot.scatter(x="apriori_type", y="avg_freq_good_results", alpha=0.5)
        plt.show()

        df.plot.scatter(x="Mgen_type", y="avg_freq_good_results", alpha=0.5)
        plt.show()


m_vals = [50, 100, 150] + [0, 40, 80]  # for initial states with all M cons at same value OR for stratified distributions
# m_vals = ["050", "100", "150", "300", "450"]
b_vals = [50, 100, 150] + [300, 500]  # for initial states with all M cons at same value
# b_vals = ["050", "100", "150", "300", "450"]
params_values = {
    "M_string": ["3." + ty + ".1" for ty in ["1", "2a", "2b"]] + [ty + "." + str(m) + "." + str(b) for ty in ["4", "5"] for m in m_vals for b in b_vals],
    "uniform_M": [0, 1],
    "M_value": [100, 300, 500],
    "Mgen_type": [0, 3, 4, 5],
    "m": m_vals,
    "b": b_vals,
    "magri_type": [0, 1, 2, 3, 4],
    "favour_spec": [0, 1],
    "apriori_type": [-1, 0, 10, 20, 30, 40],  # 25, 35
}
params_of_interest = ["apriori_type", "favour_spec", "magri_type", "Mgen_type", "b", "m"]
params_of_interest_strings = {p:[p + " = " + str(v) for v in params_values[p]] for p in params_of_interest}

def analyzeparametercombinations():  # b_gt=-1, m_gt=-1):
    print("\n---------- R: summarizing range of results for every combination of parameters ----------")
    # addedcriteria_list = []
    # if b_gt > -1:
    #     addedcriteria_list.append("b > " + str(b_gt).zfill(3))
    # if m_gt > -1:
    #     addedcriteria_list.append("m > " + str(m_gt).zfill(3))
    # if len(addedcriteria_list) > 0:
    #     addedcriteria_str = "     additional criteria: " + " ; ".join(addedcriteria_list)
    #     print(addedcriteria_str)

    param_powerset_toobig = powerset(params_of_interest)
    param_powerset = []
    for param_subset in param_powerset_toobig:
        if "Mgen_type" not in param_subset:
            new_subset = [p for p in param_subset if p not in ["b", "m"]]
            if new_subset not in param_powerset:
                param_powerset.append(new_subset)
        elif param_subset not in param_powerset:
            param_powerset.append(param_subset)
    with io.open(os.path.join(OUTPUTS_DIR, "table_of_test_analysis_results_bylang.xls"), "r") as srcfile:
        with io.open(os.path.join(OUTPUTS_DIR, "table_of_param_combo_ranges.xls"), "w") as destfile:
            destfile.write(t.join(params_of_interest + ["min_avg_result", "max_avg_result", "min_Fin_result", "max_Fin_result", "min_NEst_result", "max_NEst_result", "min_NSeto_result", "max_NSeto_result", "num_params"]) + "\n")
            df = pd.read_csv(srcfile, sep="\t", header=0)
            df.drop(columns=["b_3str", "m_3str"], inplace=True)
            df.fillna({"M_value": -1, "m": -1, "b": -1}, inplace=True)
            df["b"] = df["b"].mask(df["M_value"] > -1, df["M_value"])
            df["m"] = df["m"].mask(df["M_value"] > -1, 0)
            df["b"] = df["b"].mask(df["M_string"] == "3.1.1", 100)
            df["b"] = df["b"].mask(df["M_string"] == "3.2a.1", 100)
            df["b"] = df["b"].mask(df["M_string"] == "3.2b.1", 100)
            df["m"] = df["m"].mask(df["M_string"] == "3.1.1", 40)
            df["m"] = df["m"].mask(df["M_string"] == "3.2a.1", 80)
            df["m"] = df["m"].mask(df["M_string"] == "3.2b.1", 80)
            # df.astype({"b": "int64"})
            # df.astype({"m": "int64"})
            # df.astype({"M_value": "int64"})

            for param_combo in param_powerset:
                print(param_combo)
                tup = tuple([params_of_interest_strings[p] for p in param_combo])
                string_tuples = list(product(*tup))

                for st in string_tuples:
                    # print(st)
                    condition_str = " AND ".join(list(st))  #  + (addedcriteria_list if "Mgen_type" in param_combo else []))
                    minmax_all_str = "SELECT avg_freq_good_results_overall, lang, avg_freq_good_results_lang FROM df"
                    minmax_all_str += (" WHERE " + condition_str) if condition_str else ""
                    reduced_df_all = sqldf(minmax_all_str)
                    if reduced_df_all.empty:
                        # print("     no results for", st)
                        continue
                    elif reduced_df_all.shape[0] < 3 != 0:
                        print("     missing a subset of language results for", st)
                        continue
                    minmax_df_all = sqldf(
                        "SELECT MIN(avg_freq_good_results_overall) AS min, MAX(avg_freq_good_results_overall) AS max FROM reduced_df_all")
                    minresult_all = minmax_df_all["min"].iloc[0]
                    maxresult_all = minmax_df_all["max"].iloc[0]
                    reduced_df_langs = sqldf("SELECT lang, MIN(avg_freq_good_results_lang) AS min, MAX(avg_freq_good_results_lang) AS max FROM reduced_df_all GROUP BY lang")
                    minresult_langs = {lang: reduced_df_langs.loc[reduced_df_langs["lang"] == lang]["min"].iloc[0]
                                       for lang in langstrings}
                    maxresult_langs = {lang: reduced_df_langs.loc[reduced_df_langs["lang"] == lang]["max"].iloc[0]
                                       for lang in langstrings}

                    tablerowstring = ""
                    numparams = 0
                    for p in params_of_interest:  # "apriori_type", "favour_spec", "magri_type", "Mgen_type", "b", "m"
                        expr = [s for s in st if p + " = " in s]
                        if len(expr) > 0:
                            expr = expr[0]
                            numparams += 1
                            validx_start = expr.index(" = ") + 3
                            tablerowstring += expr[validx_start:]
                        tablerowstring += t
                    tablerowstring += str(minresult_all) + t + str(maxresult_all) + t
                    for lang in langstrings:
                        tablerowstring += str(minresult_langs[lang]) + t + str(maxresult_langs[lang]) + t
                    tablerowstring += str(numparams) + "\n"
                    destfile.write(tablerowstring)


# https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
def powerset(s):
    powset = list(chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1)))
    return [list(tup) for tup in powset]



if __name__ == "__main__":
    while True:
        itemstotest = input("\nDo you want to:\n"
                           + "\t- summarize results for each individual simulation folder (I)?\n"
                           + "\t- summarize results for all sim folders overall (A)?\n"
                           + "\t- summarize results for both I + A: each individual sim folder, followed by overall (B)?\n"
                           + "\t- see plots of spreadsheet results by parameter (P)?\n"
                           + "\t- summarize range of results for every combination of parameters (R)?\n"
                           + "\t- exit (X)?\n").upper()
        for whattotest in itemstotest:
            if whattotest == "I":
                testindividualfolders()
            elif whattotest == "A":
                summarizeallfolders()
            elif whattotest == "B":
                testindividualfolders()
                summarizeallfolders()
            elif whattotest == "P":
                analyzebyparameter()
            elif whattotest == "R":
                analyzeparametercombinations()  # b_gt=50)
            elif whattotest == "X":
                print("\n---------- X: exiting ----------")
                sys.exit(0)

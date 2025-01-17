import io
import sys

import pandas as pd
import re
import os
# import random
# import lfcd_otsoft_stratacleaner
from generate_tableaux_otsoft_specifylang import isintendedwinner, isalternatewinner, Fin, NEst, NSeto  # , KEst


# typetoanalyze = "TESTS"  #  "RESULTS"
OUTPUTS_DIR = os.path.join("C:" + os.sep, "UCLAPhonotacticLearner", "baltofinnic")
OUTPUTFOLDERPREFIX = "output_"


class Grammar:

    def __init__(self, language, blickTestResultsfilepath):
        self.lang = language
        self.testsfilepath = blickTestResultsfilepath
        self.analysisfile = self.testsfilepath.replace(".txt", "_analysis.txt")
        self.containingfolder = os.path.split(self.testsfilepath)[0]
        # self.constraints = []
        # self.intendedtableaux_list = []
        # self.grammarTESTStableaux_list = []

    def collecttestresults(self):
        words = {}
        nonwords = {}

        with io.open(self.testsfilepath, "r") as tf:
            ln = tf.readline()
            while ln.startswith("word"):
                ln = tf.readline()

            while ln != "":
                row_values = ln.strip().split("\t")
                current_word = row_values[0]
                current_score = float(row_values[1])
                current_isword = row_values[-1] == "word"

                if current_isword:
                    words[fixsymbols(current_word)] = current_score
                else:
                    nonwords[fixsymbols(current_word)] = current_score

                ln = tf.readline()

        return words, nonwords

# end of class Grammar #


def fixsymbols(txt):
    txt = txt.replace("uh", "E").replace("ih", "I").replace("ae", "A").replace("oe", "O")
    txt = txt.replace(" ", "")
    return txt


def main_individual(blicktestfolderpath=None):
    if blicktestfolderpath is None:
        blicktestfolderpath = input("Enter relative filepath whose UCLAPL MaxEnt blick test results to analyze: ")
    blicktestfoldername = os.path.split(blicktestfolderpath)[1]

    begoflangstring = blicktestfoldername.index(OUTPUTFOLDERPREFIX) + 7
    endoflangstring = blicktestfoldername.find("_", begoflangstring)
    langstring = blicktestfoldername[begoflangstring:endoflangstring]
    begofcustomizationstring = endoflangstring + 1
    # customizationstring = blicktestfoldername[begofcustomizationstring:]

    foldercontents = os.listdir(blicktestfolderpath)
    blickfiles = [f for f in foldercontents if os.path.isfile(os.path.join(blicktestfolderpath, f)) and "blick" in f]
    if len(blickfiles) == 0:
        print("folder " + blicktestfoldername + " doesn't contain a blick test file; skipping")
        return
    blickfiletestpath = os.path.join(blicktestfolderpath, blickfiles[0])

    grammar = Grammar(langstring, blickfiletestpath)
    if os.path.exists(grammar.analysisfile):
        # already done; skip this one
        print("    already done; skipping")
        return
    word_results, nonword_results = grammar.collecttestresults()

    minwordscore = min(word_results.values())
    maxwordscore = max(word_results.values())
    minnonwordscore = min(nonword_results.values())
    maxnonwordscore = max(nonword_results.values())

    ambiguous_words = {w: s for w, s in word_results.items() if s > minnonwordscore}
    ambiguous_nonwords = {nw: s for nw, s in nonword_results.items() if s < maxwordscore}
    num_ambiguous_words = len(ambiguous_words)
    num_ambiguous_nonwords = len(ambiguous_nonwords)

    num_totalresults = len(word_results) + len(nonword_results)
    num_unambiguousresults = num_totalresults - num_ambiguous_words - num_ambiguous_nonwords
    proportion_unambiguousresults = num_unambiguousresults / num_totalresults

    with io.open(grammar.analysisfile, "w") as wf:
        wf.write(grammar.testsfilepath + "\n")
        wf.write("\n")
        wf.write("word scores range from " + str(minwordscore) + " to " + str(maxwordscore) + "\n")
        wf.write("nonword scores range from " + str(minnonwordscore) + " to " + str(maxnonwordscore) + "\n")
        wf.write("\n")
        if maxwordscore < minnonwordscore:
            wf.write("there is a partition between words and nonwords\n")
        else:
            wf.write("there is overlap (no partition) between words and nonwords\n")
        wf.write("\n")
        wf.write("there are " + str(num_ambiguous_words) + " ambiguous words:\n")
        for aw in ambiguous_words.keys():
            wf.write("   " + aw + " : " + str(ambiguous_words[aw]) + "\n")
        wf.write("\n")
        wf.write("there are " + str(num_ambiguous_nonwords) + " ambiguous nonwords:\n")
        for anw in ambiguous_nonwords.keys():
            wf.write("   " + anw + " : " + str(ambiguous_nonwords[anw]) + "\n")
        wf.write("\n")
        wf.write(str(proportion_unambiguousresults) + " of results are unambiguous\n")

    # get rid of any existing results summary files
    proportionunambiguousresults_files = [fn for fn in os.listdir(grammar.containingfolder) if fn.endswith(".proportionunambiguousresults")]
    for existing in proportionunambiguousresults_files:
        os.remove(os.path.join(grammar.containingfolder, existing))
    # set the new results summary file
    with io.open(os.path.join(grammar.containingfolder, str(proportion_unambiguousresults) + ".proportionunambiguousresults"), "w") as rf:
        pass  # basically just want Unix "touch"


# TODO update
def main_overall_onefolder(analysisfilepath=None):
    if analysisfilepath is None:
        analysisfilepath = input("Enter relative analysis filepath whose MaxEnt blick test results to analyze: ")

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
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn)) and fn.startswith(OUTPUTFOLDERPREFIX)]
    for secondfolder in folderstotest:
        deleteresultsanalysisifpossible = False
        blicktestfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "blick" in fn]
        if blicktestfiles:
            blicktestfilepath = os.path.join(firstfolder, secondfolder, blicktestfiles[0])
            deleteresultsanalysisifpossible = True
        else:
            print("can't find blick tests file in", secondfolder, " - looking for RESULTS instead")
            continue

        if True:
            filesdone.append(secondfolder)
            print("analyzing blick test results of grammar in " + secondfolder)
            main_individual(os.path.join(firstfolder, secondfolder))

            # TODO
            # if deleteresultsanalysisifpossible:
            #     RESULTSanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "RESULTS" in fn and "_analysis" in fn]
            #     for Raf in RESULTSanalysisfiles:
            #         print("deleting RESULTS_analysis file", Raf)
            #         os.remove(Raf)


def summarizeallfolders():
    filesdone = []
    firstfolder = OUTPUTS_DIR  # "../sim_ins/20240507 on - OTSoft inputs"
    folderstotest = [fn for fn in os.listdir(firstfolder) if os.path.isdir(os.path.join(OUTPUTS_DIR, fn)) and fn.startswith(OUTPUTFOLDERPREFIX)]
    allresults = {}
    # highestresult = 0.0
    # highestresultspecs = []  # list of strings
    # lowestresult = 1.0
    # lowestresultspecs = []  # list of strings
    resultsbypropunambigous = {}  # dict of float --> str
    resultsbyspec = {}  # dict of str --> float

    for secondfolder in folderstotest:
        blicktestanalysisfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "blick" in fn and "_analysis" in fn]
        if blicktestanalysisfiles:
            analysisfilepath = os.path.join(firstfolder, secondfolder, blicktestanalysisfiles[0])
        else:
            print("can't find blick tests analysis file in", secondfolder)
            continue

        if True:
            filesdone.append(secondfolder)
            print("collecting blick test analysis info from " + secondfolder)

            # TODO continue from here
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

            resultsbyspec[specs] = thisspec_overallavgfreqgood
            if thisspec_overallavgfreqgood not in resultsbyavggoodfreq.keys():
                resultsbyavggoodfreq[thisspec_overallavgfreqgood] = []
            lowestnumover90forthisspec = 1100
            for lang in allresults[specs].keys():
                for resstrs, resnums in allresults[specs][lang]:
                    if resnums[3] < lowestnumover90forthisspec:
                        lowestnumover90forthisspec = resnums[3]
            resultsbyavggoodfreq[thisspec_overallavgfreqgood].append((specs, lowestnumover90forthisspec))

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

        wf.write("there are " + str(len(above95percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or above 95%:\n")
        wf.write(str(sorted(above95percent_freqs, reverse=True)))
        wf.write("\n\n")
        wf.write("there are " + str(len(above99percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or above 99%:\n")
        wf.write(str(sorted(above99percent_freqs, reverse=True)))
        wf.write("\n\n")
        wf.write("there are " + str(len(below30percent_specs)) + " of " + str(howmanyresults) + " sets of specs with results at or below 30%:\n")
        wf.write(str(sorted(below30percent_freqs, reverse=True)))
        wf.write("\n\n")

        wf.write("top 20 average frequencies of good results:\n")
        for idx, freq in enumerate(top20):
            place = idx + 1
            specline = "{place:>3}) " + str(freq) + "\n"
            wf.write(specline.format(place=place))
            for spec, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                wf.write("\t" + spec + " (lowest num inputs above 90% good results = " + str(lowestnumabove90) + ")\n")
        wf.write("\n")
        wf.write("bottom 20 average frequencies of good results:\n")
        for idx, freq in enumerate(bot20):
            place = idx - 20
            specline = "{place:>3}) " + str(freq) + "\n"
            wf.write(specline.format(place=place))
            for spec, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                wf.write("\t" + spec + "\n")
        wf.write("\n")
        wf.write("ALL average frequencies of good results:\n")
        for idx, freq in enumerate(resultsindescendingorder):
            place = idx + 1
            specline = "{place:>3}) " + str(freq) + "\n"
            wf.write(specline.format(place=place))
            for spec, lowestnumabove90 in resultsbyavggoodfreq[freq]:
                wf.write("\t" + spec + " (lowest num inputs above 90% good results = " + str(lowestnumabove90) + ")\n")


if __name__ == "__main__":
    whattotest = ""
    while whattotest not in ["A", "I", "B", "X"]:
        whattotest = input("Do you want to:\n"
                           + "\t- summarize results for each individual output folder (I)?\n"
                           + "\t- summarize results for all output folders overall (A)?\n"
                           + "\t- summarize results for both I + A: each individual output folder, followed by overall (B)?\n"
                           + "\t- exit (X)?\n").upper()
    if whattotest == "I":
        testindividualfolders()
    elif whattotest == "A":
        summarizeallfolders()
    elif whattotest == "B":
        testindividualfolders()
        summarizeallfolders()
    elif whattotest == "X":
        sys.exit(0)

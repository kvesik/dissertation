import os
import io


def main(resultsfilepath=None):
    if resultsfilepath is None:
        resultsfilepath = input("Enter relative filepath whose GLA constraint values to compare: ")

    # resultsfilefolder, resultsfilename = os.path.split(resultsfilepath)
    comparisonfilepath = resultsfilepath.replace("RESULTS", "STARTvsEND").replace(".txt", ".xls")
    # comparisonfilepath = os.path.join(resultsfilefolder, comparisonfilename)
    historyfilepath = resultsfilepath.replace("RESULTS", "HISTORY")

    if os.path.exists(comparisonfilepath):
        # already done; skip this one
        print("    already done; skipping")
        return

    with io.open(historyfilepath, "r") as hf:
        constraintcoltitles = []
        startingvalues = []
        endingvalues = []
        con_start_end = []

        ln = hf.readline().replace("\n", "")
        if ln.startswith("trialnum"):
            constraintcoltitles = ln.split("\t")[3:]

        while ln != "":
            if ln.startswith("\t\t\t"):
                startingvalues = ln.split("\t")[4:]
            elif ln.startswith("TOTAL"):
                endingvalues = ln.split("\t")[4:]
            ln = hf.readline().replace("\n", "")

        for idx in range(len(startingvalues)):
            conname = constraintcoltitles[idx]
            if conname != "now":
                startval = str(round(float(startingvalues[idx]), 3))
                endval = str(round(float(endingvalues[idx]), 3))
                con_start_end.append((conname, startval, endval))
        # con_start_end = [(constraintcoltitles[idx], round(float(startingvalues[idx]), 3), round(float(endingvalues[idx]), 3) for idx in range(len(startingvalues)) if constraintcoltitles[idx] != "now"]
        con_start_end.sort(key=lambda x: float(x[1]), reverse=True)

    with io.open(comparisonfilepath, "w") as wf:
        wf.write("\t".join(["constraint", "startingvalue", "endingvalue"]) + "\n")
        for triplet in con_start_end:
            wf.write("\t".join(triplet) + "\n")


if __name__ == "__main__":
    filesdone = []
    firstfolder = "../sim_outs/20240507_GLA_outputs"
    folderswithGLAfiles = [fn for fn in os.listdir(firstfolder) if "OTSoft-PDDP" in fn and "_GLA" in fn]
    for secondfolder in folderswithGLAfiles:
        Resultsfiles = [fn for fn in os.listdir(os.path.join(firstfolder, secondfolder)) if "_GLA_RESULTS" in fn and fn.endswith(".txt")]
        if Resultsfiles:
            resultspath = os.path.join(firstfolder, secondfolder, Resultsfiles[0])
        else:
            print("can't find results file in", secondfolder, " - skipping to next folder")
            continue
        if True:  # "Fin" in DOfile or "NSeto" in DOfile or "SSeto" in DOfile:  # True
            filesdone.append(secondfolder)
            print("comparing start and end constraint values in " + secondfolder)
            main(resultspath)

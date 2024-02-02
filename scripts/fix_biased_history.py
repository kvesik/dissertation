import io
import re
import os


def maketabs(numtabs):
    tabs = ""
    for i in range(numtabs):
        tabs += "\t"
    return tabs


def write_new_biased_history(sourcepath):

    with io.open(sourcepath, "r") as src:
        with io.open(re.sub("FullHistory.", "FullHistory_fixed.", sourcepath), "w") as dest:
            ln = src.readline()
            counter = 1
            lookingforsubsteps = False
            numtabs = 0
            substeps_string = ""
            apriori_string = ""
            while ln != "":
                # print("line " + str(counter) + ": " + ln)
                counter += 1
                cellvalues = ln.split('\t')
                cvtail = cellvalues[-5:]
                if ln.startswith("Generated"):  # header row
                    ln = re.sub("Adj[.] Num\s", "", ln)  # this column doesn't seem to be used, and is throwing off the alignment
                    numtabs = ln.count("\t")
                    # dest.write("trialnum\t" + ln)
                    dest.write(ln)
                elif ln.startswith("Apriori"):
                    firstindexofdoubletab = ln.index('\t\t')
                    # grp1 = re.sub("(.*)\t(-?\d+[.]?\d*\t-?\d+[.]?\d*)", r'\1', ln)
                    # grp2 = re.sub("(.*)\t(-?\d+[.]?\d*\t-?\d+[.]?\d*)", r'\2', ln)
                    # lnnew = re.sub("(.*)\t(-?\d+[.]?\d*\t-?\d+[.]?\d*)", r'\1\2', ln)
                    dest.write(ln[:firstindexofdoubletab] + ln[firstindexofdoubletab+1:])
                elif ln.startswith("(Initial)"):
                    dest.write(ln)
                # elif re.match(".+\S#\S.*\n", ln):  # if a line contains something like:    #FF #BB#FF  #BB ...
                elif len(cellvalues[2]) > 0 and cellvalues[2] + cellvalues[0] == cellvalues[1]:
                    # dest.write(re.findall(r'#\S+(#\S+\s+#\S+\s+-?\d+[.]?\d*\s+-?\d+[.]?\d*.*\n)', ln)[0])
                    cellvalues[1] = cellvalues[2]
                    cellvalues[2] = ""
                    newln = '\t'.join(cellvalues)
                    firstindexofdoubletab = newln.index('\t\t')
                    dest.write(newln[:firstindexofdoubletab] + newln[firstindexofdoubletab+1:])
                elif len(cellvalues[2]) == 0 and len(cellvalues[0]) == len(cellvalues[1]):
                # elif re.match("#\S+\t#\S+\t.*\n", ln):  # if it's a data line
                    dest.write(ln)

                ln = src.readline()


def main(relfilepath=None):
    if relfilepath is None:
        relfilepath = input("Enter relative filepath whose full-history file formatting to fix: ")

    write_new_biased_history(relfilepath)


if __name__ == "__main__":
    firstfolder = "../simulation_outputs/20231010-20231017_GLA_outputs"  # /ins and outs for LFCD runs 20231005"
    for fname1 in os.listdir(firstfolder):
        if os.path.isdir(firstfolder + "/" + fname1) and "FilesForOTSoft" in fname1 and "GLA" in fname1:
            secondfolder = fname1
            for fname2 in os.listdir(firstfolder + "/" + secondfolder):
                if fname2.endswith("FullHistory.xls"):
                    print("cleaning history file in " + secondfolder)
                    main(firstfolder + "/" + secondfolder + "/" + fname2)

    # main("C:\Program Files\OTSoft2.6\FilesForKE_iFBfb_posonly_negtest_cat_KPplus_wd\e126 - 20210720 - KE_iFBfb_posonly_negtest_cat_KPplus_wdFullHistory.tsv")
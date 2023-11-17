import io
import re
import os


def maketabs(numtabs):
    tabs = ""
    for i in range(numtabs):
        tabs += "\t"
    return tabs


def write_new_biased_history_compressed(sourcepath):

    with io.open(sourcepath, "r") as src:
        with io.open(re.sub("FullHistory.", "FullHistory_fixed.", sourcepath), "w") as dest:
            ln = src.readline()
            counter = 1
            lookingforsubsteps = False
            numtabs = 0
            substeps_string = ""
            apriori_string = ""
            while ln != "":
                print("line " + str(counter) + ": " + ln)
                counter += 1
                if ln.startswith("Generated"):  # header row
                    ln = re.sub("Adj[.] Num\s", "", ln)  # this column doesn't seem to be used, and is throwing off the alignment
                    numtabs = ln.count("\t")
                    dest.write(ln)
                elif ln.startswith("Apriori"):
                    if substeps_string != "":
                        # save for after this collection of changes
                        apriori_string = re.sub("(.*)\t(-?\d+[.]?\d*\t-?\d+[.]?\d*)", r'\1\2', ln)
                    else:
                        ln = re.sub("(.*)\t(-?\d+[.]?\d*\t-?\d+[.]?\d*)", r'\1\2', ln)
                        dest.write(ln)
                elif ln.startswith("(Initial)"):
                    # ln.replace("(Initial)", "(Initial)\t")  # fine once the extra column in removed
                    if substeps_string != "":
                        # write the changes (associated with one error) that were being collected, if any
                        dest.write(substeps_string + maketabs(numtabs - substeps_string.count("\t")) + "\n")
                        substeps_string = ""
                        dest.write(apriori_string)
                        apriori_string = ""
                    dest.write(ln)
                elif re.match(".+\S#\S.*\n", ln):  # if a line contains something like:    #FF #BB#FF  #BB ...
                    if substeps_string != "":
                        # write the changes (associated with one error) that were being collected, if any
                        dest.write(substeps_string + maketabs(numtabs - substeps_string.count("\t")) + "\n")
                        substeps_string = ""
                        dest.write(apriori_string)
                        apriori_string = ""
                    # restart the collection of changes
                    # substeps_string = re.sub("(.+\S)(#\S+\t#\S+\t+-?\d+[.]?\d*\t-?\d+[.]?\d*)(.*\n)", r'\2', ln)  # remove the first chunk; it's not doing anything
                    substeps_string = re.findall(r'#\S+(#\S+\s+#\S+\s+-?\d+[.]?\d*\s+-?\d+[.]?\d*)', ln)[0]
                elif re.match("#\S+\t#\S+\t.*\n", ln):  # if it's a data line
                    currenttabs = substeps_string.count("\t")
                    truncated_ln = re.sub("\t+\n", r'\n', ln)
                    newtabs = truncated_ln.count("\t")
                    # newchunk = re.sub(r'(.*)(-?\d+[.]?\d*\t-?\d+[.]?\d*)(.*\n)', r'\2', truncated_ln)
                    newchunk = re.findall(r'(-?\d+[.]?\d*\s+-?\d+[.]?\d*)', truncated_ln)[0]
                    substeps_string += maketabs(newtabs-currenttabs) + newchunk

                ln = src.readline()


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
    firstfolder = "OTSoft2.6old/run stuff dir/ins and outs for GLA runs 20231115"  # /ins and outs for LFCD runs 20231005"
    for fname1 in os.listdir(firstfolder):
        if os.path.isdir(firstfolder + "/" + fname1) and "FilesForOTSoft" in fname1 and "GLA" in fname1:
            secondfolder = fname1
            for fname2 in os.listdir(firstfolder + "/" + secondfolder):
                if fname2.endswith("FullHistory.xls"):
                    print("cleaning history file in " + secondfolder)
                    main(firstfolder + "/" + secondfolder + "/" + fname2)

    # main("C:\Program Files\OTSoft2.6\FilesForKE_iFBfb_posonly_negtest_cat_KPplus_wd\e126 - 20210720 - KE_iFBfb_posonly_negtest_cat_KPplus_wdFullHistory.tsv")
import os
import io


def main(displayonly=False):
    outputs_folder = os.path.join("..", "sim_outs", "20240507_GLA_outputs")  # , "rename_slopeandyint_multipliers")
    os.chdir(outputs_folder)
    inputfolders = [f for f in os.listdir() if os.path.isdir(f)]

    if displayonly:  # then we're just displaying
        # TODO uncomment whichever methods you need!
        # orig_As_outputs(inputfolders)
        anyoutputswith_(inputfolders, "os_")
    else:  # then we're actually renaming
        for f in inputfolders:
            f_new = f
            # TODO uncomment whichever methods you need!
            # f_new = renumber_OG_Mgen(f_new)
            # f_new = rejig_2ndtry_folders(f_new)
            # f_new = renumber_Mgen_methods(f_new)
            # f_new = rename_Mgen_refineALL(f_new)
            # f_new = relabel_OG_Mgen_candcalc(f_new)
            # f_new = relabel_misnumbered_Mgen_runs(f_new)
            f_new = relabel_50to050_folders(f_new)

            if f == f_new:
                print("no change:", f)
            else:
                if f_new in inputfolders:
                    f_new = f_new + " try2"
                print(f, "-->", f_new)
                os.rename(f, f_new)


def relabel_50to050_folders(f):
    return f.replace(".50", ".050")


def relabel_misnumbered_Mgen_runs(f):
    Mgentype_startidx = f.find("Mgen")
    if Mgentype_startidx >= 0:
        edit_summary_test_inside_results_file(f)

        Mgentype_stopidx = f.find("_", Mgentype_startidx)
        Mgentype_full = f[Mgentype_startidx:Mgentype_stopidx]

        # renaming y-int and slope multipliers to be 3x as big as they originally were
        Mgentype_pieces = Mgentype_full.split(".")
        new_yint = 3 * int(Mgentype_pieces[1])
        new_slope = 3 * int(Mgentype_pieces[2])

        newcode = ".".join([Mgentype_pieces[0], str(new_yint), str(new_slope)])
        newfoldername = f[:Mgentype_startidx] + newcode + f[Mgentype_stopidx:]
        return newfoldername

    else:
        return f


def edit_summary_test_inside_results_file(folder):
    resultsfile = [f for f in os.listdir(folder) if "RESULTS" in f][0]
    thetext = ""
    with io.open(os.path.join(folder, resultsfile), "r") as f:
        thetext = f.read().replace("type 5.150", "type 5.450").replace("type 5.100", "type 5.300").replace("type 5.050", "type 5.150").replace(".050 - randomized", ".150 - randomized").replace(".100 - randomized", ".300 - randomized")
    with io.open(os.path.join(folder, resultsfile), "w") as f:
        f.write(thetext)


def relabel_OG_Mgen_candcalc(f):
    Mgentype_startidx = f.find("Mgen")
    if Mgentype_startidx >= 0:
        Mgentype_stopidx = f.find("_", Mgentype_startidx)
        Mgentype_full = f[Mgentype_startidx:Mgentype_stopidx]

        newcode = Mgentype_full  # defaults to no change

        # renaming candidate choice & calculation strategy from "As" to "Fs"
        if Mgentype_full.endswith("Os"):
            newcode = Mgentype_full[:-2] + "os"

        newfoldername = f[:Mgentype_startidx] + newcode + f[Mgentype_stopidx:]
        return newfoldername

    else:
        return f


def renumber_Mgen_methods(f):
    Mgentype_startidx = f.find("Mgen")
    if Mgentype_startidx >= 0:
        Mgentype_stopidx = f.find("_", Mgentype_startidx)
        Mgentype_full = f[Mgentype_startidx:Mgentype_stopidx]
        Mgentype = Mgentype_full[4:]

        newcode = Mgentype  # defaults to no change

        # renaming "method 1" to "method 4"
        if Mgentype.startswith("1."):
            newcode = "4" + Mgentype[1:]

        # each of these renamed types is the main method,
        # followed by sub-method if applicable,
        # followed lastly by specific numerical settings for this instance
        elif Mgentype == "2.1":
            newcode = "3.2a.1"
        elif Mgentype == "3.1":
            newcode = "3.1.1"
        elif Mgentype == "4.1":
            newcode = "3.2b.1"
        elif Mgentype.startswith("4.") and len(Mgentype) > 6:
            # print("already renamed:", f)
            pass
        else:
            print("exception: Mgentype", Mgentype, "in folder", f)

        newfoldername = f[:Mgentype_startidx] + "Mgen" + newcode + f[Mgentype_stopidx:]
        return newfoldername

    else:
        return f


def rename_Mgen_refineALL(f):
    Mgentype_startidx = f.find("Mgen")
    if Mgentype_startidx >= 0:
        Mgentype_stopidx = f.find("_", Mgentype_startidx)
        Mgentype_full = f[Mgentype_startidx:Mgentype_stopidx]
        Mgentype = Mgentype_full[4:]

        if Mgentype.endswith("as"):
            newfoldername = f[:Mgentype_startidx] + "Mgen" + Mgentype.replace("as", "As") + f[Mgentype_stopidx:]
            # "As" with a capital A means that this is done the old way, with precisely one look at each input
            # (effectively, a batch size of 1100)
            return newfoldername
    return f


def rejig_2ndtry_folders(f):
    return f.replace("2nd try", "try2").replace("2try", "try2")


def renumber_OG_Mgen(f):
    Mgentype_startidx = f.find("Mgen1.")
    if Mgentype_startidx >= 0:
        Mgentype_stopidx = f.find("_", Mgentype_startidx)
        Mgentype_full = f[Mgentype_startidx:Mgentype_stopidx]
        Mgentype = Mgentype_full[4:]
        # if Mgentype_full.endswith("a"):  # calculated by averages
        #     calcby = "a"
        #     Mgentype = Mgentype_full[4:-1]
        # elif Mgentype_full.endswith("s"):  # calculated by sums
        #     calcby = "s"
        #     Mgentype = Mgentype_full[4:-1]
        # else:  # no tag; default is sums
        #     calcby = "s"
        #     Mgentype = Mgentype_full[4:]
            
        # each of these renamed types is the main type (calculated from inputs), 
        # followed by xxx% (ie, x.xx) for the y-int multipler and xxx% (ie, x.xx) for the slope multiplier,
        # followed lastly by the method for calculating generality (sums vs averages)
        if Mgentype == "1.1":
            newcode = "050.050"
        elif Mgentype == "1.2":
            newcode = "100.100"
        elif Mgentype == "1.3":
            newcode = "150.150"
        elif Mgentype == "1.4":
            newcode = "025.025"
        elif Mgentype == "1.5":
            newcode = "025.050"
        elif Mgentype == "1.6":
            newcode = "025.100"
        elif Mgentype == "1.7":
            newcode = "200.025"
        elif Mgentype == "1.8":
            newcode = "050.100"
        elif Mgentype == "1.9":
            newcode = "050.200"
        elif Mgentype == "1.11":
            newcode = "050.025"
        elif Mgentype == "1.12":
            newcode = "100.025"
        elif Mgentype == "1.13":
            newcode = "075.025"
        elif Mgentype == "1.14":
            newcode = "075.050"
        elif Mgentype == "1.15":
            newcode = "100.050"
        elif Mgentype == "1.16":
            newcode = "025.075"
        elif Mgentype == "1.17":
            newcode = "050.075"
        elif Mgentype == "1.18":
            newcode = "075.075"
        elif Mgentype == "1.19":
            newcode = "100.075"
        elif Mgentype == "1.21":
            newcode = "075.100"
        elif Mgentype == "1.22":
            newcode = "040.040"
        elif Mgentype == "1.23":
            newcode = "060.040"
        elif Mgentype == "1.24":
            newcode = "040.050"
        elif Mgentype == "1.25":
            newcode = "060.050"
        elif Mgentype == "1.26":
            newcode = "040.060"
        elif Mgentype == "1.27":
            newcode = "060.060"
        elif Mgentype == "1.28":
            newcode = "050.040"
        elif Mgentype == "1.29":
            newcode = "050.085"

        newfoldername = f[:Mgentype_startidx] + "Mgen1." + newcode + "as" + f[Mgentype_stopidx:]
        # "as" means all candidates + calculated by sums
        return newfoldername

    else:
        return f


def orig_As_outputs(folderslist):
    foundany = False
    for folder in folderslist:
        filesinfolder = os.listdir(folder)
        # TESTfilesinfolder = [f for f in filesinfolder if "TEST" in f]
        if "As_" in folder and len(filesinfolder) <= 4:
            print("folder " + folder + " has 4 or fewer files and may have been calculated recently")
            foundany = True
    if not foundany:
        print("didn't find any suspicious folders")


def anyoutputswith_(folderslist, seq):
    foundany = False
    for folder in folderslist:
        filesinfolder = os.listdir(folder)
        # TESTfilesinfolder = [f for f in filesinfolder if "TEST" in f]
        if seq in folder:
            print(folder)
            foundany = True
    if not foundany:
        print("didn't find any " + seq + " folders")


if __name__ == "__main__":
    main(displayonly=False)

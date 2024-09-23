import os


def main():
    outputs_folder = os.path.join("..", "sim_outs", "20240507_GLA_outputs")
    os.chdir(outputs_folder)
    inputfolders = [f for f in os.listdir() if os.path.isdir(f)]
    for f in inputfolders:
        f_new = rejig_2ndtry_folders(renumber_Mgen(f))

        if f == f_new:
            print("no change:", f)
        else:
            print(f, "-->", f_new)
            os.rename(f, f_new)


def rejig_2ndtry_folders(f):
    if "2nd try" in f:
        oldtext = "2nd try"
    elif "2try" in f:
        oldtext = "2try"
    else:
        return f

    return f.replace(oldtext, "try2")


def renumber_Mgen(f):
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


if __name__ == "__main__":
    main()

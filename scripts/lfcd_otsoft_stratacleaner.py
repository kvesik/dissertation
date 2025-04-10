import io
import os


def main(relfilepath=None):
    if relfilepath is None:
        relfilepath = input("Enter relative filepath whose output-strata formatting to fix: ")

    with io.open(relfilepath, "r") as rf:
        cleanedfilepath = relfilepath.replace("DraftOutput.txt", "DraftOutput_strata.txt")
        print("source:", relfilepath)
        print("dest:", cleanedfilepath)
        with io.open(cleanedfilepath, "w") as wf:

            rline = rf.readline()
            strata_ended = False
            while len(rline) > 0 and not strata_ended:
                rline = rline.strip()
                if rline.startswith("2. Tableaux"):
                    strata_ended = True
                elif rline.startswith("Stratum"):
                    wf.write(rline + "\n")
                else:
                    chunks = rline.split()
                    if len(chunks) == 2 and chunks[0] == chunks[1]:
                        wf.write(chunks[0] + "\n")
                rline = rf.readline()


if __name__ == "__main__":
    firstfolder = os.path.join("..", "sim_outs", "20250207_LFCD_outputs")
    for fname1 in os.listdir(firstfolder):
        if os.path.isdir(os.path.join(firstfolder, fname1)) and "FilesForOTSoft" in fname1 and "LFCD" in fname1:
            secondfolder = fname1
            foldercontents = os.listdir(os.path.join(firstfolder, secondfolder))
            draftoutputfiles = [fn for fn in foldercontents if fn.endswith("DraftOutput.txt")]
            if len(draftoutputfiles) > 0:
                print("cleaning strata in " + secondfolder)
                for fname2 in draftoutputfiles:
                    if not os.path.exists(os.path.join(firstfolder, secondfolder, fname2.replace("DraftOutput.txt", "DraftOutput_strata.txt"))):
                        main(os.path.join(firstfolder, secondfolder, fname2))


    # main("OTSoft2.6old - use this loc as of 20230413 - prev files in Program Files/R03 - FilesForOTSoft_Fin_GLA_PDDP_nodia/OTSoft_Fin_GLA_PDDP_nodiaFullHistory.xls")

    # asks for user to input file path
    # main()
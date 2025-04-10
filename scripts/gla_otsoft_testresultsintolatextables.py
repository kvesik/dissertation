import io
import pandas as pd
import os


OUTPUTS_DIR = "../sim_outs/20240507_GLA_outputs"
langstrings = ["NEst", "Fin", "NSeto"]

apriorivalues = [-1, 0, 10, 20, 30, 40]
favspecvalues = [0, 1]
promratepairs = [
    (0, "default"),
    (1, "Type 1: \promtype{1}"),
    (2, "Type 2: \promtype{2}"),
    (3, "Type 3: \promtype{3}"),
    (4, "Type 4: \promtype{4}")
]

bottomrule_multiplesof = len(promratepairs) * len(favspecvalues) * len(apriorivalues)
cmidrule2to7_multiplesof = len(promratepairs) * len(favspecvalues)
cmidrule3to7_multiplesof = len(promratepairs)

def readresults_writetablerows(counter, df, tablefilepath, b_str=None, m_str=None):
    with io.open(tablefilepath, "w") as tablefile:
        for apriori in apriorivalues:
            for favspec in favspecvalues:
                for promratepair in promratepairs:
                    settingstowrite = "     " + str(counter) + ". & "
                    settingstowrite += ("none" if apriori == -1 else str(apriori)) + " & "
                    settingstowrite += ("" if favspec else "in") + "active" + " & "
                    settingstowrite += promratepair[1]

                    resultstowrite = ""
                    for lang in langstrings:
                        if b_str and m_str:
                            freq = df.loc[(df['apriori_type'] == apriori) &
                                          (df['favour_spec'] == favspec) &
                                          (df['magri_type'] == promratepair[0]) &
                                          (df['lang'] == lang) &
                                          (df['b_3str'] == b_str) &
                                          (df['m_3str'] == m_str)]['avg_freq_good_results_lang'].iloc[0]
                        else:
                            freq = df.loc[(df['apriori_type'] == apriori) &
                                          (df['favour_spec'] == favspec) &
                                          (df['magri_type'] == promratepair[0]) &
                                          (df['lang'] == lang)]['avg_freq_good_results_lang'].iloc[0]
                        pct = freq * 100
                        resultstowrite += " & " + "$" + "{:.2f}".format(pct) + "$"

                    tablefile.write(settingstowrite + resultstowrite + "\\\\* \n")
                    if counter % bottomrule_multiplesof == 0:
                        tablefile.write("     \\bottomrule\n")
                    elif counter % cmidrule2to7_multiplesof == 0:
                        tablefile.write("     \cmidrule{2-7}\n")
                    elif counter % cmidrule3to7_multiplesof == 0:
                        tablefile.write("     \cmidrule{3-7}\n")
                    counter += 1
    return counter


if __name__ == "__main__":

    with io.open(os.path.join(OUTPUTS_DIR, "table_of_test_analysis_results_bylang.xls"), "r") as infile:
        df = pd.read_csv(infile, sep="\t", header=0, keep_default_na=False)
        counter = 1

        for distfcn in [1, 2, 3, 4, 5]:
            print("Creating table rows for distribution function {}".format(distfcn))
            if distfcn == 1:  # uniform initial M
                for initM in [100, 300, 500]:
                    tablefilepath = "tablerows_distfcn{}_initM{}.txt".format(distfcn, initM)
                    print(os.path.split(tablefilepath)[1])
                    smallerdf = df.loc[(df['uniform_M'] == 1) & (df['M_value'] == str(initM))]
                    counter = readresults_writetablerows(counter, smallerdf, tablefilepath)
            elif distfcn == 2:  # stratified by constraint type
                tablefilepath = "tablerows_distfcn{}.txt".format(distfcn)
                print(os.path.split(tablefilepath)[1])
                smallerdf = df.loc[df['M_string'] == "3.1.1"]
                counter = readresults_writetablerows(counter, smallerdf, tablefilepath)
            elif distfcn == 3:  # stratified by reference set
                for direction in ["topdown", "bottomup"]:
                    tablefilepath = "tablerows_distfcn{}_{}.txt".format(distfcn, direction)
                    print(os.path.split(tablefilepath)[1])
                    if direction == "topdown":
                        smallerdf = df.loc[df['M_string'] == "3.2a.1"]
                    elif direction == "bottomup":
                        smallerdf = df.loc[df['M_string'] == "3.2b.1"]
                    counter = readresults_writetablerows(counter, smallerdf, tablefilepath)
            elif distfcn in [4, 5]:  # data-informed or random
                for b_str in ["050", "100", "150"]:
                    for m_str in ["050", "100"]:
                        tablefilepath = "tablerows_distfcn{}_b{}_m{}.txt".format(distfcn, b_str, m_str)
                        print(os.path.split(tablefilepath)[1])
                        stringtomatch = str(distfcn) + "." + b_str + "." + m_str + ("fs" if distfcn == 4 else "")
                        smallerdf = df.loc[df['M_string'] == stringtomatch]
                        counter = readresults_writetablerows(counter, smallerdf, tablefilepath, b_str=b_str, m_str=m_str)

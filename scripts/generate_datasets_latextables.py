import io

from generate_tableaux_otsoft_specifylang import makeinputstrings, iswordinlang, NEst, Fin, NSeto, i, e, A, y, O, I, E, a, u, o, front, back

vowels = {
    front: [i, e, A, y, O],
    back: [I, E, a, u, o]
}
allsegments = vowels[front] + vowels[back]
yes = "y"
no = "n"

latexlookup = {
    i: i,
    e: e,
    A: "\\ae",
    y: y,
    O: "\\o",
    I: "\\textturnm",
    E: "\\textramshorns",
    a: "\\textscripta",
    u: u,
    o: o,
    ".": "."
}


# modifies the input dict in-place
def padlists(seqlenlists):
    # {2: {k: [] for k in vowels[fb]}, 3: {k: [] for k in vowels[fb]}}
    toreturn = []
    for seqlen, wordlists in seqlenlists.items():
        maxlen = max([len(wdlist) for wdlist in wordlists.values()])
        toreturn.append(maxlen)
        for k, v in wordlists.items():
            if len(v) < maxlen:
                seqlenlists[seqlen][k].extend([""]*(maxlen - len(v)))
    return tuple(toreturn)


def formatforlatex(vowelseq):
    return "".join([latexlookup[v] for v in vowelseq])


def buildline(yesorno, wordsdict, idx, withstar=False):
    linetowrite = ""
    for k in (vowels[front] if i in wordsdict.keys() else vowels[back]):
        vseq = wordsdict[k][idx]
        linetowrite += " & " + ("*" if yesorno == no and vseq else "") + vseq
    linetowrite += " \\\\" + ("*" if withstar else "") + " \n"
    linetowrite = "    " + linetowrite.strip(" & ")
    return linetowrite


def writeliststofile(lang, frontorback, yesorno, lists):
    # {2: {k: [] for k in vowels[fb]}, 3: {k: [] for k in vowels[fb]}}
    filename = "{}_{}_data_{}.txt".format(lang, frontorback, yesorno)
    print("populating " + filename + " ...")
    maxlen2, maxlen3 = padlists(lists)

    with io.open(filename, "w") as outfile:
        for idx in range(maxlen2):
            outfile.write(buildline(yesorno, lists[2], idx, withstar=True))
        outfile.write("    \\midrule\n")
        for idx in range(maxlen3):
            outfile.write(buildline(yesorno, lists[3], idx))
        outfile.write("    \\bottomrule\n")


if __name__ == "__main__":
    length2wordsfront = makeinputstrings([vowels[front], allsegments], ucla=True)
    length2wordsback = makeinputstrings([vowels[back], allsegments], ucla=True)

    length3wordsfront = makeinputstrings([vowels[front], allsegments, allsegments], ucla=True)
    length3wordsback = makeinputstrings([vowels[back], allsegments, allsegments], ucla=True)

    wordpairlists = {
        front: {
            2: [(wd.replace(".", ""), formatforlatex(wd.replace(".", "..."))) for wd in length2wordsfront],
            3: [(wd.replace(".", ""), formatforlatex(wd.replace(".", "..."))) for wd in length3wordsfront]
        },
        back: {
            2: [(wd.replace(".", ""), formatforlatex(wd.replace(".", "..."))) for wd in length2wordsback],
            3: [(wd.replace(".", ""), formatforlatex(wd.replace(".", "..."))) for wd in length3wordsback]
        }
    }

    for lang in [NEst, Fin, NSeto]:
        for fb in [front, back]:
            yesnolists = {
                yes: {2: {k: [] for k in vowels[fb]}, 3: {k: [] for k in vowels[fb]}},
                no: {2: {k: [] for k in vowels[fb]}, 3: {k: [] for k in vowels[fb]}},
            }

            for seqlen in [2, 3]:
                for wdpair in wordpairlists[fb][seqlen]:
                    if iswordinlang(wdpair[0], lang):
                        yesnolists[yes][seqlen][wdpair[0][0]].append(wdpair[1])
                    else:
                        yesnolists[no][seqlen][wdpair[0][0]].append(wdpair[1])

            for yn in [yes, no]:
                writeliststofile(lang, fb, yn, yesnolists[yn])

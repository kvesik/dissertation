

from generate_tableaux_otsoft_specifylang import makeinputstrings, allsegments, iswordinlang, NEst, Fin, NSeto

length2words = makeinputstrings([allsegments, allsegments], ucla=True)
# length2words_nodelims = [wd.replace(".", "") for wd in length2words]
# length2words_3dotdelims = [wd.replace(".", "...") for wd in length2words]
length2words_pairs = [(wd.replace(".", ""), wd.replace(".", "...")) for wd in length2words]

length3words = makeinputstrings([allsegments, allsegments, allsegments], ucla=True)
# length3words_nodelims = [wd.replace(".", "") for wd in length3words]
# length3words_3dotdelims = [wd.replace(".", "...") for wd in length3words]
length3words_pairs = [(wd.replace(".", ""), wd.replace(".", "...")) for wd in length3words]




if __name__ == "__main__":
    print("TODO")

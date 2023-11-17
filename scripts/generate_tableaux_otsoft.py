from itertools import product
import io
import pandas as pd
import sys
import os

i_only = ["i"]
mids = ["e", "õ"]
markedfronts_unmarkedbacks = ["F", "B"]
allsegs = i_only + mids + markedfronts_unmarkedbacks
classes = [i_only, mids, markedfronts_unmarkedbacks]

fronts = ["e", "F"]
neutrals = ["i"]
backs = ["õ", "B"]
marked = ["F", "õ"]
unmarked = ["B", "e", "i"]

front = "front"
back = "back"
neutral = "neutral"

IdBkSyl1 = "Id(Bk)Syl1"
IdBk = "Id(Bk)"
IdBkFt1 = "Id(Bk)Ft1"
AgrBk = "Agr(Bk)"

star_F = "*F"  # K&P marked fronts
GMHF = "GMHF"
star_7 = "*õ"  # K&P marked back
GMH7 = "GMHõ"
star_B = "*B"  # K&P unmarked backs
GMHB = "GMHB"
star_FB = "*F*B"  # K&P marked fronts and unmarked backs
GMHFB = "GMHFB"
star_e = "*e"  # unmarked nonhigh front
GMHe = "GMHe"
star_7e = "*õ*e"  # mid unrounded - in hierarchy A & B
GMH7e = "GMHõe"
star_7e2o = "*e*F*õ*B"  # "*e*ö*õ*o"  # mid - in hierarchy A & C
GMH7e2o = "GMHeFõB"  # "GMHeöõo"
star_e2 = "*e*F"  # "*e*ö"  # mid front - in hierarchy C & D
GMHe2 = "GMHeF"  # "GMHeö"
star_e47a = "*e*ä*õ*a"  # nonhigh unrounded - in hierarchy B & F
GMHe47a = "GMHeäõa"
star_e4 = "*e*ä"  # front nonhigh unrounded - in hierarchy E & F
GMHe4 = "GMHeä"
star_e42 = "*e*ä*ö"  # front nonhigh - in hierarchy D & E
GMHe42 = "GMHeäö"
star_e27o4a = "*e*ä*õ*a*ö*o"  # nonghigh - in hierarchy A & B & C & D & E & F
GMHe27o4a = "GMHeäõaö"


finalQP2constraints = [star_F, star_7, star_e, IdBkSyl1, IdBk, AgrBk, GMHF, GMH7, GMHe]
adaptedQP2constraints = [star_F, star_7, star_7e, IdBkSyl1, IdBk, AgrBk, GMHF, GMH7, GMHe]
starBQP2constraints = [star_F, star_B, star_7, star_e, IdBkSyl1, IdBk, AgrBk, GMHF, GMHB, GMH7, GMHe]
removeGMHcons = [star_F, star_B, star_7, star_e, IdBkSyl1, IdBk, AgrBk, GMHF, GMHe]
stringencycons1 = [star_7, star_7e, star_F, star_FB, IdBkSyl1, IdBk, AgrBk, GMH7, GMH7e, GMHF, GMHFB]
stringencycons2 = [star_7, star_F, star_e2, star_7e2o, IdBkSyl1, IdBk, AgrBk, GMH7, GMHF, GMHe2, GMH7e2o]
stringencycons3 = [star_7, star_7e, star_F, star_e2, star_7e2o, IdBkSyl1, IdBk, AgrBk, GMH7e, GMH7, GMHF, GMHe2, GMH7e2o]
# finalQP2constraints = [star_F, star_7, star_e, IdBkSyl1, IdBk, AgrBk, GMHF, GMHe]
# finalQP2constraints = [star_F, star_7, star_e, IdBkSyl1, IdBkFt1, IdBk, AgrBk, GMHF, GMH7, GMHe]

KE = "KE"
SE = "SE"


def makeinputstrings(segmentsperposition):
    inputs = [combo for combo in product(*segmentsperposition)]
    inputs = ["".join(combo) for combo in inputs]
    return inputs


def get_frontback_candidates(wd):
    if wd == "":
        return [""]
    for i, segment in enumerate(wd):
        for cls in classes:
            if segment in cls:
                options = []
                for s in cls:
                    options.extend([s+suffix for suffix in get_frontback_candidates(wd[i+1:])])
                return options


def getbackness(segment):
    if segment in neutrals:
        return neutral
    elif segment in backs:
        return back
    else:
        return front


def gmhset_wd_violations(segmentslist, candidate):
    ct = 0
    for seg in segmentslist:
        ct += gmh_wd_violations(seg, candidate)
    return 1 if ct > 0 else 0  # should be max 1 violation per word


def gmh_wd_violations(segment, candidate):
    ct = 0
    for i in range(len(candidate) - 1):
        violate_agree = (candidate[i] in fronts + neutrals) != (candidate[i + 1] in fronts + neutrals)
        violate_star_seg = candidate.count(segment) > 0  # in word
        ct += int(violate_agree and violate_star_seg)
    return 1 if ct > 0 else 0  # should be max 1 violation per word


def numviolations(inputform, candidate, constraint):
    if constraint.startswith("*"):  # must be of form "*a*b*c"
        bannedsegments = [seg for seg in constraint.split("*") if seg != ""]
        numviolations = 0
        for s in bannedsegments:
            numviolations += candidate.count(s)
        return numviolations
    elif constraint == IdBkSyl1:
        return int(inputform[0] != candidate[0])
    elif constraint == IdBkFt1:
        ct = 0
        for i in range(2):
            ct += int(inputform[i] != candidate[i])
        return ct
    elif constraint == IdBk:
        ct = 0
        for i in range(len(inputform)):
            ct += int(inputform[i] != candidate[i])
        return ct
    elif constraint == AgrBk:
        ct = 0
        for i in range(len(candidate)-1):
            ct += int((candidate[i] in fronts + neutrals) != (candidate[i+1] in fronts + neutrals))
        return ct
    elif constraint.startswith("GMH"):
        segments = constraint[3:]
        return gmhset_wd_violations(segments, candidate)
    # elif constraint == GMHF:
    #     return gmh_wd_violations("F", candidate)
    # elif constraint == GMHB:
    #     return gmh_wd_violations("B", candidate)
    # elif constraint == GMHFB:
    #     return gmhset_wd_violations(["F", "B"], candidate)
    # elif constraint == GMH7:
    #     return gmh_wd_violations("õ", candidate)
    # elif constraint == GMHe:
    #     return gmh_wd_violations("e", candidate)
    # elif constraint == GMH7e:
    #     return gmhset_wd_violations(["õ", "e"], candidate)
    else:
        print("constraint not recognized: " + constraint)
        return -1


def firstnonneutral(wd):
    for segment in wd:
        if segment != "i":
            return segment
    return "i"


def isintendedwinner(inputform, candidate, lang):
    isintendedwinner = False
    backnesses = [getbackness(segment) for segment in candidate]
    if lang == KE:
        isintendedwinner = (backnesses.count(front) == 0 or backnesses.count(back) == 0) and firstnonneutral(inputform) == firstnonneutral(candidate)
    elif lang == SE:
        unmarkeds = [v for v in candidate[1:] if v in unmarked]
        if (len(unmarkeds) == len(candidate[1:])) and (candidate[0] == inputform[0]):
            isintendedwinner = True
    else:
        print("language " + lang + " not recognized; sorry")
        sys.exit(1)
    return isintendedwinner


def getviolations(inputform, candidate, constraintset):
    return [numviolations(inputform, candidate, con) for con in constraintset]


def generate_tableaux(inputs, constraintset, lang, relativefrequencies=None):
    # with io.open("OTSoft_"+lang+"_iFBfb_forGLA_cat_removeGMHQP2cons_no2xcounts.txt", "w", encoding='ANSI') as fGLA:
    #     with io.open("OTSoft_"+lang+"_iFBfb_forLFCD_cat_removeGMHQP2cons_no2xcounts.txt", "w", encoding='ANSI') as fLFCD:
    with io.open("OTSoft_"+lang+"_GLA_stringencycons3.txt", "w", encoding='ANSI') as fGLA:
        with io.open("OTSoft_"+lang+"_LFCD_stringencycons3.txt", "w", encoding='ANSI') as fLFCD:
            print("\t\t\t" + "\t".join(constraintset))
            print("\t\t\t" + "\t".join(constraintset))
            fGLA.write("\t\t\t" + "\t".join(constraintset) + "\n")
            fGLA.write("\t\t\t" + "\t".join(constraintset) + "\n")
            fLFCD.write("\t\t\t" + "\t".join(constraintset) + "\n")
            fLFCD.write("\t\t\t" + "\t".join(constraintset) + "\n")
            ct = 0
            for wd in inputs:
                listofcandidates = get_frontback_candidates(wd)
                onetableau = ""
                hasfaithfulwinner = False
                for idx, cand in enumerate(listofcandidates):
                    violns = [str(violn) for violn in getviolations(wd, cand, constraintset)]
                    outstring = wd if idx == 0 else ""
                    outstring += "\t" + cand + "\t"
                    if isintendedwinner(wd, cand, lang) and wd == cand:
                        # faithful winner; use in learning data
                        outstring += "1\t"
                        ct += 1
                        hasfaithfulwinner = True
                    else:
                        outstring += "\t"
                    outstring += "\t".join(violns)
                    onetableau += outstring + "\n"
                print(onetableau.strip())
                if relativefrequencies is not None and wd in relativefrequencies.keys():
                    for numcopies in range(relativefrequencies[wd]):
                        fGLA.write(onetableau)
                else:
                    # if relativefrequencies is None:
                    #     print("relative frequencies is None")
                    # elif wd not in relativefrequencies.keys():
                    #     print("wd " + wd + " not in relfreqs keys")
                    fGLA.write(onetableau)
                if hasfaithfulwinner:
                    fLFCD.write(onetableau)
            return ct


def readrelfreqs(filename):
    if not os.path.isfile(filename):
        return None

    relativefrequencies = {}
    with io.open(filename, "r", encoding="ANSI") as freqfile:
        df = pd.read_csv(freqfile, sep="\t", header=None, keep_default_na=False)
        for idx, row in df.iterrows():
            ngram = row[0].replace("7", "õ")
            relativefrequencies[ngram] = int(row[1])
    return relativefrequencies


def generatetext(candidates, constraintset, lang):
    print("\nfaithful only (" + lang + ") - number of words used: " + str(generate_tableaux(candidates, constraintset, lang, relativefrequencies=readrelfreqs("ngramcounts"+lang+"_1000.txt"))) + " of " + str(len(candidates)) + "\n\n")


length2words = makeinputstrings([allsegs, allsegs])
length3words = makeinputstrings([allsegs, allsegs, allsegs])
somelongerwords = ["iieB", "iiFõ", "iiiBe", "iiiiõF", "iiiiõ"]
# generatetext(length2words+length3words+somelongerwords, removeGMHcons, KE)
# generatetext(length2words+length3words+somelongerwords, removeGMHcons, SE)
# generatetext(length2words+length3words+somelongerwords, stringencycons1, KE)
# generatetext(length2words+length3words+somelongerwords, stringencycons1, SE)
# generatetext(length2words+length3words+somelongerwords, stringencycons2, KE)
# generatetext(length2words+length3words+somelongerwords, stringencycons2, SE)
generatetext(length2words+length3words+somelongerwords, stringencycons3, KE)
generatetext(length2words+length3words+somelongerwords, stringencycons3, SE)

# words_from_OTSoft_experiments = ["iõ", "ie", "iB", "iF", "õi", "ei", "Bi", "Fi", "BB", "BF", "FB", "FF",
#                                  "FBB", "õõ", "õe", "eõ", "ee", "eõõ", "Bõ", "Be", "Fõ", "Fe", "FBõ", "Fõõ",
#                                  "õB", "õF", "eF", "eB", "eõB", "eBB", "BiB", "BiF", "FiF", "FiB",
#                                  "õiõ", "õie", "eie", "eiõ", "Biõ", "Bie", "Fiõ", "Fie",
#                                  "õiB", "õiF", "eiF", "eiB", "FiBiF", "FiBiB", "õee"
#                                  ]


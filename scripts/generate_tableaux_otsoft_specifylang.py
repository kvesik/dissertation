from itertools import product
import io
import pandas as pd
import sys
import os
import math
from datetime import datetime

initial = "initial"
noninitial = "noninitial"
anywhere = "anywhere"

front = "front"
back = "back"
# neutral = "neutral"
high = "high"
low = "low"
rnd = "round"

# KE = "KE"
# SE = "SE"
NEst = "NEst"
SEst = "SEst"
SSeto = "SSeto"
NSeto = "NSeto"
Fin = "Fin"
fullset = "fullset"
langnames = [NEst, SSeto, NSeto, Fin]

i = "i"
I = "I"  # OTSoft
# I = "ɨ"
# I = "ih"  # UCLA
e = "e"
E = "E"  # OTSoft
# E = "õ"
# E = "uh"  # UCLA
o = "o"
O = "O"  # OTSoft
# O = "ö"
# O = "oe"  # UCLA
y = "y"
# w = "ɯ"
u = "u"
a = "a"
A = "A"  # OTSoft
# A = "ä"
# A = "ae"  # UCLA

vowels_features = {
    i: {
        back: False,
        high: True,
        low: False,
        rnd: False
    },
    I: {
        back: True,
        high: True,
        low: False,
        rnd: False
    },
    e: {
        back: False,
        high: False,
        low: False,
        rnd: False
    },
    E: {
        back: True,
        high: False,
        low: False,
        rnd: False
    },
    o: {
        back: True,
        high: False,
        low: False,
        rnd: True
    },
    O: {
        back: False,
        high: False,
        low: False,
        rnd: True
    },
    y: {
        back: False,
        high: True,
        low: False,
        rnd: True
    },
    u: {
        back: True,
        high: True,
        low: False,
        rnd: True
    },
    a: {
        back: True,
        high: False,
        low: True,
        rnd: False
    },
    A: {
        back: False,
        high: False,
        low: True,
        rnd: False
    },
}

# back; high; low; round
features_vowels = {
    True: {
        True: {
            True: {
                True: None,
                False: None
            },
            False: {
                True: u,
                False: I
            }
        },
        False: {
            True: {
                True: None,
                False: a
            },
            False: {
                True: o,
                False: E
            }
        }
    },
    False: {
        True: {
            True: {
                True: None,
                False: None
            },
            False: {
                True: y,
                False: i
            }
        },
        False: {
            True: {
                True: None,
                False: A
            },
            False: {
                True: O,
                False: e
            }
        }
    }
}

fbcorrespondents = {
    i: I,
    I: i,
    e: E,
    E: e,
    o: O,
    O: o,
    y: u,
    u: y,
    a: A,
    A: a
}

f1 = [O]
f3 = [O, A, y]
f4 = [O, A, y, e]
f5 = [O, A, y, e, i]
b1 = [I]
b2 = [I, E]
b3 = [I, E, o]
b5 = [I, E, o, a, u]

# sets = {
#     "F1": f1,
#     "F3": f3,
#     "F4": f4,
#     "F5": f5,
#     "B1": b1,
#     "B2": b2,
#     "B3": b3,
#     "B5": b5
# }

sets_dict = {
    fullset: {
        "F1": f1,
        "F3": f3,
        "F4": f4,
        "F5": f5,
        "B1": b1,
        "B2": b2,
        "B3": b3,
        "B5": b5
    },
    # for simplified Finnish learning
    Fin: {
        "F3": f3,
        "F5": f5,
        "B2": b2,
        "B5": b5
    },
    # for simplified(-ish) S Seto learning
    SSeto: {
        "F1": f1,
        "F3": f3,
        "F4": f4,
        "F5": f5,
        "B1": b1,
        "B2": b2,
        "B5": b5
    },
    # for simplified N Seto learning
    NSeto: {
        "F4": f4,
        "F5": f5,
        "B1": b1,
        "B5": b5
    },
    # for simplified N Estonian learning
    NEst: {
        "F3": f3,
        "B1": b1,
        "B2": b2
    }
}

# segM_connames = {setname: "*"+setname for setname in sets["all"].keys()}

# star_f1 = "*F1"
# star_f3 = "*F3"
# star_f4 = "*F4"
# star_f5 = "*F5"
# star_b1 = "*B1"
# star_b2 = "*B2"
# star_b3 = "*B3"
# star_b5 = "*B5"

# # for the full complement of constraints
# frontsets = [f1, f3, f4, f5]
# backsets = [b1, b2, b3, b5]
frontsegments = f5
backsegments = b5
allsegments = f5 + b5

frontsets_dict = {
    # for the full complement of constraints
    fullset: [f1, f3, f4, f5],
    # for simplified Finnish learning
    Fin: [f3, f5],
    # for simplified N Seto learning
    NSeto: [f4, f5],
    # for simplified S Seto learning
    SSeto: [f1, f3, f4],
    # for simplified N Estonian learning
    NEst: [f3]
}

backsets_dict = {
    # for the full complement of constraints
    fullset: [b1, b2, b3, b5],
    # for simplified Finnish learning
    Fin: [b2, b5],
    # for simplified N Seto learning
    NSeto: [b1, b5],
    # for simplified S Seto learning
    SSeto: [b1, b5],
    # for simplified N Estonian learning
    NEst: [b1, b2]
}

fbsegments = {
    front: frontsegments,
    back: backsegments
}

IdBkSyl1 = "Id(Bk)Syl1"
IdBk = "Id(Bk)"
# IdBkFt1 = "Id(Bk)Ft1"
# AgrBk = "Agr(Bk)"
MaxIOSyl1 = "MaxIOSyl1"
MaxIO = "MaxIO"
MaxIOFSyl1 = "MaxIO(Fr)Syl1"
MaxIOBSyl1 = "MaxIO(Bk)Syl1"
MaxIOF = "MaxIO(Fr)"
MaxIOB = "MaxIO(Bk)"
star_empty = "NonEmpty"
IdHLRSyl1 = "Id(HiLoRd)Syl1"
IdHLR = "Id(HiLoRd)"
IdHiSyl1 = "Id(Hi)Syl1"
IdHi = "Id(Hi)"
IdLoSyl1 = "Id(Lo)Syl1"
IdLo = "Id(Lo)"
IdRdSyl1 = "Id(Rd)Syl1"
IdRd = "Id(Rd)"

ident_cons_general = [IdBk, IdHi, IdLo, IdRd]
ident_cons_syl1 = [IdBkSyl1, IdHiSyl1, IdLoSyl1, IdRdSyl1]
ident_cons_all = ident_cons_syl1 + ident_cons_general

identconstraint_relevantfeature = {
    IdBk: back,
    IdBkSyl1: back,
    IdHi: high,
    IdHiSyl1: high,
    IdLo: low,
    IdLoSyl1: low,
    IdRd: rnd,
    IdRdSyl1: rnd
}


class OTSoftTableauxGenerator:

    # special
    #   = 0 means no special case (previously simple=False)
    #   = 1 means use simplified stringency sets (previously simple=True)
    #   = 2 means use targeted negative evidence for SSeto opacity
    #       (so, eg, the alg knows that Aa->AA, rather than Aa->Aa with a acting as opaque)
    def __init__(self, lang, special=0, bfocus=True, withdeletions=False, deletionbyfeature=False, withnonempty=False, withtranspn=False, groupfeatures=False, countgroupasint=False, withinteractions=False, fortesting=False):
        self.special = special
        self.bfocus = bfocus
        self.lang = lang
        self.withdeletions = withdeletions
        self.deletionbyfeature = deletionbyfeature
        self.withnonempty = withnonempty
        self.withinteractions = withinteractions
        self.withtranspn = withtranspn
        self.groupfeatures = groupfeatures
        self.countgroupasint = countgroupasint
        self.fortesting = fortesting

        self.stringencysets = sets_dict[lang] if special == 1 else sets_dict[fullset]
        self.segM_connames = {setname: "*" + setname for setname in self.stringencysets.keys()}
        self.frontsets = frontsets_dict[lang] if special == 1 else frontsets_dict[fullset]
        self.backsets = backsets_dict[lang] if special == 1 else backsets_dict[fullset]

        self.nodis_connames = [
            nodis_conname(name1, name2, islocal, back if self.bfocus else front)
            for (name1, name2, islocal)
            in product(self.stringencysets.keys(), self.stringencysets.keys(), [True, False])
            if name1[0] != name2[0]
        ]

        self.allcons = [IdBkSyl1, IdBk]
        if self.withdeletions:
            if self.deletionbyfeature:
                self.allcons += [MaxIOFSyl1, MaxIOF, MaxIOBSyl1, MaxIOB]
            else:
                self.allcons += [MaxIOSyl1, MaxIO]
            if self.withnonempty:
                self.allcons += [star_empty]
        if self.withtranspn:
            if self.groupfeatures:
                self.allcons += [IdHLRSyl1, IdHLR]
            elif not self.groupfeatures:
                self.allcons += [IdHiSyl1, IdHi, IdLoSyl1, IdLo, IdRdSyl1, IdRd]
        self.allcons += list(self.segM_connames.values())
        self.allcons += self.nodis_connames

    def nodis_violations(self, constraintname, candidate):
        firstsetname, secondsetname, islocal, underlinedvalue = nodis_conelements(constraintname)
        firstset = self.stringencysets[firstsetname]
        secondset = self.stringencysets[secondsetname]
        numviolations = 0
        candidate = candidate.replace("_", "")  # harmony constraints don't care about deleted segments

        if len(candidate) < 2:
            return 0

        if islocal:
            for idx in range(len(candidate) - 1):
                seg1 = candidate[idx]
                seg2 = candidate[idx + 1]
                if seg1 in firstset and seg2 in secondset:
                    numviolations += 1

        else:  # long-distance  -- remember underline!

            comparisonchecklist = [seg not in fbsegments[underlinedvalue] for seg in candidate]
            checkbefore = (underlinedvalue == back) == ("B" in secondsetname)

            for idx, doneyet in enumerate(comparisonchecklist):
                if not doneyet:
                    if checkbefore:
                        # if any of the preceding segments are in "firstset" and this segment is in "secondset"
                        if candidate[idx] in secondset and has_seg_in_set(candidate[:idx], firstset):
                            numviolations += 1
                    else:  # check after
                        # if any of the following segments are in "secondset" and this segment is in "firstset"
                        if candidate[idx] in firstset and has_seg_in_set(candidate[idx + 1:], secondset):
                            numviolations += 1
        return numviolations

    def segmentalM_violations(self, constraintname, candidate):
        setname = constraintname.replace("*", "")
        setlist = self.stringencysets[setname]
        violns = [int(seg in setlist) for seg in candidate]
        numviolations = sum(violns)
        return numviolations

    def get_numgenidentviolations(self, inputform, candidate):
        genidentcons = [ic for ic in ident_cons_general if ic in self.allcons]
        numviolns = 0
        for ic in genidentcons:
            numviolns += self.get_numviolations(inputform, candidate, ic)
        return numviolns

    def get_numviolations(self, inputform, candidate, constraint):
        if constraint in self.segM_connames.values():
            return self.segmentalM_violations(constraint, candidate)
        # elif constraint in self.bfocus_nodis_connames:
        #     return self.nodis_violations(constraint, candidate)
        # elif constraint in self.ffocus_nodis_connames:
        #     return self.nodis_violations(constraint, candidate)
        elif constraint in self.nodis_connames:
            return self.nodis_violations(constraint, candidate)
        elif constraint in ident_cons_all:
            # compare values of relevant feature for first vowel or all vowels in input form vs candidate
            feature = identconstraint_relevantfeature[constraint]
            indices = [0] if constraint in ident_cons_syl1 else []
            return self.get_identviolations(indices, feature, inputform, candidate)
        elif constraint in [IdHLRSyl1, IdHLR]:
            # compare values of each feature for relevant vowel(s) in input form vs candidate
            ct = 0
            numindicestocompare = 1 if constraint == IdHLRSyl1 else len(inputform)
            for idx in range(0, numindicestocompare):
                numfeaturechangesatthisindex = 0
                for feature in [high, low, rnd]:
                    numfeaturechangesatthisindex += self.get_identviolations([idx], feature, inputform, candidate)
                if self.countgroupasint:
                    ct += numfeaturechangesatthisindex
                elif numfeaturechangesatthisindex > 0:
                    ct += 1
            return ct
        elif constraint in [MaxIO, MaxIOF, MaxIOB, MaxIOSyl1, MaxIOFSyl1, MaxIOBSyl1]:
            posns = [0] if "Syl1" in constraint else []
            feat = back if "Bk" in constraint else (front if "Fr" in constraint else None)
            return self.get_maxviolations(positions=posns, feature=feat, inputform=inputform, candidate=candidate)
        # elif constraint == MaxIOSyl1:
        #     return candidate[:1].count("_")
        # elif constraint == MaxIOFSyl1:
        #     return candidate[:1].count("_") if inputform[0] in frontsegments else 0
        # elif constraint == MaxIOBSyl1:
        #     return candidate[:1].count("_") if inputform[0] in backsegments else 0
        # elif constraint == MaxIO:
        #     return candidate.count("_")
        # elif constraint == MaxIOF:
        #     return candidate.count("_") if inputform[0] in frontsegments else 0
        # elif constraint == MaxIOB:
        #     return candidate.count("_") if inputform[0] in backsegments else 0
        elif constraint == star_empty:
            hascontent = len(candidate.replace("_", "")) > 0
            return int(not hascontent)
        else:
            print("constraint not recognized: " + constraint)
            return -1

    # returns the number of MaxIO violations for the given feature value, at the positions indicated,
    #   in the given input/candidate
    # if feature is None, then just count overall deletions without regard to which feature
    # positions: a list of 0 or more indices at which to compare the given feature value in the input form
    #   vs the candidate; if the list is empty, check *all* indices
    def get_maxviolations(self, positions, feature, inputform, candidate):
        if len(positions) == 0:
            positions = range(0, len(inputform))
        ct = 0
        for idx in positions:
            if feature is None:
                ct += int(candidate[idx] == "_")
            else:
                ct += int(candidate[idx] == "_" and (getbackness(inputform[idx]) == feature))
        return ct

    # returns the number of ident violations for the given feature value, at the positions indicated,
    #   in the given input/candidate
    # positions: a list of 0 or more indices at which to compare the given feature value in the input form
    #   vs the candidate; if the list is empty, check *all* indices
    def get_identviolations(self, positions, feature, inputform, candidate):
        if len(positions) == 0:
            positions = range(0, len(inputform))
        ct = 0
        for idx in positions:
            ct += int(candidate[idx] != "_" and (vowels_features[inputform[idx]][feature] != vowels_features[candidate[idx]][feature]))
        return ct

    def get_allviolations(self, inputform, candidate, constraintset):
        return [self.get_numviolations(inputform, candidate, con) for con in constraintset]

    def generate_tableaux(self, inputs, relativefrequencies=None, foldername=None, customizations=""):
        # with io.open("OTSoft_"+lang+"_GLA_PDDP_nodiacritics.txt", "w", encoding='utf-8') as fGLA:
        #     with io.open("OTSoft_"+lang+"_LFCD_PDDP_nodiacritics.txt", "w", encoding='utf-8') as fLFCD:
        folder_prefix = "" if foldername is None else foldername + customizations + "/"
        # filename_prefix = "OTSoft" + ("_simp" if self.simple else "")
        # if self.withdeletions:
        #     filename_prefix += "_wdel"
        # if self.withtranspn:
        #     if self.groupfeatures:
        #         filename_prefix += "_wft-grp"
        #     elif not self.groupfeatures:
        #         filename_prefix += "_wft-ind"
        # if self.withinteractions:
        #     filename_prefix += "_ixn"
        # filename_prefix += "_" + self.lang
        #
        # filename_suffix = "_PDDP"
        # filename_suffix += "_test" if self.fortesting else ""
        # filename_suffix += ".txt"
        filename_prefix = "OTSoft-PDDP-" + self.lang
        filename_suffix = customizations + ".txt"

        with io.open(folder_prefix + filename_prefix + "_GLA" + filename_suffix, "w", encoding='utf-8') as fGLA:
            with io.open(folder_prefix + filename_prefix + "_LFCD" + filename_suffix, "w", encoding='utf-8') as fLFCD:
                # print("\t\t\t" + "\t".join(self.allcons))
                # print("\t\t\t" + "\t".join(self.allcons))
                fGLA.write("\t\t\t" + "\t".join(self.allcons) + "\n")
                fGLA.write("\t\t\t" + "\t".join(self.allcons) + "\n")
                fLFCD.write("\t\t\t" + "\t".join(self.allcons) + "\n")
                fLFCD.write("\t\t\t" + "\t".join(self.allcons) + "\n")
                ct = 0
                for wd in inputs:
                    # just in case we want to include some targeted negative evidence of non-opacity as input for SSeto
                    usenegativeevidenceforopacity = False
                    if self.special == 2 and self.lang == SSeto:
                        for bigram in [wd[j]+wd[j+1] for j in range(len(wd)-1)]:
                            if bigram in ["Oa", "Ou", "Aa", "Au", "ya", "yu", "ea", "eu"] and not (wd.startswith(e) or wd.startswith(i)):
                                usenegativeevidenceforopacity = True

                    # fb_cands_only = get_frontback_candidates(wd)
                    fb_cands_only = get_modifiedcandidates_wd("fb", wd)

                    # if the modifications are not interacting, we can just concatenate all of the
                    # individually-modified candidate lists (removing duplicates)
                    if not self.withinteractions:
                        # del_cands_only = get_deletion_candidates_wd(wd) if self.withdeletions else []
                        # tr_cands_only = get_transparentization_candidates_wd(wd) if self.withtranspn else []
                        del_cands_only = get_modifiedcandidates_wd("del", wd) if self.withdeletions else []
                        tr_cands_only = get_modifiedcandidates_wd("tr", wd) if self.withtranspn else []
                        listofcandidates = remove_dups(fb_cands_only + del_cands_only + tr_cands_only)
                    # but if the modifications are interacting, then each step must be performed on the previous
                    # modification's list of potential candidates
                    else:
                        # fb_del_cands = get_deletion_candidates_list(fb_cands_only) if self.withdeletions else fb_cands_only
                        # fb_del_tr_cands = get_transparentization_candidates_list(fb_del_cands) if self.withtranspn else fb_del_cands
                        fb_del_cands = get_modifiedcandidates_list("del", fb_cands_only) if self.withdeletions else fb_cands_only
                        fb_del_tr_cands = get_modifiedcandidates_list("tr", fb_del_cands) if self.withtranspn else fb_del_cands
                        listofcandidates = remove_dups(fb_del_tr_cands)

                    # listofcandidates = get_frontback_candidates(wd)
                    # if self.withdeletions and self.withinteractions:
                    #     listofcandidates = get_deletion_candidates_list(listofcandidates)
                    # elif self.withdeletions and not self.withinteractions:
                    #     listofcandidates.extend(get_deletion_candidates_wd(wd))
                    # # if self.withdeletions and not self.withtranspn:
                    # #     listofcandidates.extend(get_deletion_candidates_wd(wd))
                    # # elif self.withtranspn and not self.withdeletions:
                    # #     listofcandidates.extend(get_featurechange_candidates(wd))
                    # # elif self.withdeletions and self.withtranspn:
                    # #     deletion_cands = get_deletion_candidates_wd(wd)
                    onetableau = ""
                    violationprofiles = []
                    hasfaithfulwinner = False
                    for idx, cand in enumerate(listofcandidates):
                        # if wd == "ioE" and self.simple and self.lang == NSeto and cand == "ioE":
                        #     temp = "pause here"
                        violns = [str(violn) for violn in self.get_allviolations(wd, cand, self.allcons)]
                        if violns not in violationprofiles:
                            violationprofiles.append(violns)
                            outstring = wd if idx == 0 else ""
                            outstring += "\t" + cand + "\t"
                            iswinner = isintendedwinner(wd, cand, self.lang)
                            if iswinner and wd == cand:
                                # faithful winner; use in learning (and testing) data
                                outstring += "1\t"
                                ct += 1
                                hasfaithfulwinner = True
                            elif iswinner and (self.fortesting or usenegativeevidenceforopacity):
                                # unfaithful winner; use only in testing data or
                                # if generating some targeted negative inputs for SSeto opacity
                                outstring += "1\t"
                                ct += 1
                            else:
                                # unfaithful winner; do not use in learning data
                                outstring += "\t"
                            outstring += "\t".join(violns)
                            onetableau += outstring + "\n"
                    # onetableau = self.discardlessfaithfulwinners(onetableau)
                    # print(onetableau.strip())
                    if relativefrequencies is not None and wd in relativefrequencies.keys():
                        for numcopies in range(relativefrequencies[wd]):
                            fGLA.write(onetableau)
                    else:
                        # if relativefrequencies is None:
                        #     print("relative frequencies is None")
                        # elif wd not in relativefrequencies.keys():
                        #     print("wd " + wd + " not in relfreqs keys")
                        fGLA.write(onetableau)
                    if hasfaithfulwinner or self.fortesting or usenegativeevidenceforopacity:
                        fLFCD.write(onetableau)
                    for idx1, vp1 in enumerate(violationprofiles):
                        for idx2, vp2 in enumerate(violationprofiles[idx1+1:]):
                            if vp1 == vp2:
                                print("*** input", wd, "in language", self.lang,
                                      "has another candidate with the same violation profile as",
                                      listofcandidates[idx1])

                    # vp_pairs = product(violationprofiles, violationprofiles)
                    # for idx, vp_pair in enumerate(vp_pairs):
                    #     if vp_pair[0] == vp_pair[1]:
                    #         print("*** input", wd, "in language", self.lang, "has at least two candidates with the same violation profile")
                return ct

    def generatetext(self, candidates, foldername=None, customizations=""):
        typeofinputfile = "test" if "test" in customizations else "faithful only"
        print("\n" + typeofinputfile + " (" + self.lang + ") - number of words used: " + str(
            self.generate_tableaux(candidates, foldername=foldername, customizations=customizations)) + " of " + str(
            len(candidates)) + "\n\n")

    def discardlessfaithfulwinners(self, tableaustring):
        tableaumatrix = tomatrix(tableaustring)
        inputform = tableaumatrix[0][0]
        rowlabeledaswinner = [r[2] == '1' for r in tableaumatrix]
        if sum(rowlabeledaswinner) > 1:
            num_genidentviolns = []
            for idx, r in enumerate(tableaumatrix):
                violns = 0 if not rowlabeledaswinner[idx] else self.get_numgenidentviolations(inputform, r[1])
                num_genidentviolns.append(violns)

            minviolns = min([nv for nv in num_genidentviolns if nv > 0])
            for idx, r in enumerate(tableaumatrix):
                if num_genidentviolns[idx] != minviolns:
                    r[2] = ""

        rowstrings = ["\t".join(r) + "\n" for r in tableaumatrix]
        return "".join(rowstrings)


def tomatrix(tableaustring):
    tableaumatrix = []
    tableaurows = tableaustring.strip().split("\n")
    for r in tableaurows:
        cells = r.split("\t")
        tableaumatrix.append(cells)
    return tableaumatrix


# inverse of nodis_conelements
def nodis_conname(firstsetname, secondsetname, islocal, underlinedvalue):
    constraintname = "*" + firstsetname + ("" if islocal else "...") + secondsetname
    if underlinedvalue == front:
        constraintname = constraintname.replace("F", "_F")
    elif underlinedvalue == back:
        constraintname = constraintname.replace("B", "_B")
    return constraintname


# inverse of nodis_conname
def nodis_conelements(constraintname):
    islocal = "..." not in constraintname
    underlinedvalue = front if "_F" in constraintname else back
    constraintname = constraintname.replace("...", "").replace("*", "").replace("_", "")
    firstsetname = constraintname[:2]
    secondsetname = constraintname[2:]
    return firstsetname, secondsetname, islocal, underlinedvalue


def makeinputstrings(segmentsperposition, ucla=False):
    delimiter = "." if ucla else ""
    inputs = [combo for combo in product(*segmentsperposition)]
    inputs = [delimiter.join(combo) for combo in inputs]
    return inputs

#
# def get_featurechange_candidates(wd):
#     return [wd]
#     # if wd == "":
#     #     return [wd]
#     # else:
#     #     candidates = []
#     #     for variant in get_featurechange_candidates(wd[1:]):
#     #         candidates.append(wd[0] + variant)
#     #         candidates.append(TODO + variant)
#     #     return candidates


# def get_deletion_candidates_wd(wd):
#     if wd == "":
#         return [wd]
#     else:
#         candidates = []
#         for variant in get_deletion_candidates_wd(wd[1:]):
#             candidates.append(wd[0] + variant)
#             candidates.append("_" + variant)
#         return candidates


# def get_deletion_candidates_list(existing_candidates):
#     additional_candidates = []
#     for wd in existing_candidates:
#         wd_candidates = get_deletion_candidates_wd(wd)
#         # wd_candidates = [cand for cand in wd_candidates if cand not in all_candidates]
#         additional_candidates.extend(wd_candidates)
#     return remove_dups(existing_candidates + additional_candidates)
#
#
# def get_frontback_candidates(wd):
#     fb_options = tuple([[seg, fbcorrespondents[seg]] for seg in wd])
#     candidates = ["".join(list(p)) for p in product(*fb_options)]
#     return candidates
#
#
# def get_transparentization_candidates_wd(wd):
#     transp_options = tuple([[seg, i, e] for seg in wd])
#     candidates = ["".join(list(p)) for p in product(*transp_options)]
#     return candidates

def get_modifiedcandidates_wd(modtype, wd):
    modified_options = ()
    if modtype == "fb":
        modified_options = tuple([[seg, fbcorrespondents[seg]] for seg in wd])
    elif modtype == "tr":
        modified_options = tuple([[seg, i, e] for seg in wd])
    elif modtype == "del":
        modified_options = tuple([[seg, "_"] for seg in wd])
    candidates = ["".join(list(p)) for p in product(*modified_options)]
    return candidates


def get_modifiedcandidates_list(modtype, existing_candidates):
    additional_candidates = []
    for wd in existing_candidates:
        wd_candidates = get_modifiedcandidates_wd(modtype, wd)
        additional_candidates.extend(wd_candidates)
    return remove_dups(existing_candidates + additional_candidates)


# def get_transparentization_candidates_list(existing_candidates):
#     additional_candidates = []
#     for wd in existing_candidates:
#         wd_candidates = get_transparentization_candidates_wd(wd)
#         # wd_candidates = [cand for cand in wd_candidates if cand not in all_candidates]
#         additional_candidates.extend(wd_candidates)
#     return remove_dups(existing_candidates + additional_candidates)


def getbackness(segment):
    if segment in backsegments:
        return back
    elif segment in frontsegments:
        return front
    else:
        return None


def has_seg_in_set(wd, settocheck):
    occurrences = [s in settocheck for s in wd]
    return True in occurrences


# def firstnonneutral(wd):
#     for segment in wd:
#         if segment != "i":
#             return segment
#     return "i"


def checksetsinpositions(vowelset, position, candidate):
    checkinit = position == initial or position == anywhere
    checknoninit = position == noninitial or position == anywhere
    for idx, v in enumerate(candidate):
        if idx == 0 and checkinit and v in vowelset:
            return True
        elif idx > 0 and checknoninit and v in vowelset:
            return True
    return False


# def iswordinlang(candidate, lang):
#     # TODO need to deal with unfaithful cases in test file!
#
#     if len(candidate) == 0:
#         return True
#
#     elif lang == NEst:
#         # check inventory
#         if checksetsinpositions(b1, anywhere, candidate):
#             return False
#         # check positional restrictions
#         elif checksetsinpositions(b2+f3, noninitial, candidate):
#             # this used to be b3+f3, but I changed it to b2 so that o is allowed to be in non-initial syllables
#             return False
#         else:
#             return True
#
#     elif lang == Fin:
#         # check inventory
#         if checksetsinpositions(b2, anywhere, candidate):
#             return False
#         # make sure we don't have both backs and nonneutral fronts in the same word
#         elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f3, anywhere, candidate):
#             return False
#         else:
#             return True
#
#     elif lang == NSeto:
#         # inventory is unrestricted
#
#         # check positional restrictions
#         if checksetsinpositions(b1, noninitial, candidate):
#             return False
#         # make sure there's no nonneutral fronts and backs in the same word
#         elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f4, anywhere, candidate):
#             return False
#         else:
#             return True
#
#     elif lang == SSeto:
#         # inventory is unrestricted
#
#         # check positional restrictions
#         if checksetsinpositions(b1+f1, noninitial, candidate):
#             return False
#         # if candidate begins with /e/, just check VH for the remainder of the word
#         elif candidate[0] == e:
#             return iswordinlang(candidate[1:], lang)
#         # if candidate contains an (opaque) /o/ somewhere noninitially,
#         # ensure that VH works both before the /o/ and including/after it
#         elif o in candidate[1:]:
#             o_idx = candidate.index(o, 1)
#             return iswordinlang(candidate[:o_idx], lang) and iswordinlang(candidate[o_idx:], lang)
#         # otherwise just make sure there's no nonneutral fronts and backs in the same word
#         elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f4, anywhere, candidate):
#             return False
#         else:
#             return True
#
#     else:
#         print("language " + lang + " not recognized; sorry")
#         sys.exit(1)


def iswordinlang(wd, lang):

    # In case we're looking at a substring of a word in SSeto that either started with /e/ or contained an /o/
    if len(wd) == 0:
        return True

    elif lang == NEst:
        # check inventory
        if checksetsinpositions(b1, anywhere, wd):
            return False
        # check positional restrictions
        elif checksetsinpositions(b2 + f3, noninitial, wd):
            # this used to be b3+f3, but I changed it to b2 so that o is allowed to be in non-initial syllables
            return False
        else:
            return True

    elif lang == Fin:
        # check inventory
        if checksetsinpositions(b2, anywhere, wd):
            return False
        # make sure we don't have both backs and nonneutral fronts in the same word
        elif checksetsinpositions(b5, anywhere, wd) and checksetsinpositions(f3, anywhere, wd):
            return False
        else:
            return True

    elif lang == NSeto:
        # inventory is unrestricted

        # check positional restrictions
        if checksetsinpositions(b1, noninitial, wd):
            return False
        # make sure there's no nonneutral fronts and backs in the same word
        elif checksetsinpositions(b5, anywhere, wd) and checksetsinpositions(f4, anywhere, wd):
            return False
        else:
            return True

    elif lang == SSeto:
        # inventory is unrestricted

        # check positional restrictions
        if checksetsinpositions(b1+f1, noninitial, wd):
            return False
        # if input begins with /e/, ignore it and just check VH for the remainder of the word
        elif wd[0] == e:
            return iswordinlang(wd[1:], lang)
        # if input contains an (opaque) /o/ somewhere noninitially, ensure the candidate does too
        #   and that VH works both before the /o/ and including/after it
        elif o in wd[1:]:
            o_idx = wd.index(o, 1)
            return iswordinlang(wd[:o_idx], lang) and iswordinlang(wd[o_idx:], lang)
        # otherwise just make sure there's no nonneutral fronts and backs in the same word
        elif checksetsinpositions(b5, anywhere, wd) and checksetsinpositions(f4, anywhere, wd):
            return False
        else:
            return True


def isintendedwinner(inputform, candidate, lang):
    if lang not in langnames:
        print("language " + lang + " not recognized; sorry")
        sys.exit(1)

    # If the input was grammatical to begin with, then the matching candidate should be the winner.
    if iswordinlang(inputform, lang):
        return inputform == candidate

    # If not, however, then it should be the one where:
    #   (a) the initial vowel has changed backness to avoid banned vowels, and
    #   (b) noninitial vowels have changed backness to meet
    #       (i) positional restriction requirements and
    #       (ii) vowel harmony requirements set by the initial/preceding vowel

    # in this world deletion is not used as a solution to disharmony,
    # so the candidate must have the same number of segments as the input
    if len(inputform) != len(candidate.replace("_", "")):
        return False
    # nor is transparentization used as a solution to disharmony,
    # so the candidate must not have changed any segments to /i/ or /e/ unless they were
    # /I/ or /E/ to begin with, respectively
    for idx in range(len(inputform)):
        if candidate[idx] == i and inputform[idx] not in [i, I]:
            return False
        elif candidate[idx] == e and inputform[idx] not in [e, E]:
            return False

    # In case we're looking at the "rest" of a word in SSeto that started with /e/
    if len(inputform) == 0:
        return True

    # check first-syllable faithfulness
    elif (lang == NEst and (inputform[0] not in b1 and inputform[0] != candidate[0])) \
            or (lang == Fin and (inputform[0] not in b2 and inputform[0] != candidate[0])) \
            or (lang == NSeto and (inputform[0] != candidate[0])) \
            or (lang == SSeto and (inputform[0] != candidate[0])):
        return False

    # check inventory, positional restrictions, and/or harmony
    elif not iswordinlang(candidate, lang):
        return False

    # elif iswordinlang and isintendedwinner(*removeinitialtransparentV(inputform, candidate, lang)):
    #     # this word is grammatical, but it's not the best choice (because after an initial transparent vowel,
    #     #   there's another vowel that's unfaithful and doesn't need to be)
    #     return False

    else:
        return True


# def removeinitialtransparentV(inputform, candidate, lang):
#     return inputform, candidate, lang
#
#     if lang == NEst:
#         # harmony / transparency are not applicable
#         return inputform, candidate, lang
#     if istransparent(candidate[0], lang)(lang == Fin and candidate[0] in [i, e]:
#         return inputform[1:], candidate[1:], lang
#     elif lang == NEst and candidate[0] in [i]:
#         return
#
#
# def istransparent(segment, lang):
#
#     return ((lang == Fin and segment in [i, e]) or
#             (lang == NSeto and segment in [i]) or
#             (lang == SSeto and segment in [i]))


    # elif lang == NEst:
    #     # check first-syllable faithfulness
    #     if inputform[0] not in b1 and inputform[0] != candidate[0]:
    #         return False
    #     # check inventory, positional restrictions, and/or harmony
    #     elif not isgrammatical(candidate, lang):
    #         return False
    #     # check inventory
    #     # elif checksetsinpositions(b1, anywhere, candidate):
    #     #     return False
    #     # # check positional restrictions
    #     # elif checksetsinpositions(b2 + f3, noninitial, candidate):
    #     #     # this used to be b3+f3, but I changed it to b2 so that o is allowed to be in non-initial syllables
    #     #     return False
    #     else:
    #         return True
    #
    # elif lang == Fin:
    #     # check first-syllable faithfulness
    #     if inputform[0] not in b2 and inputform[0] != candidate[0]:
    #         return False
    #     # check inventory, positional restrictions, and/or harmony
    #     elif not isgrammatical(candidate, lang):
    #         return False
    #     # # check inventory
    #     # if checksetsinpositions(b2, anywhere, candidate):
    #     #     return False
    #     # # make sure we don't have both backs and nonneutral fronts in the same word
    #     # elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f3, anywhere, candidate):
    #     #     return False
    #     else:
    #         return True
    #
    # elif lang == NSeto:
    #     # check first-syllable faithfulness
    #     if inputform[0] != candidate[0]:
    #         return False
    #     # check inventory, positional restrictions, and/or harmony
    #     elif not isgrammatical(candidate, lang):
    #         return False
    #
    #     # # inventory is unrestricted
    #     #
    #     # # check positional restrictions
    #     # if checksetsinpositions(b1, noninitial, candidate):
    #     #     return False
    #     # # make sure there's no nonneutral fronts and backs in the same word
    #     # elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f4, anywhere, candidate):
    #     #     return False
    #     else:
    #         return True
    #
    # elif lang == SSeto:
    #     # check first-syllable faithfulness
    #     if inputform[0] != candidate[0]:
    #         return False
    #     # check inventory, positional restrictions, and/or harmony
    #     elif not isgrammatical(candidate, lang):
    #         return False
    #
    #     # # inventory is unrestricted
    #     #
    #     # # check positional restrictions
    #     # if checksetsinpositions(b1+f1, noninitial, candidate):
    #     #     return False
    #     # # if input begins with /e/, we already know the candidate does too
    #     # #   so just check "initial" faith and VH for the remainder of the word
    #     # elif inputform[0] == e:
    #     #     return isintendedwinner(inputform[1:], candidate[1:], lang)
    #     # # if input contains an (opaque) /o/ somewhere noninitially, ensure the candidate does too
    #     # #   and that VH works both before the /o/ and including/after it
    #     # elif o in inputform[1:]:
    #     #     o_idx = inputform.index(o, 1)
    #     #     return isintendedwinner(inputform[:o_idx], candidate[:o_idx], lang) \
    #     #         and isintendedwinner(inputform[o_idx:], candidate[o_idx:], lang)
    #     # # otherwise just make sure there's no nonneutral fronts and backs in the same word
    #     # elif checksetsinpositions(b5, anywhere, candidate) and checksetsinpositions(f4, anywhere, candidate):
    #     #     return False
    #     else:
    #         return True
    #
    # else:
    #     print("language " + lang + " not recognized; sorry")
    #     sys.exit(1)


#
# if __name__ == "__main__":
#     cands = get_frontback_candidates("ayi")
#     print("candidates for", "ayi", ":", cands)
#
#     print("violations of", "*_B5F5", ":", [cand + " " + str(get_numviolations("", cand, "*_B5F5")) for cand in cands])
#     print("violations of", "*_B3F5", ":", [cand + " " + str(get_numviolations("", cand, "*_B3F5")) for cand in cands])
#     print("violations of", "*B5..._F5", ":", [cand + " " + str(get_numviolations("", cand, "*B5..._F5")) for cand in cands])
#     print("violations of", "*_B5...F5", ":", [cand + " " + str(get_numviolations("", cand, "*_B5...F5")) for cand in cands])
#
#     print("violations of", "*F3", ":", [cand + " " + str(get_numviolations("", cand, "*F3")) for cand in cands])
#     print("violations of", "*B2", ":", [cand + " " + str(get_numviolations("", cand, "*B2")) for cand in cands])
#
#     print("violations of", IdBkSyl1, "with input", "ayi", ":", [cand + " " + str(get_numviolations("ayi", cand, IdBkSyl1)) for cand in cands])
#     print("violations of", IdBk, "with input", "ayi", ":", [cand + " " + str(get_numviolations("ayi", cand, IdBk)) for cand in cands])
#
#     print("\nwhich candidate is the intended winner in each language, for input", "ayɨ", "?")
#     for lang in [NEst, Fin, NSeto, SSeto]:
#         print(lang)
#         print([cand + " " + str(isintendedwinner("ayi", cand, lang)) for cand in cands])


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


def separate_characters(wd):
    segments = wd.split(".")
    spaced_word = " ".join(segments)
    return spaced_word


def remove_dups(wordlist):
    return list(dict.fromkeys(wordlist))


class UCLAPLGenerator:

    def __init__(self, lang):  # , simple=False):
        # self.simple = simple
        self.lang = lang

    def generate_inputsandtests(self, wordlist, maxlength, foldername=None):
        learningwords = []
        testingwords = []
        lwords_spaced = []
        twords_spaced = []

        for wd in wordlist:
            testingwords.append(wd)

            if iswordinlang(wd.split("."), self.lang):
                learningwords.append(wd)
                lwords_spaced.append(separate_characters(wd))
                twords_spaced.append(separate_characters(wd) + "\t" + "word")
            else:
                twords_spaced.append(separate_characters(wd) + "\t" + "nonword")

        folder_prefix = "" if foldername is None else foldername + "/"
        with io.open(folder_prefix + "UCLAPL_" + self.lang + "_PDDP_maxlen" + str(maxlength) + "_LearningData.txt", "w", encoding='utf-8') as learnfile:
            with io.open(folder_prefix + "UCLAPL_" + self.lang + "_PDDP_maxlen" + str(maxlength) + "_TestingData.txt", "w", encoding='utf-8') as testfile:

                for tword in twords_spaced:
                    testfile.write(tword + "\n")

                multiplier = math.ceil(3000/len(lwords_spaced))
                for lap in range(multiplier):
                    for lword in lwords_spaced:
                        learnfile.write(lword + "\n")

        print("Learning Data for " + self.lang + ":", learningwords)
        print("Testing Data for " + self.lang + ":", testingwords)
        print("---------------------------------------------")


# generatetext(length2words+length3words+somelongerwords, removeGMHcons, KE)
# generatetext(length2words+length3words+somelongerwords, removeGMHcons, SE)
# generatetext(length2words+length3words+somelongerwords, stringencycons1, KE)
# generatetext(length2words+length3words+somelongerwords, stringencycons1, SE)
# generatetext(length2words+length3words+somelongerwords, stringencycons2, KE)
# generatetext(length2words+length3words+somelongerwords, stringencycons2, SE)
# generatetext(length2words+length3words, allcons_bfocus, NEst)
# generatetext(length2words+length3words, allcons_bfocus, Fin)
# generatetext(length2words+length3words, allcons_bfocus, NSeto)
# generatetext(length2words+length3words, allcons_bfocus, SSeto)

# words_from_OTSoft_experiments = ["iõ", "ie", "iB", "iF", "õi", "ei", "Bi", "Fi", "BB", "BF", "FB", "FF",
#                                  "FBB", "õõ", "õe", "eõ", "ee", "eõõ", "Bõ", "Be", "Fõ", "Fe", "FBõ", "Fõõ",
#                                  "õB", "õF", "eF", "eB", "eõB", "eBB", "BiB", "BiF", "FiF", "FiB",
#                                  "õiõ", "õie", "eie", "eiõ", "Biõ", "Bie", "Fiõ", "Fie",
#                                  "õiB", "õiF", "eiF", "eiB", "FiBiF", "FiBiB", "õee"
#                                  ]


# SPECIALin
#   = 0 means no special case (previously SIMPin=False)
#   = 1 means use simplified stringency sets (previously SIMPin=True)
#   = 2 means use targeted negative evidence for SSeto opacity
#       (so, eg, the alg knows that Aa->AA, rather than Aa->Aa with a acting as opaque)
def main_helper(SPECIALin, DELin, DELFTin, NEMPin, TRANSPin, FTGRPin, GRPINTin, IXNin, TESTin):

    uclayes_otsoftno = False  # True for generating UCLA-PL input files; False for OTSoft

    length1words = makeinputstrings([allsegments], ucla=uclayes_otsoftno)
    length2words = makeinputstrings([allsegments, allsegments], ucla=uclayes_otsoftno)
    length3words = makeinputstrings([allsegments, allsegments, allsegments], ucla=uclayes_otsoftno)
    length4words = makeinputstrings([allsegments, allsegments, allsegments, allsegments], ucla=uclayes_otsoftno)
    length5words = makeinputstrings([allsegments, allsegments, allsegments, allsegments, allsegments], ucla=uclayes_otsoftno)
    # somelongerwords = ["iieB", "iiFõ", "iiiBe", "iiiiõF", "iiiiõ"]

    if not uclayes_otsoftno:  # OTSoft
        customizations = ""
        customizations += "_simp" if SPECIALin == 1 else ("_neg" if SPECIALin == 2 else "")
        if DELin:
            customizations += "_wdel" + ("-wft" if DELFTin else "-gen") + ("-ne" if NEMPin else "")
        # customizations += "_wdel" if DELin else ""
        if TRANSPin:
            customizations += "_wtr" + (("-grp" + ("-int" if GRPINTin else "-tf")) if FTGRPin else "-ind")
        customizations += "_ixn" if IXNin else ""
        customizations += "_test" if TESTin else ""
        foldername = datetime.now().strftime('%Y%m%d.%H%M%S') + '_forOTS'  # '-OTSoft-files'
        os.mkdir(foldername+customizations)
        for langname in [SSeto, NEst]:  # langnames:
            tableaux_generator = OTSoftTableauxGenerator(langname, special=SPECIALin, bfocus=True, withdeletions=DELin,
                                                         deletionbyfeature=DELFTin, withnonempty=NEMPin,
                                                         withtranspn=TRANSPin, groupfeatures=FTGRPin, countgroupasint=GRPINTin,
                                                         withinteractions=IXNin, fortesting=TESTin)
            tableaux_generator.generatetext(length2words + length3words, foldername=foldername, customizations=customizations)

    if uclayes_otsoftno:  # UCLA
        foldername = datetime.now().strftime('%Y%m%d.%H%M%S') + '-OTSoft-files'
        os.mkdir(foldername)
        for langname in langnames:
            inputandtest_generator = UCLAPLGenerator(langname)  # , simple=False)
            lengthupto = 5
            wordlists = [length1words, length2words, length3words, length4words, length5words]
            allwords = []
            for i in range(lengthupto):
                allwords.extend(wordlists[i])
            inputandtest_generator.generate_inputsandtests(allwords, lengthupto, foldername=foldername)


if __name__ == "__main__":
    ft = [False, True]

    # generate inputs for all languages, under all combinations of arguments as of 20231005
    if True:
        counter = 1
        for DEL in ft:
            deletebyfeature = [False]
            includenonemptyMconstraint = [False]
            if DEL:
                deletebyfeature += [True]
                includenonemptyMconstraint += [True]
            for DELFT in deletebyfeature:
                for NONEMPTY in includenonemptyMconstraint:
                    for TRANSP in [False]:  # ft:
                        groupfeaturesoptions = [False]
                        if TRANSP:
                            groupfeaturesoptions += [True]
                        for FTGRP in groupfeaturesoptions:
                            countgroupasintoptions = [False]
                            if FTGRP:
                                countgroupasintoptions += [True]
                            for GRPINT in countgroupasintoptions:
                                interactionoptions = [False]
                                if DEL or TRANSP:
                                    interactionoptions = [True]  # += [True]
                                for IXN in interactionoptions:
                                    for TEST in ft:
                                        print("iteration", counter)
                                        counter += 1
                                        # if TRANSP and FTGRP: ###############################
                                        main_helper(SPECIALin=2, DELin=DEL, DELFTin=DELFT, NEMPin=NONEMPTY, TRANSPin=TRANSP, FTGRPin=FTGRP, GRPINTin=GRPINT, IXNin=IXN, TESTin=TEST)

    elif False:
        counter = 1
        DEL = True
        DELFT = False
        NONEMPTY = True
        TRANSP = False
        FTGRP = False
        GRPINT = False
        IXN = True
        for TEST in ft:
            print("iteration", counter, "of 2")
            counter += 1
            main_helper(SPECIALin=0, DELin=DEL, DELFTin=DELFT, NEMPin=NONEMPTY, TRANSPin=TRANSP, FTGRPin=FTGRP, GRPINTin=GRPINT, IXNin=IXN, TESTin=TEST)

    # generate inputs for all languages but for only one specific combination of arguments
    else:
        main_helper(SPECIALin=0, DELin=False, DELFTin=False, NEMPin=False, TRANSPin=False, FTGRPin=False, GRPINTin=False, IXNin=False, TESTin=True)


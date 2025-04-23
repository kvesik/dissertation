from itertools import product
import io
import pandas as pd
import sys
import os
import math
import re
from datetime import datetime

# heavy = "H"
# light = "L"

# Tesar & Smolensky set
# notes from Apoussidou & Boersma 2004
# Comparing Different Optimality-Theoretic Learning Algorithms: The Case of Metrical Phonology
###########################################
# The alignment constraints AFL and AFR make sure that a foot is aligned with one of the edges of a word.
# Their violation is gradient: AFL is assigned one violation mark for every syllable between the left edge
# of the word and the left edge of every foot. In the candidate surface form /L (L2 L) (L1 L)/, where ‘2’
# stands for secondary stress, AFL is violated four times: once for the first foot, three times for the second foot.
AFL = "AFL"  # align each foot with the word, left edge
AFR = "AFR"  # align each foot with the word, right edge
# The constraints MAIN-L and MAIN-R do the same as AFL and AFR, but only for the foot that contains the main
# stress. Thus, the candidate /L (L2 L) (L1 L)/ violates MAIN-L three times, and MAIN-R not at all.
MainLeft = "Main-L"  # align the head foot with the word, left edge
MainRight = "Main-R"  # align the head foot with the word, right edge
# The two WORD-FOOT alignment constraints favour candidates where at least one foot is aligned with the word edge.
# These constraints are not gradient, but binary: they are assigned a single violation mark if there is an unfooted
# syllable at the edge of the word. Thus, the candidate /L L (L1) (L2 L)/ violates WFL (once), but not WFR.
WFL = "WFL"  # align the word with some foot, left edge
WFR = "WFR"  # align the word with some foot, right edge
# The constraint NONFINAL expresses extrametricality: it is violated if the last syllable is parsed (included) in a foot.
# This constraint thus prefers /(L1) L/ to /(L1 L)/.
NonFinal = "NonFinal"  # do not foot the final syllable of the word
# The constraint PARSE favours candidates in which all syllables are parsed into feet. It is assigned one violation
# mark for each unfooted syllable. Thus, the candidate /L (L1 L) L L/ violates PARSE three times.
Parse = "Parse"  # each syllable must be footed
# The constraint FtNonFinal favours candidates with trochaic (initially stressed) feet like (L1 L), (L2 L), (L1 H),
# and so on. However, degenerate feet consisting of only one syllable, like (L1) and (H2), violate this constraint.
FtNonFinal = "FtNonFinal"  # each head syllable must not be final in its foot
# The constraint IAMBIC favours candidates with iambic (finally stressed) feet like (L L1), and this constraint is not
# violated in degenerate feet like (L1).
Iambic = "Iambic"  # The rightmost syllable in a foot is the head syllable (Apoussidou 2007 diss)
# The WEIGHT-TO-STRESS-PRINCIPLE favours candidates that have stress on a heavy syllable. Every unstressed heavy
# syllable causes a violation. Thus, /(L2 H) H (H1) L/ violates WSP twice (once for the unfooted H, once for the
# H in the first foot’s weak position), whereas /(L H2) (H2) (H1) L/ does not violate WSP.
WSP = "WSP"  # each heavy syllable must be stressed
# FtBin is the constraint for foot size: feet should be binary regarding either syllables or moras; a light syllable
# counts as one mora, a heavy syllable as two. In the candidate set under discussion here, this constraint is only
# assigned a violation mark for each monosyllabic light foot, i.e. (L1) and (L2), whereas feet like (L1 H) and (H H2) do
# not violate this constraint (remember that candidates with more than two syllables are not generated).
FtBin = "FtBin"  # each foot must be either bimoraic or bisyllabic
# additional / alternative constraints for Jacobs set and Prince & Smolensky set
Trochaic = "Trochaic"  # The leftmost syllable in a foot is the head syllable (Apoussidou 2007 diss)
HeadNonFinal = "HeadNonFinal"  # The head foot is not aligned with the right edge of the word, and the head syllable is not the last syllable in the word. (Apoussidou 2007 diss)
# Apoussidou 2007 (diss): "A mora is a smaller unit than a syllable, and determines the weight of the syllable:
# syllables with a long vowel or a diphthong contain two moras (they are heavy), while syllables with only a short
# vowel contain only one mora (they are light). ...  In quantity-sensitive languages a foot ideally consists of two
# moras: either two light syllables or one heavy syllable."
FtBimoraic = "FtBimoraic"  # Each foot must be bimoraic (Apoussidou 2007 diss)

# TODO is WFR a subset of Main-R, which is a subset of AFR? And same for L?

# Tesar & Smolensky (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
t_s_cons = "t_s_cons"
# Jacobs (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
j_cons = "j_cons"
# Prince & Smolensky (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
p_s_cons = "p_s_cons"
# ... and the augmented version of each, with FtBimoraic (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
t_s_cons_aug = "t_s_cons_aug"
j_cons_aug = "j_cons_aug"
p_s_cons_aug = "p_s_cons_aug"

constraint_sets = {
    # Tesar & Smolensky (as per Apoussidou & Boersma 2003: The learnability of Latin stress, and Jarosz 2016)
    t_s_cons: [AFL, AFR, MainLeft, MainRight, WFL, WFR, NonFinal, Parse, FtNonFinal, Iambic, WSP, FtBin],
    # Jacobs (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
    # "uneven-trochee" constraint set
    j_cons: [AFL, AFR, MainLeft, MainRight, WFL, WFR, NonFinal, Parse, Trochaic, Iambic, WSP, FtBin],
    # Prince & Smolensky (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
    # "moraic-trochee" cosntraint set
    p_s_cons: [AFL, AFR, MainLeft, MainRight, WFL, WFR, HeadNonFinal, Parse, Trochaic, Iambic, WSP, FtBin],
    # ... and the augmented version of each, with FtBimoraic (as per Apoussidou & Boersma 2003: The learnability of Latin stress)
    t_s_cons_aug: [AFL, AFR, MainLeft, MainRight, WFL, WFR, NonFinal, Parse, FtNonFinal, Iambic, WSP, FtBin, FtBimoraic],
    j_cons_aug: [AFL, AFR, MainLeft, MainRight, WFL, WFR, NonFinal, Parse, Trochaic, Iambic, WSP, FtBin, FtBimoraic],
    p_s_cons_aug: [AFL, AFR, MainLeft, MainRight, WFL, WFR, HeadNonFinal, Parse, Trochaic, Iambic, WSP, FtBin, FtBimoraic]
}

overt_forms = {
    "latin_main": [
        "L1 L",
        "L1 H",
        "H1 L",
        "H1 H",
        "L1 L L",
        "L1 L H",
        "L H1 L",
        "L H1 H",
        "H1 L L",
        "H1 L H",
        "H H1 L",
        "H H1 H",
        "L L1 L L",
        "L L1 L H",
        "L L H1 L",
        "L L H1 H",
        "L H1 L L",
        "L H1 L H",
        "L H H1 L",
        "L H H1 H",
        "H L1 L L",
        "H L1 L H",
        "H L H1 L",
        "H L H1 H",
        "H H1 L L",
        "H H1 L H",
        "H H H1 L",
        "H H H1 H"
    ],
    "latin_secondary": [
        "L1 L",
        "L1 H",
        "H1 L",
        "H1 H",
        "L1 L L",
        "L1 L H",
        "L H1 L",
        "L H1 H",
        "H1 L L",
        "H1 L H",
        "H2 H1 L",
        "H2 H1 H",
        "L L1 L L",
        "L L1 L H",
        "L2 L H1 L",
        "L2 L H1 H",
        "L H1 L L",
        "L H1 L H",
        "L H2 H1 L",
        "L H2 H1 H",
        "H2 L1 L L",
        "H2 L1 L H",
        "H2 L H1 L",
        "H2 L H1 H",
        "H2 H1 L L",
        "H2 H1 L H",
        "H2 H2 H1 L",
        "H2 H2 H1 H"
    ],
}


class OTSoftTableauxGenerator:

    def __init__(self, langname, consetname, fortesting=False):
        self.lang = langname
        self.constraintsetname = consetname
        self.allcons = constraint_sets[consetname]
        self.fortesting = fortesting

    # The alignment constraints AFL and AFR make sure that a foot is aligned with one of the edges of a word.
    # Their violation is gradient: AFL is assigned one violation mark for every syllable between the left edge
    # of the word and the left edge of every foot. In the candidate surface form /L (L2 L) (L1 L)/, where ‘2’
    # stands for secondary stress, AFL is violated four times: once for the first foot, three times for the second foot.
    def AF_violations(self, candidate, constraint):
        if constraint == AFL:
            bracket = "("
            # candidate stays as is
        elif constraint == AFR:
            bracket = ")"
            candidate = candidate[::-1]

        num_violns = 0
        syls_seen = 0

        for char in candidate:
            if char == bracket:
                # how many syllables have we seen so far?
                num_violns += syls_seen
            elif char in ["H", "L"]:
                # add a syllable to the count
                syls_seen += 1
        return num_violns

    # The constraints MAIN-L and MAIN-R do the same as AFL and AFR, but only for the foot that contains the main
    # stress. Thus, the candidate /L (L2 L) (L1 L)/ violates MAIN-L three times, and MAIN-R not at all.
    def Main_violations(self, candidate, constraint):
        # find where main stress is
        main_idx = candidate.find("1")
        if main_idx < 0:
            return 0
        else:
            # take the substring of the candidate only on the [direction] side of the foot with main stress
            if constraint == MainLeft:
                candidate_substring = candidate[:main_idx]
                # find last instance of (
                m = re.search('\(', candidate_substring)
                openbracket_idx = m.end()
                candidate_substring = candidate_substring[:openbracket_idx]
            elif constraint == MainRight:
                candidate_substring = candidate[main_idx:]
                # find first instance of )
                closebracket_idx = candidate_substring.index(")")
                candidate_substring = candidate_substring[closebracket_idx:]

            # count how many syllables are in that substring and return that as the number of violations
            return candidate_substring.count("L") + candidate_substring.count("H")

    # The two WORD-FOOT alignment constraints favour candidates where at least one foot is aligned with the word edge.
    # These constraints are not gradient, but binary: they are assigned a single violation mark if there is an unfooted
    # syllable at the edge of the word. Thus, the candidate /L L (L1) (L2 L)/ violates WFL (once), but not WFR.
    def WF_violations(self, candidate, constraint):
        if constraint == WFL:
            return int(not candidate.startswith("("))
        elif constraint == WFR:
            return int(not candidate.endswith(")"))

    # The constraint NONFINAL expresses extrametricality: it is violated if the last syllable is parsed (included) in a foot.
    # This constraint thus prefers /(L1) L/ to /(L1 L)/.
    def NonFinal_violations(self, candidate):
        return int(candidate.endswith(")"))

    # The constraint PARSE favours candidates in which all syllables are parsed into feet. It is assigned one violation
    # mark for each unfooted syllable. Thus, the candidate /L (L1 L) L L/ violates PARSE three times.
    def Parse_violations(self, candidate):
        num_violns = 0
        currently_in_a_foot = False

        for char in candidate:
            if char == "(":
                currently_in_a_foot = True
            elif char == ")":
                currently_in_a_foot = False
            elif (not currently_in_a_foot) and (char in ["H", "L"]):
                num_violns += 1

        return num_violns

    # The constraint FtNonFinal favours candidates with trochaic (initially stressed) feet like (L1 L), (L2 L), (L1 H),
    # and so on. However, degenerate feet consisting of only one syllable, like (L1) and (H2), violate this constraint.
    def FtNonFinal_violations(self, candidate):
        # count the number of instances of digit-closebracket bigrams, eg "1)" or "2)"
        return len(re.findall('\d\)', candidate))

    # The constraint IAMBIC favours candidates with iambic (finally stressed) feet like (L L1), and this constraint is not
    # violated in degenerate feet like (L1).
    def Iambic_violations(self, candidate):
        # count the number of digits that are not immediately followed by close-brackets ")"
        return len(re.findall('\d[^\)]', candidate))

    # The WEIGHT-TO-STRESS-PRINCIPLE favours candidates that have stress on a heavy syllable. Every unstressed heavy
    # syllable causes a violation. Thus, /(L2 H) H (H1) L/ violates WSP twice (once for the unfooted H, once for the
    # H in the first foot’s weak position), whereas /(L H2) (H2) (H1) L/ does not violate WSP.
    def WSP_violations(self, candidate):
        # count the number of instances of H that aren't immediately followed by a digit (including at the end of the string)
        return len(re.findall('H[^\d]', candidate)) + len(re.findall('H$', candidate))

    # FtBin is the constraint for foot size: feet should be binary regarding either syllables or moras; a light syllable
    # counts as one mora, a heavy syllable as two. In the candidate set under discussion here, this constraint is only
    # assigned a violation mark for each monosyllabic light foot, i.e. (L1) and (L2), whereas feet like (L1 H) and (H H2) do
    # not violate this constraint (remember that candidates with more than two syllables are not generated).
    def FtBin_violations(self, candidate):
        # count the number of instances of (L), (L1), and (L2)
        candidate = removestresses(candidate)
        return candidate.count("(L)")

    def Trochaic_violations(self, candidate):
        # count the number of instances of <openbracket><H or L><not a digit> trigrams, eg "(H L1)" or "(L)" or "(L H)"
        return len(re.findall('\([HL][^\d]', candidate))

    # The head foot is not aligned with the right edge of the word, and the head syllable is not the last syllable in the word.
    # HEADNONFINAL demands that neither the head syllable of a foot nor the head foot itself are in wordfinal
    # position. Both of these conditions can assign a violation mark:
    # HEADNONFINAL is violated once in the form /(H2)(L1 L)/, twice in /(H2)(L L1)/, and not at all in /(H1)(L L2)/.
    def HeadNonFinal_violations(self, candidate):
        ct = 0
        if candidate.endswith('1)'):
            # the head syllable AND the head foot are in word-final position
            ct += 2
        elif re.findall('1 [HL]\)$', candidate):
            # the head foot is final (but not the head syllable)
            ct += 1
        return ct

    # Apoussidou 2007 (diss): "A mora is a smaller unit than a syllable, and determines the weight of the syllable:
    # syllables with a long vowel or a diphthong contain two moras (they are heavy), while syllables with only a short
    # vowel contain only one mora (they are light). ...  In quantity-sensitive languages a foot ideally consists of two
    # moras: either two light syllables or one heavy syllable."
    # Each foot must be bimoraic (Apoussidou 2007 diss)
    def FtBimoraic_violations(self, candidate):
        # feet that satisfy FtBimoraic: (H), (L L)
        # feet that violate FtBimoraic: (H L), (L H), (H H), (L)
        candidate = removestresses(candidate)
        ct = len(re.findall('\(H L\)', candidate))
        ct += len(re.findall('\(L H\)', candidate))
        ct += len(re.findall('\(H H\)', candidate))
        ct += len(re.findall('\(L\)', candidate))
        return ct

    def get_numviolations(self, inputform, candidate, constraint):
        if constraint in [AFR, AFL]:
            return self.AF_violations(candidate, constraint)
        elif constraint in [MainRight, MainLeft]:
            return self.Main_violations(candidate, constraint)
        elif constraint in [WFL, WFR]:
            return self.WF_violations(candidate, constraint)
        elif constraint == NonFinal:
            return self.NonFinal_violations(candidate)
        elif constraint == Parse:
            return self.Parse_violations(candidate)
        elif constraint == FtNonFinal:
            return self.FtNonFinal_violations(candidate)
        elif constraint == Iambic:
            return self.Iambic_violations(candidate)
        elif constraint == WSP:
            return self.WSP_violations(candidate)
        elif constraint == FtBin:
            return self.FtBin_violations(candidate)
        elif constraint == Trochaic:
            return self.Trochaic_violations(candidate)
        elif constraint == HeadNonFinal:
            return self.HeadNonFinal_violations(candidate)
        elif constraint == FtBimoraic:
            return self.FtBimoraic_violations(candidate)
        else:
            print("constraint not recognized: " + constraint)
            return -1

    def get_allviolations(self, inputform, candidate, constraintset):
        return [self.get_numviolations(inputform, candidate, con) for con in constraintset]

    def generate_tableaux(self, overtforms, foldername=None, customizations=""):
        folder_prefix = "" if foldername is None else foldername + customizations + "/"
        filename_prefix = "OTSoft-" + self.constraintsetname + "-" + self.lang
        filename_suffix = customizations + ".txt"

        with io.open(folder_prefix + filename_prefix + "_GLA" + filename_suffix, "w", encoding='utf-8') as fGLA:
            # with io.open(folder_prefix + filename_prefix + "_LFCD" + filename_suffix, "w", encoding='utf-8') as fLFCD:
            fGLA.write("\t\t\t" + "\t".join(self.allcons) + "\n")
            fGLA.write("\t\t\t" + "\t".join(self.allcons) + "\n")
            # fLFCD.write("\t\t\t" + "\t".join(self.allcons) + "\n")
            # fLFCD.write("\t\t\t" + "\t".join(self.allcons) + "\n")
            ct = 0
            for overtform in overtforms:
                ur = removestresses(overtform)
                # listofcandidates = [overtform] + get_candidates(ur)  # OLD
                listofcandidates = remove_dups(get_candidates(ur, mainonly=("main" in self.lang)))

                onetableau = ""
                violationprofiles = []
                for idx, cand in enumerate(listofcandidates):
                    violns = [str(violn) for violn in self.get_allviolations(ur, cand, self.allcons)]
                    if violns not in violationprofiles:
                        violationprofiles.append(violns)
                        outstring = overtform if idx == 0 else ""
                        outstring += "\t" + cand + "\t"
                        isacceptablewinner = (removeparens(overtform) == removeparens(cand))  # False  # OLD idx == 0  # the first "candidate" will always be the overt form
                        if isacceptablewinner:
                            # matches the overt form's stress placement
                            outstring += "1\t"
                            ct += 1
                        else:
                            # does not match the overt form
                            outstring += "\t"
                        outstring += "\t".join(violns)
                        onetableau += outstring + "\n"
                fGLA.write(onetableau)
                for idx1, vp1 in enumerate(violationprofiles):
                    for idx2, vp2 in enumerate(violationprofiles[idx1+1:]):
                        if vp1 == vp2:
                            print("*** input", overtform, "in language", self.lang,
                                  "has another candidate with the same violation profile as",
                                  listofcandidates[idx1])

            return ct

    def generatetext(self, overtforms, foldername=None, customizations=""):
        typeofinputfile = "test" if "test" in customizations else "faithful only"
        print("\n" + typeofinputfile + " (" + self.lang + ") - number of words used: " + str(
            self.generate_tableaux(overtforms, foldername=foldername, customizations=customizations)) + " of " + str(
            len(overtforms)) + "\n\n")


def tomatrix(tableaustring):
    tableaumatrix = []
    tableaurows = tableaustring.strip().split("\n")
    for r in tableaurows:
        cells = r.split("\t")
        tableaumatrix.append(cells)
    return tableaumatrix


# space-separated strings representing all combinations of H and L, for sequences of given length
# eg: "H L", "L L H", "H L H H", etc
def makeinputstrings(stringlength):
    URs = []
    for n in range(2, 6):
        for combo in product(*tuple([["H", "L"]]*n)):
            URs.append(" ".join(list(combo)))
    return URs


def get_footings(word, justone=False):
    syllables_list = word.strip().split(" ")
    if justone:
        monosyllabic_options = []
        bisyllabic_options = []
        for idx, syl in enumerate(syllables_list):
            monosyllabic_options.append(" ".join(syllables_list[:idx] + ["(" + syl + ")"] + syllables_list[idx+1:]))
            if idx + 1 < len(syllables_list):
                bisyllabic_options.append(" ".join(syllables_list[:idx] + ["(" + " ".join(syllables_list[idx:idx+2]) + ")"] + syllables_list[idx+2:]))
        return monosyllabic_options + bisyllabic_options
    else:  # all possible footings
        return get_footings_helper(syllables_list)


def get_footings_helper(syllables_list, cand_so_far=""):
    # print("syllables list:", syllables_list)
    if len(syllables_list) == 0:
        # base case
        return [cand_so_far]
    else:
        cands_at_this_level = []
        # option 1 - keep the first syllable by itself
        # option 1a - foot the lone syllable
        option1a = cand_so_far + " (" + syllables_list[0] + ")"
        # print("option1a:", option1a)
        for fullstring in get_footings_helper(syllables_list[1:], option1a):
            cands_at_this_level.append(fullstring.strip())
        # option 1b - don't foot the lone syllable
        option1b = cand_so_far + " " + syllables_list[0]
        # print("option1b:", option1a)
        for fullstring in get_footings_helper(syllables_list[1:], option1b):
            cands_at_this_level.append(fullstring.strip())

        # option 2 - pair up (and foot) the first syllable with the second, if possible
        if len(syllables_list) >= 2:
            option2 = cand_so_far + " (" + syllables_list[0] + " " + syllables_list[1] + ")"
            # print("option2:", option1a)
            for fullstring in get_footings_helper(syllables_list[2:], option2):
                cands_at_this_level.append(fullstring.strip())

        return cands_at_this_level


def mark_mainstress(candidate):
    cands_at_this_level = []
    for idx, char in enumerate(candidate):
        if char == "2":
            cands_at_this_level.append(candidate[:idx] + "1" + candidate[idx+1:])

    if not cands_at_this_level:
        # there were no stresses marked in the original candidate, which means it wasn't footed
        # so just return the original candidate
        cands_at_this_level = [candidate]
    return cands_at_this_level


def get_list_of_elements(candidate):
    elements_split = candidate.split(" ")
    elements_whole = []
    i = 0
    while i < len(elements_split):
        el = elements_split[i]
        if el.startswith("(") and not el.endswith(")"):
            # it's the first half of a two-syllable foot
            elements_whole.append(el + " " + elements_split[i+1])
            i += 2
        else:
            elements_whole.append(el)
            i += 1
    return elements_whole


def add_stresses(list_of_elements, cand_so_far=""):
    if len(list_of_elements) == 0:
        # base case
        return [cand_so_far]
    else:
        cands_at_this_level = []
        el0 = list_of_elements[0]
        if not el0.startswith("("):
            # if the first element is not footed, just leave it as is
            for option in add_stresses(list_of_elements[1:], cand_so_far + (" " if cand_so_far else "") + el0):
                cands_at_this_level.append(option)
        elif " " not in el0:
            # if the first element is a single-syllable foot, stress it
            for option in add_stresses(list_of_elements[1:], cand_so_far + (" " if cand_so_far else "") + el0[:2] + "2" + el0[2:]):
                cands_at_this_level.append(option)
        else:
            # the first element is a two-syllable foot, so try stressing either of the two syllables
            trochee = el0[:2] + "2" + el0[2:]
            iamb = el0[:4] + "2" + el0[4:]
            for option_t in add_stresses(list_of_elements[1:], cand_so_far + (" " if cand_so_far else "") + trochee):
                cands_at_this_level.append(option_t)
            for option_i in add_stresses(list_of_elements[1:], cand_so_far + (" " if cand_so_far else "") + iamb):
                cands_at_this_level.append(option_i)
        return cands_at_this_level


def get_candidates(word, mainonly=False):
    if mainonly:
        # figure out all possible *single* footings of the given syllables
        footed_candidates = get_footings(word, justone=True)
    else:
        # figure out *all* possible footings of the given syllables
        footed_candidates = get_footings(word, justone=False)

    # figure out all possible stress locations for those footings
    footed_stressed_candidates = []
    for f_cand in footed_candidates:
        list_of_elements = get_list_of_elements(f_cand)
        withstresses = add_stresses(get_list_of_elements(f_cand))
        footed_stressed_candidates.extend(add_stresses(get_list_of_elements(f_cand)))

    # figure out all possible locations for main stress
    footed_stressed_withmain_candidates = []
    for f_s_cand in footed_stressed_candidates:
        footed_stressed_withmain_candidates.extend(mark_mainstress(f_s_cand))

    if mainonly:
        return [cand.replace("2", "") for cand in footed_stressed_withmain_candidates]
    else:
        return footed_stressed_withmain_candidates


def removeparens(wd):
    return wd.replace("(", "").replace(")", "")


def removestresses(wd):
    return wd.replace("1", "").replace("2", "")


def iswordinlang(wd, lang):
    wd_nofeet = removeparens(wd)
    return wd_nofeet in overt_forms[lang].keys()


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

def main_helper(TESTin):

    customizations = ""
    customizations += "_test" if TESTin else ""
    foldername = datetime.now().strftime('%Y%m%d.%H%M%S') + '_OTS'  # '-OTSoft-files'  # .%H%M%S
    os.mkdir(foldername+customizations)
    for langname in overt_forms.keys():
        for consetname in constraint_sets.keys():
            tableaux_generator = OTSoftTableauxGenerator(langname, consetname, fortesting=TESTin)
            tableaux_generator.generatetext(overt_forms[langname], foldername=foldername, customizations=customizations)


if __name__ == "__main__":
#     cands = get_candidates("H L L H")
#     print("the", len(cands), "candidates are:", cands)


    ft = [False, True]

    # generate inputs for all languages for one specific combination of arguments
    for t in [False]:
        main_helper(TESTin=t)


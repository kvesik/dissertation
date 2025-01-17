import io

frontfeatures = ["f1", "f2", "f3", "f4", "f5"]
backfeatures = ["b1", "b2", "b3", "b4", "b5"]


# def linewrite(txt, f, nl=True):
#     nl = "\n" if nl else ""
#     f.write(txt + nl)


def compose_segmental_cons():
    segmental_cons_string = ""
    for wdbound in ["", "[-word_boundary]"]:  # context-free vs noninitial
        for feat in frontfeatures + backfeatures:
            segmental_cons_string += "*" + wdbound + "[+" + feat + "]\t(tier=default)\n"
    return segmental_cons_string


def compose_VH_cons():
    VH_cons_string = ""
    for wdbound in ["", "[-word_boundary]"]:  # local vs long-distance
        for feat1 in frontfeatures:
            for feat2 in backfeatures:
                VH_cons_string += "*[+" + feat1 + "]" + wdbound + "[+" + feat2 + "]\t(tier=default)\n"
        for feat1 in backfeatures:
            for feat2 in frontfeatures:
                VH_cons_string += "*[+" + feat1 + "]" + wdbound + "[+" + feat2 + "]\t(tier=default)\n"
    return VH_cons_string


def main():
    writestring = ""
    writestring += compose_segmental_cons()
    writestring += compose_VH_cons()
    writestring = writestring.strip()
    writestring = writestring.replace("[+b5]", "[-f5]")
    with io.open("UCLAPL_all_constraints.txt", "w") as f:
        f.write(writestring)


if __name__ == "__main__":
    main()

import os

inputfolders = [f for f in os.listdir() if os.path.isdir(f)]
for f in inputfolders:
    if f.startswith("2024") and f.find("forOTS") == 16:
        timeremoved = f[:8]+f[15:]
        # nameshortened = timeremoved.replace("-OTSoft-files", "_forOTS")
        # print(f, "-->", nameshortened)
        print(f, "-->", timeremoved)
        os.rename(f, timeremoved)

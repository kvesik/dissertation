import os

inputfolders = [f for f in os.listdir() if os.path.isdir(f)]
for f in inputfolders:
    if f.startswith("2023") and f.index("OTSoft") == 16:
        timeremoved = f[:8]+f[15:]
        nameshortened = timeremoved.replace("-OTSoft-files", "_forOTS")
        print(f, "-->", nameshortened)
        os.rename(f, nameshortened)

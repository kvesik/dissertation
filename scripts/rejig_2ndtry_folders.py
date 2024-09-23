import os

outputs_folder = os.path.join("..", "sim_outs", "20240507_GLA_outputs")
os.chdir(outputs_folder)
inputfolders = [f for f in os.listdir() if os.path.isdir(f)]
for f in inputfolders:
    if "2nd try" in f:
        oldtext = "2nd try"
    elif "2try" in f:
        oldtext = "2try"
    else:
        print("no change:", f)
        continue

    newfoldername = f.replace(oldtext, "try2")
    print(f, "-->", newfoldername)
    os.rename(f, newfoldername)

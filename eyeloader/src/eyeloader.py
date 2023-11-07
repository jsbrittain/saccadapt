import pandas as pd
import numpy as np


# read eyelink data from asc file
def load_file(
    filename: str,
    *,
    verbose: bool = False,
) -> pd.DataFrame:
    with open(filename, "r") as f:
        data = f.readlines()
    # extract sampling parameters
    DISPLAY_COORDS = list(
        map(float, [x[:-1].split(" ") for x in data if "DISPLAY_COORDS" in x][0][-2:])
    )
    SAMPLE_RATE = float(
        [x[:-1].split("\t") for x in data if "RATE" in x and x.startswith("SAMPLES")][
            0
        ][4]
    )
    # extract trial parameters
    START = np.array(
        [int(x[:-1].split("\t")[1]) for x in data if x.startswith("START")], "int"
    )
    END = np.array(
        [int(x[:-1].split("\t")[1]) for x in data if x.startswith("END")], "int"
    )
    assert len(START) == len(END)
    TRIALID = [int(x.strip().split(" ")[-1]) for x in data if "TRIALID" in x]
    BLOCK = [int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR block" in x]
    RECYCLED = [
        x.strip().split(" ")[-1] == "True"
        for x in data
        if "TRIAL_VAR Trial_Recycled_" in x
    ]
    RECAL = [x.strip().split(" ")[-1] == "True" for x in data if "TRIAL_VAR Recal" in x]
    TARGPOS = [int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR targpos" in x]
    STEPPOS = [int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR steppos" in x]
    DUR = END - START
    # Target position shifts (can occur multiple times in a trial)
    TARGET_POS = [
        list(map(int, x[:-1].split(" ")[4][1:-1].split(",")))
        for x in data
        if "TARGET_POS" in x
    ]
    TARGET_POS_SAMPLE = [
        int(x.split(" ")[0].split("\t")[1]) for x in data if "TARGET_POS" in x
    ]
    assert len(TARGET_POS) == len(TARGET_POS_SAMPLE)
    TARGETS = []
    tpos = np.array(TARGET_POS, "int")
    tsample = np.array(TARGET_POS_SAMPLE, "int")
    for start, end in zip(START, END):
        indices = np.array(
            (np.greater_equal(tsample, start) & np.less_equal(tsample, end)).nonzero()[
                0
            ],
            "int",
        )
        TARGETS.append(tuple(zip(tsample[indices], tpos[indices])))
    # Fixation and saccade events (EFIX contains SFIX time; same with SACC)
    FIX = [
        (
            x.strip().split("\t")[0].split(" ")[-1],
            x.strip().split("\t")[1].split(" ")[0],
        )
        for x in data
        if x.startswith("EFIX")
    ]
    SACC = [
        (
            x.strip().split("\t")[0].split(" ")[-1],
            x.strip().split("\t")[1].split(" ")[0],
        )
        for x in data
        if x.startswith("ESACC")
    ]
    TRIAL_FIX = []
    TRIAL_SACC = []
    # for start, end in zip(START, END):
    # indices = np.array(
    #    (np.greater_equal(tsample, start) & np.less_equal(tsample, end)).nonzero()[0],
    #    "int",
    # )
    # print(FIX[indices])
    # TRIAL_FIX.append(list(FIX[indices]))
    # TRIAL_SACC.append(list(SACC[indices]))
    # Form trial dataframe
    trial = pd.DataFrame(
        data={
            "TrialID": TRIALID,
            "BlockNo": BLOCK,
            "Recycled": RECYCLED,
            "Recal": RECAL,
            "TargetPos": TARGPOS,
            "StepPos": STEPPOS,
            "StartPos": START,
            "EndPos": END,
            "Duration": DUR,
            "Targets": TARGETS,
            # "Fixations": TRIAL_FIX,
            # "Saccades": TRIAL_SACC,
        }
    )
    # isolate lines denoting eye position (those ending with ellipses)
    data = [line[:-4] for line in data if line[-4:] == "...\n"]
    # convert list[str] to numpy matrix
    data = np.genfromtxt(
        data,
        delimiter="\t",
        usecols=range(5),
        missing_values=".",
        filling_values=np.nan,
        dtype=float,
    )

    # scale data to sampling parameters
    def xtrans(x):
        return 2 * (x / DISPLAY_COORDS[0] - 0.5)

    def ytrans(x):
        return 2 * (x / DISPLAY_COORDS[1] - 0.5)

    data[:, 1] = xtrans(data[:, 1])
    data[:, 2] = ytrans(data[:, 2])
    TARGET_POS = [[xtrans(x), ytrans(y)] for x, y in TARGET_POS]
    # labels
    channel_label = [
        "sample",
        "x-pos (norm)",
        "y-pos (norm)",
        "pupil (raw)",
        "constant",
    ]

    # convert to pandas dataframe
    df = pd.DataFrame(data[:, :-1], columns=channel_label[:-1])
    # fill-in missing samples (aligns samples to indices)
    df["sample"] = df["sample"].astype("int")
    new_index = pd.Index(
        np.arange(df["sample"].iloc[0], df["sample"].iloc[-1]), name="sample"
    )
    df = df.set_index("sample").reindex(new_index).reset_index()
    # zero starting sample
    if False:
        FIRST_SAMPLE = df["sample"].iloc[0]
        START = START - FIRST_SAMPLE
        END = END - FIRST_SAMPLE
        df["sample"] = df["sample"] - FIRST_SAMPLE
    # samples to time
    channel_label[0] = "Time (msecs)"
    df[channel_label[0]] = df["sample"] * 1000 / SAMPLE_RATE  # msecs
    df = df.set_index("sample")

    # Remove relcalibation trials
    if verbose:
        print("Trials before rejection: ", len(trial))
    trial = trial[trial["Recal"] == False]  # noqa: E712
    trial = trial.reset_index(drop=True)
    if verbose:
        print("Trials after rejection: ", len(trial))

    return df

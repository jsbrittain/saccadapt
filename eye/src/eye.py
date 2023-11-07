import pandas as pd
import numpy as np


class Eye:
    def __init__(self, filename=None):
        self.data = pd.DataFrame()
        self.trial = pd.DataFrame()

        if filename is not None:
            self.load_file(filename)

    # read eyelink data from asc file
    def load_file(
        self,
        filename: str,
        *,
        verbose: bool = False,
    ) -> pd.DataFrame:
        with open(filename, "r") as f:
            data = f.readlines()
        self.read_data(data, verbose=verbose)
        return self.data

    def read_data(
        self,
        data: list,
        *,
        verbose: bool = False,
    ) -> pd.DataFrame:
        # extract sampling parameters
        self._DISPLAY_COORDS = list(
            map(
                float,
                [x[:-1].split(" ") for x in data if "DISPLAY_COORDS" in x][0][-2:],
            )
        )
        self._SAMPLE_RATE = float(
            [
                x[:-1].split("\t")
                for x in data
                if "RATE" in x and x.startswith("SAMPLES")
            ][0][4]
        )
        # extract trial parameters
        self._START = np.array(
            [int(x[:-1].split("\t")[1]) for x in data if x.startswith("START")], "int"
        )
        self._END = np.array(
            [int(x[:-1].split("\t")[1]) for x in data if x.startswith("END")], "int"
        )
        assert len(self._START) == len(self._END)
        self._TRIALID = [int(x.strip().split(" ")[-1]) for x in data if "TRIALID" in x]
        self._BLOCK = [
            int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR block" in x
        ]
        self._RECYCLED = [
            x.strip().split(" ")[-1] == "True"
            for x in data
            if "TRIAL_VAR Trial_Recycled_" in x
        ]
        self._RECAL = [
            x.strip().split(" ")[-1] == "True" for x in data if "TRIAL_VAR Recal" in x
        ]
        self._TARGPOS = [
            int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR targpos" in x
        ]
        self._STEPPOS = [
            int(x.strip().split(" ")[-1]) for x in data if "TRIAL_VAR steppos" in x
        ]
        self._DUR = self._END - self._START
        # Target position shifts (can occur multiple times in a trial)
        self._TARGET_POS = [
            list(map(int, x[:-1].split(" ")[4][1:-1].split(",")))
            for x in data
            if "TARGET_POS" in x
        ]
        self._TARGET_POS_SAMPLE = [
            int(x.split(" ")[0].split("\t")[1]) for x in data if "TARGET_POS" in x
        ]
        assert len(self._TARGET_POS) == len(self._TARGET_POS_SAMPLE)
        TARGETS = []
        tpos = np.array(self._TARGET_POS, "int")
        tsample = np.array(self._TARGET_POS_SAMPLE, "int")
        for start, end in zip(self._START, self._END):
            indices = np.array(
                (
                    np.greater_equal(tsample, start) & np.less_equal(tsample, end)
                ).nonzero()[0],
                "int",
            )
            TARGETS.append(tuple(zip(tsample[indices], tpos[indices])))
        # Fixation and saccade events (EFIX contains SFIX time; same with SACC)
        self._FIX = [
            (
                int(x.strip().split("\t")[0].split(" ")[-1]),
                int(x.strip().split("\t")[1].split(" ")[0]),
            )
            for x in data
            if x.startswith("EFIX")
        ]
        self._SACC = [
            (
                int(x.strip().split("\t")[0].split(" ")[-1]),
                int(x.strip().split("\t")[1].split(" ")[0]),
            )
            for x in data
            if x.startswith("ESACC")
        ]
        tsample = np.array([x[0] for x in self._FIX], "int")
        # Split fixations into trials
        self._TRIAL_FIX = []
        for start, end in zip(self._START, self._END):
            indices = np.array(
                (
                    np.greater_equal(tsample, start) & np.less_equal(tsample, end)
                ).nonzero()[0],
                "int",
            )
            self._TRIAL_FIX.append([self._FIX[ix] for ix in indices])
        # Split saccades into trials
        tsample = np.array([x[0] for x in self._SACC], "int")
        self._TRIAL_SACC = []
        for start, end in zip(self._START, self._END):
            indices = np.array(
                (
                    np.greater_equal(tsample, start) & np.less_equal(tsample, end)
                ).nonzero()[0],
                "int",
            )
            self._TRIAL_SACC.append([self._SACC[ix] for ix in indices])
        # create trial dataframe
        self.trial = pd.DataFrame(
            data={
                "TrialID": self._TRIALID,
                "BlockNo": self._BLOCK,
                "Recycled": self._RECYCLED,
                "Recal": self._RECAL,
                "TargetPos": self._TARGPOS,
                "StepPos": self._STEPPOS,
                "StartPos": self._START,
                "EndPos": self._END,
                "Duration": self._DUR,
                "Targets": TARGETS,
                "Fixations": self._TRIAL_FIX,
                "Saccades": self._TRIAL_SACC,
            }
        )
        # isolate lines denoting eye position in data (those ending with ellipses)
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
            return 2 * (x / self._DISPLAY_COORDS[0] - 0.5)

        def ytrans(x):
            return 2 * (x / self._DISPLAY_COORDS[1] - 0.5)

        data[:, 1] = xtrans(data[:, 1])
        data[:, 2] = ytrans(data[:, 2])
        self._TARGET_POS = [[xtrans(x), ytrans(y)] for x, y in self._TARGET_POS]
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
            self._START = self._START - FIRST_SAMPLE
            self._END = self._END - FIRST_SAMPLE
            df["sample"] = df["sample"] - FIRST_SAMPLE
        # samples to time
        channel_label[0] = "Time (msecs)"
        df[channel_label[0]] = df["sample"] * 1000 / self._SAMPLE_RATE  # msecs
        df = df.set_index("sample")

        # Remove relcalibation trials
        if verbose:
            print("Trials before rejection: ", len(self.trial))
        self.trial = self.trial[self.trial["Recal"] == False]  # noqa: E712
        self.trial = self.trial.reset_index(drop=True)
        if verbose:
            print("Trials after rejection: ", len(self.trial))
        self.data = df

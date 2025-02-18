#!/usr/bin/env python
import argparse
import pandas as pd
from pathlib import Path

# Parameters
min_saccade_duration = 30  # msecs

# Column names
RECORDING_SESSION_LABEL = "RECORDING_SESSION_LABEL"
TRIAL_INDEX = "TRIAL_INDEX"
TRIAL_SACCADE_TOTAL = "TRIAL_SACCADE_TOTAL"
CURRENT_SAC_DIRECTION = "CURRENT_SAC_DIRECTION"
CURRENT_SAC_DURATION = "CURRENT_SAC_DURATION"
CURRENT_SAC_AMPLITUDE = "CURRENT_SAC_AMPLITUDE"
# Constants
RIGHT = "RIGHT"
LEFT = "LEFT"
NO_DIRECTION = "."


def main(filename):
    # Read the data
    df = pd.read_csv(filename)

    # Get a list of unique trial labels
    trials = df[TRIAL_INDEX].unique()

    # Initialize the output data frame (empty)
    df_right = pd.DataFrame(columns=df.columns)

    # Iterate over trial labels
    for trial in trials:
        # Construct a dataframe for the current trial (all saccades)
        df_trial = df[df[TRIAL_INDEX] == trial]
        # Filter for rightward saccades only (excludes LEFT and NO_DIRECTION)
        df1 = df_trial
        df1 = df1[df1[CURRENT_SAC_DIRECTION] == RIGHT]
        # Apply the minimum saccade duration filter
        df1 = df1[df1[CURRENT_SAC_DURATION] >= min_saccade_duration]
        if len(df1) > 0:
            # Sort the remaining saccades by descending amplitude
            df1 = df1.sort_values(by=[CURRENT_SAC_AMPLITUDE], ascending=False)
            # Take the first (largest) saccade and append to the output dataframe
            df_right = pd.concat([df_right, df1.head(1)])
        else:
            # No suitable saccades found - append NaN to the output dataframe
            df_right = pd.concat([df_right, pd.DataFrame({
                RECORDING_SESSION_LABEL: [df_trial[RECORDING_SESSION_LABEL].iloc[0]],
                TRIAL_INDEX: [df_trial[TRIAL_INDEX].iloc[0]],
                TRIAL_SACCADE_TOTAL: [df_trial[TRIAL_SACCADE_TOTAL].iloc[0]],
                CURRENT_SAC_DIRECTION: [NO_DIRECTION],
                CURRENT_SAC_DURATION: pd.NA,
                CURRENT_SAC_AMPLITUDE: pd.NA
            })])

    # Save the output dataframe to the output folder
    Path("output").mkdir(parents=True, exist_ok=True)
    df_right.to_csv(Path("output") / Path(filename).name, index=False)

    # Print the output dataframe
    print(df_right)


if __name__ == "__main__":
    # Check command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The filename of the input data")
    args = parser.parse_args()
    filename = args.filename

    # Run the main function
    main(filename)

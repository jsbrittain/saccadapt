
Our preferred environment manager for Python is uv ([installation guide](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)).

To install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, to run the Python code:
```bash
uv venv
. .venv/bin/activate
uv pip install -r requirements.txt
python main.py data/test.csv
```

You can specify your own filename by running:
```bash
python main.py <filename>
```
or simply
```bash
./main.py <filename>
```

The processed data will be given the same filename, but placed in a new directory `output/`.

Where trials do not meet the admission criteria (tunable, default below) those trials are marked with NaN in the output file.

The admission criteria are:
- Rightward saccade
- Saccade duration > 30 msecs
- Only the largest remaining saccade (per trial) is considered

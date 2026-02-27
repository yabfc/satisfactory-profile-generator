# Generate a profile for [YABFC](https://github.com/yabfc/yabfc) from a Satisfactory dump

This script generates a profile that can be used in [YABFC](https://github.com/yabfc/yabfc) from a Satisfactory class descriptor dump.

## Prerequisites

- python 3.11+ or `uv` if preferred

## Locate the dump

You can find the required JSON file in your Satisfactory installation directory under:
`CommunityResources/Docs/en-US.json`
Copy `en-US.json` into this project directory, or provide the full path when running the script

## Run the Script

Using `uv`:

```bash
uv run main.py -i en-US.json
```

Or with python directly

```bash
python3 main.py -i en-US.json
```

The script will dump the generated profile in the current working directory in the file `profile.json` if no other output is specified.

### Example help output

```
usage: main.py [-h] -i INPUT [-o OUTPUT]

YABFC Profile Generator for Satisfactory dumps

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
  -o OUTPUT, --output OUTPUT  (defaults to profile.json)
```

## Contributing

If you find a bug or a way to extract recipes, items, machines, and research more easily, feel free to open an issue.

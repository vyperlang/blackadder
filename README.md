# blackadder
[black](https://github.com/psf/black)-[adder](https://github.com/vyperlang/vyper)

A code formatter for vyper.

# Usage
Use pre-commit hooks: put this in your repo's `.pre-commit-config.yaml`
```
repos:
-   repo: https://github.com/spinoch/blackadder
    rev: "master"
    hooks:
    - id: blackadder
      language_version: python3
```

To run it manually, run the following in you terminal:
```
blackadder --fast --include '\.vy$' .
```

# Warning
This is still in an experimental state. Formatting may be done incorrectly for `log` keywords if the next variable name is less than 3 characters long.
If you run into issues, check out the logs to see what happens.

As of now, `blackadder` will fail if invoked without `--fast`.
In general, black options shouldn't be expected to work except for `--diff` and `--include`.

# blackadder
[black](https://github.com/psf/black)-[adder](https://github.com/vyperlang/vyper)

# Usage
Use pre-commit hooks: put this in your repo's `.pre-commit-config.yaml`
```
repos:
-   repo: https://github.com/spinoch/blackadder
    rev: 0.1
    hooks:
    - id: blackadder
      language_version: python3
```

To run it manually, run the following in you terminal:
```
blackadder --fast --include '\.vy$' --diff .
```


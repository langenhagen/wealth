# Wealth
A suite of code and Jupyter notebooks to obtain insights into personal finances.

`Wealth` contains code and `Jupyter` notebook templates that help to get insights into all things
finance, e.g. transactions, savings, compound interest, inflation and pension.
Export your bank transaction data as CSV into your `Wealth` workspace and experiment via interactive
widgets.

The project has following structure:
```
.
├── LICENSE                         The project's license formulation.
├── prototype/                      Contains exemplaric defaults.
│   ├── config/                     Contains config file examples.
│   ├── notebooks/                  Contains the Jupyter notebook templates.
│   └── scripts/                    Contains utility scripts for the workspace.
├── README.md                       You are now here.
├── requirements.txt                Requirements.txt for a Wealth workspace project.
├── requirements-dev.txt            Additional requirements for a Wealth workspace project.
├── scripts/                        Contains utility scripts.
│   └── create-workspace.sh         Sets up a workspace.
└── src/                            Contains source files.
    ├── wealth/                     The Python source code package.
    └── setup.py                    Setup file for the Python package.
```


## Security Note
`Wealth` may handle sensible personal information.  
`Wealth` does not transfer any personal information or data derived from it to anyone.  
`Wealth` computes everything locally.


## Prerequisites
`Wealth` runs on `Linux` and `Mac OS` and requires `Python`, at least version `3.7.0`.  
`Wealth` downloads further requirements during setup.


## Setup
Wealth distinguishes between the actual `Wealth` project/repository and `workspaces` that you can
set up in order to avoid accidentally uploading private data to the internet.

To setup a `Wealth` workspace, go to the root directory of the project and run:
```bash
scripts/create-workspace.sh [--dev] [<path/to/new/workspace>]
```
You can specify a path or install a workspace under the default location:
```bash
scripts/create-workspace.sh                     # create a workspace under ~/wealth/workspace
scripts/create-workspace.sh  "~/my/finances"    # create a  workspace under ~/my/finances
```

You can provide the argument `--dev` to install additional development packages.  
Consult the script `scripts/create-workspace.sh` for further information.

Upon installation, `Wealth` creates a workspace directory with `Jupyter` notebooks, example
configuration and example data.  
You can replace the example data with you own.  

A workspace directory is separate from the `Wealth` project in order keep your data out of
`Wealth`'s version control. The data you add to the workspace or derive via `Wealth`'s tools stays
only in your hands.

After successfully running `create-workspace.sh`, you can go to the new workspace and start using
your `Wealth` workspace.


## Deinstallation
In order to delete a workspace, simply delete the workspace folder.  
If you want to delete the project `Wealth` from your system, just delete its folder.


### Import Banking Data
Online Banking services provide means to download lists of transactions in a `*.csv` file format.
You can download these `*.csv` files and feed them to `Wealth`.

1. Log in to your online bank account and download `*.csv` files. This is different for every bank.
   Usually, you may find the download/export functionality under a category called "Transactions" or
   similar. You should be able to download `CSV` data from specified time frames. It may be
   beneficial to download indivual files for fixed time frames, e.g. different `*.csv` files for
   each year.

`CSV` data from different bank accounts may have a different structure.
`Wealth` contains parsers for data of the following banks:
- `DKB - Deutsche Kreditbank Giro`
- `DKB Visa - Deutsche Kreditbank Visa`
- `N26 - with support for Spaces`
- `Sparkasse`

Each bank has their own CSV way to define the CSVs. Rename the `*.csv` files so that `Wealth` is
able to connect any given csv with the right bank.

The csv files must contain the bank account types in their file names.  
Available account-names are:
1. `dkb-giro`
2. `dkb-visa`
3. `n26-mastercard`
4. `sparkasse-giro`

For example, for an N26 credit card account, the a valid filename would be
`2021-n26-mastercard.csv`.


## License
See [LICENSE](LICENSE) file.


## Contributing
Work on your stuff locally, branch, commit and modify to your heart's content.
If there is anything you can extend, fix or improve, please do so!
Happy coding!

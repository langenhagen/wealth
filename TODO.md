# TODO
TODOs for the project `Wealth`.

- assert that label regexes yield disjoint sets of matches
- add bash script to `reimport-workspace.sh` to reimport scripts and missing notebooks.
- use a Bubbleplot for showing where you have Many Expenses, the size of the sum of the expenses
- consider stacked barplots
- have mouse hover balloon messages
- have tool to come up with regexes helping labelling transactions. E.g. cli-tool, jupyter notebook
  or via GUI.
- evaluate transactions by label
- have future predictions, e.g. via rolling mean and fourier approximation or taylor expansion
- make `clean-notebooks.sh` work recursively
- throw superfluous/old stuff out
- do something similar: https://demo.firefly-iii.org/transactions/withdrawal
- allow to add different scenarios
  - define artificial timeframes, e.g. from 2020-2099 or from Jan 2020 to July 2020
  - take initial offsets and different posts of regular lump-sum incomes, expenses, investiments
    with re-investments, like interest on interest and inflation
  - allow to combine scenarios, i.e., add them together
    - allow to deactivate scenarios
  - allow for scenario adjustments via widgets
  - allow for comparisons between scenarios
      - income vs income
      - spending vs spending
      - income vs spending
- document track.csv

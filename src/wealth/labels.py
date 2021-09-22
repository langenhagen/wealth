"""Loader for labels.yml file."""
from typing import Optional, Tuple

import yaml

from wealth.util import tree


class Label(tree.Node):
    """A label that you can attach to a transaction post."""

    def __init__(self, name: str, regex: str = None):
        """Create a new Label with the given name and regex."""
        super().__init__()
        self.name: str = name
        self.regex: Optional[str] = regex


def build_label_tree(dictionary: dict, root: Label) -> None:
    """Build a tree from a given dictionary of dictionaries."""
    for key, value in dictionary.items():
        if key == "regex":
            continue
        if isinstance(value, dict):
            label = Label(name=key, regex=value.get("regex"))
            build_label_tree(dictionary=value, root=label)
        else:
            label = Label(name=key, regex=None)
        root.children.append(label)


def load_label_tree_from_yaml() -> Tuple[Label, Label]:
    """Load labels from a yaml file and convert them to trees."""
    with open("../config/labels.yml", encoding="UTF-8") as file:
        raw_label_data = yaml.load(file, Loader=yaml.FullLoader)

    assert isinstance(raw_label_data, dict)
    assert isinstance(raw_label_data.get("Income"), dict)
    assert isinstance(raw_label_data.get("Expense"), dict)

    income_label_tree = Label("Income")
    build_label_tree(raw_label_data["Income"], income_label_tree)
    expense_label_tree = Label("Expense")
    build_label_tree(raw_label_data["Expense"], expense_label_tree)

    return income_label_tree, expense_label_tree


income_labels, expense_labels = load_label_tree_from_yaml()

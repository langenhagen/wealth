"""A simple n-ary tree implementation.

Contains a simple type and functions for working with generic directed graphs
and n-ary trees."""
import dataclasses
from typing import Callable, Iterable, List, Type


@dataclasses.dataclass
class Node:
    """A simple Node in an n-ary tree or directed graph."""

    children: List["Node"] = dataclasses.field(default_factory=list)

    def iterate_breadth_first(self) -> Iterable["Node"]:
        """Yield elements via breadth first search."""
        queue = [self]
        while queue:
            node = queue.pop(0)
            queue.extend(node.children)
            yield node

    def iterate_depth_first(self) -> Iterable["Node"]:
        """Yield elements via depth first search."""
        yield self
        for child in self.children:
            yield from child.iterate_depth_first()

    def find_path(self, predicate: Callable[[Type["Node"]], bool]):
        """Return the first path to a node that fulfills the given predicate."""
        result = [self]
        if predicate(self):
            return result

        for child in self.children:
            results = child.find_path(predicate)
            if results and predicate(results[-1]):
                return result + results
        return []

    def yield_leaves(self) -> Iterable["Node"]:
        """Yield the leaves in a given tree."""
        for node in self.iterate_depth_first():
            if node.children:
                continue
            yield node

    def get_paths_to_leaves(  # pylint: disable=W0102;
        self, path: List["Node"] = [], paths: List[List["Node"]] = []
    ) -> List[List["Node"]]:
        """Get the paths to all leaves in a given tree."""
        path.append(self)
        if not self.children:
            paths.append(path.copy())
        else:
            for child in self.children:
                child.get_paths_to_leaves(path, paths)
        path.pop()
        return paths

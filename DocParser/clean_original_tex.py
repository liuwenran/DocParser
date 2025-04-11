import re
from typing import Optional

from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexNode,
    LatexWalker,
)

def find_env_node_by_name(nodes: list[LatexNode], env_name: str) -> Optional[LatexEnvironmentNode]:

    for node in nodes:

        if isinstance(node, LatexEnvironmentNode) and node.environmentname == env_name:
            return node
        else:
            sub_nodes = getattr(node, 'nodelist', [])
            if hasattr(node, 'nodeargd') and node.nodeargd is not None:
                sub_nodes += node.nodeargd.argnlist
            # print('step in, sub_nodes', len(sub_nodes))
            env_node = find_env_node_by_name(sub_nodes, env_name)
            if env_node is not None:
                return env_node

    return None

class LatexCleaner:
    def __init__(self):
        self.macros_to_remove = {'newcommand', 'renewcommand', 'footnote'}
        self.environments_to_remove = {'figure'}

    def clean_ast(self, latex_code: str) -> list[LatexNode]:
        walker = LatexWalker(latex_code)
        nodes, _, _ = walker.get_latex_nodes()
        return self._filter_nodes(nodes)

    def clean_text(self, latex_code: str) -> str:
        cleaned_nodes = self.clean_ast(latex_code)
        return LatexNodes2Text().nodelist_to_text(cleaned_nodes)

    def _filter_nodes(self, nodes):
        return nodes
        cleaned = []
        for node in nodes:
            if isinstance(node, LatexCommentNode):
                continue
            if isinstance(node, LatexMacroNode):
                if node.macroname in self.macros_to_remove:
                    continue
            if isinstance(node, LatexEnvironmentNode):
                if node.environmentname in self.environments_to_remove:
                    continue
                node.nodelist = self._filter_nodes(node.nodelist)
            elif hasattr(node, 'nodelist') and node.nodelist:
                node.nodelist = self._filter_nodes(node.nodelist)
            cleaned.append(node)
        return cleaned


if __name__ == "__main__":

    with open('tex_results/1010.5567/paper_original.tex', 'r') as f:
        latex = f.read()

    walker = LatexWalker(latex)
    nodes, _, _ = walker.get_latex_nodes()
    document = find_env_node_by_name(nodes, 'document')
    print(document)
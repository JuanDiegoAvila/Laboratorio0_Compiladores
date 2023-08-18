from antlr4.tree.Tree import TerminalNode
from graphviz import Digraph
from dist.yalpVisitor import yalpVisitor

class TreeVisitor(yalpVisitor):
    def __init__(self):
        super().__init__()
        self.graph = Digraph()
        self.id = 0

    def visit(self, tree):
        label = self.getNodeLabel(tree)

        self.graph.node(str(self.id), label)
        padre = self.id
        self.id += 1

        if not isinstance(tree, TerminalNode):  
            for c in tree.children:  
                self.graph.edge(str(padre), str(self.id))
                self.visit(c)

        return self.graph

    def getNodeLabel(self, node):
        if isinstance(node, TerminalNode):
            return node.getText()
        else:
            class_name = type(node).__name__
            rule_name = class_name.split('.')[1] if '.' in class_name else class_name
            rule_name = rule_name[:-7] if rule_name.endswith('Context') else rule_name
            return rule_name


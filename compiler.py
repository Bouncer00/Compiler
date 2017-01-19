#!/usr/bin/env python
import argparse

from abstract_sytax_tree import AST
from code_generator import CodeGenerator
from flow_graph import FlowGraph
from parser import Parser
from analyzer2 import Analyzer2
from analyzer import Analyzer
from compiler_exceptions import CompilerException
# from lib.static_analysis import CodeAnalysis
# from lib.flow_graph import FlowGraph
# from lib.machine_code import MachineCode


def main():
    args = parse_args()
    compilation(args.file_path, args.out)


def parse_args():
    parser = argparse.ArgumentParser(description='Compiler')
    parser.add_argument(
        'file_path',
        help='.imp file'
        )
    parser.add_argument(
        '--out',
        default="a.mr",
        help='place the output into OUT')
    return parser.parse_args()


def compilation(file_path, out_path):
    parser = Parser()
    # flow_graph = FlowGraph()
    # machine_code = MachineCode()

    with open(file_path, 'r') as f:
        content = f.read()

    parse_tree = parser.parse(content)
    print parse_tree
    analyzer = Analyzer2(parse_tree)
    analyzer.analyze()
    ast_creator = AST(parse_tree)
    abstract_syntax_tree, sym_tab = ast_creator.create()
    code_generator = CodeGenerator(abstract_syntax_tree, sym_tab)
    code = code_generator.generate()
    for i in range(len(code)):
        print str(i), code[i]

    with open("labor4/code", 'w') as f:
        for line in code:
            f.write(line + '\n')
    # flow_graph = FlowGraph(parse_tree, abstract_syntax_tree)
    # flow_graph.create_flow_graph()

if __name__ == '__main__':
    main()
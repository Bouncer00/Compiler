#!/usr/bin/env python

# Yet another MGC compiler
# Author Adam Bobowski
#
# Compiler runner

import argparse

from parser import Parser
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

    # try:
    parse_tree = parser.parse(content)
    analyzer = Analyzer(parse_tree)
    analyzer.analyze()
    # print(parse_tree)
        # symtab, ast = analyser.check(ptree)
        # graph = flow_graph.convert(ast)
        # code = machine_code.gen(graph, symtab)
    # except YamcError:
    #     exit(1)

    # with open(out_path, 'w') as f:
    #     for line in code:
    #         f.write(line + '\n')


if __name__ == '__main__':
    main()
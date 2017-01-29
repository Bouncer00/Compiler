#!/usr/bin/env python
import argparse
import sys

from abstract_sytax_tree import AST
from code_generator import CodeGenerator
from code_parser import Parser
from analyzer2 import Analyzer2
from compiler_exceptions import CompilerException


def main():
    args = parse_args()
    compilation(args.file_path, args.out_file)


def parse_args():
    parser = argparse.ArgumentParser(description='Compiler')
    parser.add_argument(
        'file_path',
        help='.imp file'
        )
    parser.add_argument(
        'out_file',
        default="out.mr",
        help='out file')
    return parser.parse_args()


def compilation(file_path, out_path):
    parser = Parser()

    with open(file_path, 'r') as f:
        content = f.read()

    parse_tree = parser.parse(content)
    print parse_tree
    analyzer = Analyzer2(parse_tree)
    try:
        analyzer.analyze()
    except CompilerException:
        print CompilerException.message
        sys.exit(1)


    ast_creator = AST(parse_tree)
    abstract_syntax_tree, sym_tab = ast_creator.create()
    code_generator = CodeGenerator(abstract_syntax_tree, sym_tab)
    code = code_generator.generate()
    for i in range(len(code)):
        print str(i), code[i]

    with open(out_path, 'w') as f:
        for line in code:
            f.write(line + '\n')

if __name__ == '__main__':
    main()
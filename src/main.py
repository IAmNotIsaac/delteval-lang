from delta_lexer import DeltaLexer
from delta_parser import DeltaParser
from delta_executor import DeltaExecutor
from delta_types import *


source = open("delta_scripts/functions_test.delta").read()

lexer = DeltaLexer(source)
tokens = lexer.parse()

parser = DeltaParser(tokens)
program = parser.parse()

executor = DeltaExecutor(program)
executor.execute()
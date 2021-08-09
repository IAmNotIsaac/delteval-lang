from delta_lexer import DeltaLexer
from delta_parser import DeltaParser
from delta_executor import DeltaExecutor


source = open("delta_scripts/variables_test.delta").read()

lexer = DeltaLexer(source)
tokens = lexer.parse()

parser = DeltaParser(tokens)
program = parser.parse()

executor = DeltaExecutor(program)
executor.execute()
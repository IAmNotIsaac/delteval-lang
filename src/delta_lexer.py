from delta_types import DeltaNumber


class Token:
	TYPE_INT 		= 	0x00_0000
	TYPE_FLOAT 		= 	0x00_0001
	TYPE_IDENTIFER	=	0x00_0002

	OP_EOS			=	0x01_0000 # end of statement
	OP_EOF			=	0x01_0001 # end of file

	OP_PLUS			= 	0x01_0002
	OP_MINUS		=	0x01_0003
	OP_MULTIPLY		=	0x01_0004
	OP_DIVIDE		=	0x01_0005
	OP_LBRACKET		=	0x01_0006
	OP_RBRACKET		=	0x01_0007
	OP_ASSIGN		=	0x01_0008
	OP_POWER		=	0x01_0009
	
	OP_EQUALS		=	0x01_000A
	OP_NEQUALS		=	0x01_000B
	OP_LESSER		=	0x01_000C
	OP_GREATER		=	0x01_000D
	OP_LEQUALS		=	0x01_000E
	OP_GEQUALS		=	0x01_000F

	OP_SCOPE_BEGIN	=	0x01_0010
	OP_SCOPE_END	=	0x01_0011

	def __init__(self, tok_type: int, value=None) -> None:
		self.tok_type = tok_type
		self.value = value
	

	def __repr__(self) -> str:
		REPR_KEY = {
			Token.TYPE_INT:			"INT",
			Token.TYPE_FLOAT:		"FLOAT",
			Token.TYPE_IDENTIFER:	"IDENT", 

			Token.OP_EOS:			"EOS",
			Token.OP_EOF:			"EOF",

			Token.OP_PLUS:			"OP_PLUS",
			Token.OP_MINUS:			"OP_MINUS",
			Token.OP_MULTIPLY:		"OP_MULTIPLY",
			Token.OP_DIVIDE:		"OP_DIVIDE",
			Token.OP_LBRACKET:		"OP_LBRACKET",
			Token.OP_RBRACKET:		"OP_RBRACKET",
			Token.OP_ASSIGN:		"OP_ASSIGN",
			Token.OP_POWER:			"OP_POWER",

			Token.OP_EQUALS:		"OP_EQUALS",
			Token.OP_NEQUALS:		"OP_NEQUALS",
			Token.OP_LESSER:		"OP_LESSER",
			Token.OP_GREATER:		"OP_GREATER",
			Token.OP_LEQUALS:		"OP_LEQUALS",
			Token.OP_GEQUALS:		"OP_GEQUALS",

			Token.OP_SCOPE_BEGIN:	"OP_SCOPE_BEGIN",
			Token.OP_SCOPE_END:		"OP_SCOPE_END"
		}

		return f"{REPR_KEY[self.tok_type]}({self.value})" if self.value != None else f"{REPR_KEY[self.tok_type]}"
	

	def matches(self, comp_tok_type) -> bool:
		return True if self.tok_type == comp_tok_type else False
	

	def matches_any(self, comp_tok_types) -> bool:
		return True if self.tok_type in comp_tok_types else False



class DeltaLexer:
	COMMENT_CHAR = "#"
	OPEN_MULTILINE_COMMENT_CHAR = ">"
	CLOSE_MULTILINE_COMMENT_CHAR = "<"
	LETTERS = "abcdefghijklmnopqrstuvwxyz_"
	NUMBERS = "1234567890."
	OPERATORS = ";+-*/()=!<>^{}"
	OPERATORS_COMBOS = {
		";": 	Token.OP_EOS,

		"+": 	Token.OP_PLUS,
		"-": 	Token.OP_MINUS,
		"*": 	Token.OP_MULTIPLY,
		"/": 	Token.OP_DIVIDE,
		"(": 	Token.OP_LBRACKET,
		")": 	Token.OP_RBRACKET,
		"=":	Token.OP_ASSIGN,
		"^":	Token.OP_POWER,

		"==":	Token.OP_EQUALS,
		"!=":	Token.OP_NEQUALS,
		"<":	Token.OP_LESSER,
		">":	Token.OP_GREATER,
		"<=":	Token.OP_LEQUALS,
		">=":	Token.OP_GEQUALS,

		"{":	Token.OP_SCOPE_BEGIN,
		"}":	Token.OP_SCOPE_END
	}


	def __init__(self, source: str) -> None:
		self.source = source
		
		self.index = -1
		self.char = None

		self.advance()
	

	def advance(self) -> None:
		self.index += 1
		self.last_char = self.char
		self.char = self.source[self.index] if self.index < len(self.source) else None
	

	def parse(self) -> list:
		tokens = []
		lock_mode = 0	# 0 = no lock, 1 = comment lock, 2 = multiline comment lock

		tokens.append(Token(Token.OP_SCOPE_BEGIN))

		while self.char != None:
			if self.char == DeltaLexer.COMMENT_CHAR:
				if lock_mode == 2:
					if self.last_char == DeltaLexer.CLOSE_MULTILINE_COMMENT_CHAR:
						lock_mode = 0
				else:
					lock_mode = int(not lock_mode)
			elif self.char == "\n" and lock_mode == 1:
				lock_mode = 0
			elif self.last_char == DeltaLexer.COMMENT_CHAR and self.char == DeltaLexer.OPEN_MULTILINE_COMMENT_CHAR and lock_mode == 1:
				lock_mode = 2

			if lock_mode:
				self.advance()
			elif self.char in DeltaLexer.LETTERS:
				tokens.append(self.make_identifier())
			elif self.char in DeltaLexer.NUMBERS:
				tokens.append(self.make_number())
			elif self.char in DeltaLexer.OPERATORS:
				tokens.append(self.make_operator())
			else:
				self.advance()

		tokens.append(Token(Token.OP_SCOPE_END))
		tokens.append(Token(Token.OP_EOF))

		return tokens
	

	def make_identifier(self) -> Token:
		identifier = ""

		while self.char and self.char in DeltaLexer.LETTERS + DeltaLexer.NUMBERS:
			if self.char == ".":
				break

			identifier += self.char

			self.advance()
		
		return Token(Token.TYPE_IDENTIFER, identifier)



	def make_number(self) -> Token:
		num_str = ""
		dot_count = 0

		while self.char and self.char in DeltaLexer.NUMBERS:
			if self.char == ".":
				dot_count += 1
			
			num_str += self.char

			self.advance()
		
		if not dot_count:
			return Token(Token.TYPE_INT, int(num_str))
		elif dot_count == 1:
			return Token(Token.TYPE_FLOAT, float(num_str))
		else:
			# error message!
			pass
	

	def make_operator(self) -> Token:
		op_combo = ""
		test_combo = ""

		while self.char and self.char in DeltaLexer.OPERATORS:
			test_combo += self.char

			if test_combo in DeltaLexer.OPERATORS_COMBOS.keys():
				op_combo = test_combo

			self.advance()
		
		if op_combo in DeltaLexer.OPERATORS_COMBOS.keys():
			return Token(DeltaLexer.OPERATORS_COMBOS[op_combo])
		else:
			# error message!
			pass
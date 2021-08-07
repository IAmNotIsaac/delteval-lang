from os import stat
from delta_lexer import Token


class Node:
	pass


class ScopeNode(Node):
	def __init__(self, statements) -> None:
		self.statements = statements
	

	def __repr__(self) -> str:
		return f"{self.statements}"


class NumberNode(Node):
	def __init__(self, tok) -> None:
		self.tok = tok
	

	def __repr__(self) -> str:
		return f"{self.tok.value}"


class BinOpNode(Node):
	def __init__(self, left_node, op_tok, right_node) -> None:
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	
	def __repr__(self) -> str:
		return f"({self.left_node} {self.op_tok} {self.right_node})"


class UnaryOpNode(Node):
	def __init__(self, op_tok, node) -> None:
		self.op_tok = op_tok
		self.node = node
	

	def __repr__(self) -> str:
		return f"({self.op_tok} {self.node})"



class DeltaParser:
	def __init__(self, tokens: list) -> None:
		self.tokens = tokens

		self.index = -1
		self.token = None

		self.advance()
	

	def advance(self) -> None:
		self.index += 1
		self.token = self.tokens[self.index] if self.index < len(self.tokens) else None
	

	def parse(self) -> Node:
		expr = self.make_scope()
		return expr
	

	#####


	def make_scope(self) -> Node:
		if self.token.matches(Token.OP_SCOPE_BEGIN):
			self.advance()

			statements = []

			while True:
				statements.append(self.make_scope())
				self.advance()

				if self.token.matches(Token.OP_EOS):
					continue
				elif self.token.matches(Token.OP_SCOPE_END):
					break
				else:
					# error message!
					pass

			return ScopeNode(statements)
		
		return self.make_expression()
		

	def make_expression(self) -> Node:
		return self.make_comp_expr()


	def make_comp_expr(self) -> Node:
		return self.binary_op(self.make_arith_expression, [Token.OP_EQUALS, Token.OP_NEQUALS, Token.OP_LESSER, Token.OP_GREATER, Token.OP_LEQUALS, Token.OP_GEQUALS])


	def make_arith_expression(self) -> Node:
		return self.binary_op(self.make_term, [Token.OP_PLUS, Token.OP_MINUS])
	

	def make_term(self) -> Node:
		return self.binary_op(self.make_factor, [Token.OP_MULTIPLY, Token.OP_DIVIDE])


	def make_factor(self) -> Node:
		token = self.token

		if token.matches_any([Token.OP_PLUS, Token.OP_MINUS]):
			self.advance()

			factor = self.make_factor()

			return UnaryOpNode(token, factor)
		

		return self.make_power()
	

	def make_power(self) -> Node:
		return self.binary_op(self.make_atom, [Token.OP_POWER], self.make_factor)
	

	def make_atom(self) -> Node:
		token = self.token

		if token.matches_any([Token.TYPE_INT, Token.TYPE_FLOAT]):
			self.advance()

			return NumberNode(token)
		

		elif token.matches(Token.OP_LBRACKET):
			self.advance()

			expr = self.make_expression()

			if self.token.matches(Token.OP_RBRACKET):
				self.advance()

				return expr


	#####


	def binary_op(self, func_a, ops, func_b=None) -> Node:
		func_b = func_a if func_b == None else func_b

		left = func_a()

		while self.token.matches_any(ops):
			op_tok = self.token
			self.advance()

			right = func_b()

			left = BinOpNode(left, op_tok, right)
		
		return left
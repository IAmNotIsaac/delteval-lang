from os import stat
from delta_lexer import Token
from delta_types import DeltaNone, DeltaNumber


class Node:
	pass


class NumberNode(Node):
	def __init__(self, tok) -> None:
		self.tok = tok
	

	def __repr__(self) -> str:
		return f"{self.tok.value}"


class BooleanNode(Node):
	def __init__(self, tok) -> None:
		self.tok = tok
	

	def __repr__(self) -> str:
		return f"{self.tok}"


class StringNode(Node):
	def __init__(self, tok) -> None:
		self.tok = tok
	

	def __repr__(self) -> str:
		return f"\"{self.tok.value}\""


class ArrayNode(Node):
	def __init__(self, length, value) -> None:
		self.length = length
		self.value = value
	

	def __repr__(self) -> str:
		return f"{self.value}"


class VarAccessNode(Node):
	def __init__(self, name_tok) -> None:
		self.name_tok = name_tok
	

	def __repr__(self) -> str:
		return f"VariableAccess({self.name_tok.value})"


class VarAssignNode(Node):
	def __init__(self, name_tok, node) -> None:
		self.name_tok = name_tok
		self.node = node
	

	def __repr__(self) -> str:
		return f"VariableAssign({self.name_tok.value} = {self.node})"


class ScopeNode(Node):
	def __init__(self, statements) -> None:
		self.statements = statements

		# we use these for the executor
		self.variables = {}
		self.parent = None
	

	def __repr__(self) -> str:
		return f"Scope{self.statements}"

	
	# also used for the executor
	def get_variable_owner(self, var_name):
		if var_name in self.variables:
			return self

		elif self.parent:
			return self.parent.get_variable_owner(var_name)
		
		else:
			return None

	
	def get_variable(self, var_name):
		owner = self.get_variable_owner(var_name)

		if owner:
			return owner.variables[var_name]
		else:
			return DeltaNone()
	

	def set_variable(self, var_name, value):
		owner = self.get_variable_owner(var_name)

		if owner:
			owner.variables[var_name] = value
		else:
			self.variables[var_name] = value


class IfNode(Node):
	def __init__(self, eval_scope, action_scope) -> None:
		self.eval_scope = eval_scope
		self.action_scope = action_scope


class PrintNode(Node):
	def __init__(self, node) -> None:
		self.node = node
	

	def __repr__(self) -> str:
		return f"Print({self.node})"


class ReturnNode(Node):
	def __init__(self, node) -> None:
		self.node = node
	

	def __repr__(self) -> str:
		return f"Print({self.node})"


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
		expr = self.make_expression()
		return expr
	

	#####
		

	def make_expression(self) -> Node:
		if self.token.matches(Token.TYPE_KEYWORD):
			if self.token.value == "print":
				self.advance()
				return PrintNode(self.make_expression())
			
			elif self.token.value == "return":
				self.advance()
				return ReturnNode(self.make_expression())
			
			elif self.token.value == "let":
				self.advance()

				if self.token.matches(Token.TYPE_IDENTIFER):
					var_name = self.token
					self.advance()

					if self.token.matches(Token.OP_ASSIGN):
						self.advance()

						return VarAssignNode(var_name, self.make_expression())
		
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
		

		elif token.matches(Token.TYPE_STRING):
			self.advance()

			return StringNode(token)
		

		elif token.matches(Token.TYPE_IDENTIFER):
			self.advance()

			return VarAccessNode(token)
		

		elif token.matches(Token.TYPE_KEYWORD):
			if token.value == "true":
				self.advance()
				return BooleanNode(token)

			elif token.value == "false":
				self.advance()
				return BooleanNode(token)
			
			elif token.value == "if":
				self.advance()

				eval_scope = self.make_expression()

				if self.token.matches(Token.TYPE_KEYWORD) and self.token.value == "then":
					self.advance()

					return IfNode(eval_scope, self.make_scope())
		

		elif token.matches(Token.OP_LBRACKET):
			self.advance()

			expr = self.make_expression()

			if self.token.matches(Token.OP_RBRACKET):
				self.advance()

				return expr
		

		elif token.matches(Token.OP_ARRAY_BEGIN):
			self.advance()

			expressions = []

			while True:
				expr = self.make_expression()

				if self.token.matches(Token.OP_ARRAY_END):
					expressions.append(expr)
					self.advance()
					break

				elif self.token.matches(Token.OP_COMMA):
					expressions.append(expr)
					self.advance()

					if self.token.matches(Token.OP_ARRAY_END):
						break

					else:
						continue
				
				else:
					# error!
					print(f"warning: did not expect {self.token}!")

			length = NumberNode(Token(Token.TYPE_INT, len(expressions)))

			if self.token.matches(Token.OP_SPECIFY):
				self.advance()

				if self.token.matches(Token.OP_ARRAY_BEGIN):
					self.advance()

					expr = self.make_expression()

					if self.token.matches(Token.OP_ARRAY_END):
						self.advance()

						length = expr

			return ArrayNode(length, expressions)

		return self.make_scope()


	def make_scope(self) -> Node:
		if self.token.matches(Token.OP_SCOPE_BEGIN):
			self.advance()

			statements = []

			while True:
				expr = self.make_expression()

				if expr:
					if self.token.matches(Token.OP_EOS):
						statements.append(expr)
						self.advance()
						continue

					elif self.token.matches(Token.OP_SCOPE_END):
						statements.append(expr)
						break

					else:
						# ?????
						statements.append(expr)
				
				else:
					break
				

			if self.token.matches(Token.OP_SCOPE_END):
				self.advance()

				return ScopeNode(statements)


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
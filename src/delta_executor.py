from delta_types import *
from delta_parser import Node, ScopeNode
from delta_lexer import Token


class DeltaExecutor:
	def __init__(self, program: ScopeNode) -> None:
		self.program = program

	
	def execute(self) -> None:
		self.visit(self.program)
		# for program in self.program:
		# 	for statement in program.statements:
		# 		res = self.visit(statement)
		# 		print(res)
	

	def visit(self, node) -> Node:
		method_name = f"visit_{(type(node)).__name__}"
		method = getattr(self, method_name)
		return method(node)
	

	def visit_ScopeNode(self, node) -> Node:
		for statement in node.statements:
			res = self.visit(statement)
			if not isinstance(res, DeltaScope):
				print(res)
		return DeltaScope(node.statements)
	

	def visit_NumberNode(self, node) -> Node:
		return DeltaNumber(node.tok.value)


	def visit_BinOpNode(self, node) -> None:
		OP_METHODS = {
			Token.OP_PLUS: 			"add",
			Token.OP_MINUS:			"subtract",
			Token.OP_MULTIPLY:		"multiply",
			Token.OP_DIVIDE:		"divide",
			Token.OP_POWER:			"power",
			Token.OP_EQUALS:		"comp_ee",
			Token.OP_NEQUALS:		"comp_ne",
			Token.OP_LESSER:		"comp_lr",
			Token.OP_GREATER:		"comp_gr",
			Token.OP_LEQUALS:		"comp_le",
			Token.OP_GEQUALS:		"comp_ge",
		}

		left = self.visit(node.left_node)
		right = self.visit(node.right_node)

		op_method = getattr(left, OP_METHODS[node.op_tok.tok_type])
		result = op_method(right)

		return result
	

	def visit_UnaryOpNode(self, node) -> None:
		number = self.visit(node.node)

		if node.op_tok.matches(Token.OP_PLUS):
			result = number.abs()
		elif node.op_tok.matches(Token.OP_MINUS):
			result = number.neg()
		
		return result

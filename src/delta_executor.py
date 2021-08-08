from delta_types import *
from delta_parser import Node, ReturnNode, ScopeNode
from delta_lexer import Token


class DeltaExecutor:
	def __init__(self, program: ScopeNode) -> None:
		self.program = program

	
	def execute(self) -> None:
		self.visit(self.program)
	

	def visit(self, node) -> Node:
		method_name = f"visit_{(type(node)).__name__}"
		method = getattr(self, method_name)
		return method(node)
	

	def visit_NumberNode(self, node):
		return DeltaNumber(node.tok.value)
	

	def visit_BooleanNode(self, node):
		return DeltaBool(node.tok.value)
	

	def visit_PrintNode(self, node):
		print(self.visit(node.node))
		return None
	

	def visit_ScopeNode(self, node):
		for statement in node.statements:
			res = self.visit(statement)

			if isinstance(statement, ReturnNode):
				return res
	

	def visit_ReturnNode(self, node):
		return self.visit(node.node)


	def visit_IfNode(self, node):
		res = self.visit(node.eval_scope)

		if res.value == True:
			self.visit(node.action_scope)
			return True
		return False


	def visit_BinOpNode(self, node):
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
	

	def visit_UnaryOpNode(self, node):
		number = self.visit(node.node)

		if node.op_tok.matches(Token.OP_PLUS):
			result = number.abs()
		elif node.op_tok.matches(Token.OP_MINUS):
			result = number.neg()
		
		return result

from delta_types import *
from delta_parser import Node, ReturnNode, ScopeNode
from delta_lexer import Token


class DeltaExecutor:
	def __init__(self, program: ScopeNode) -> None:
		self.program = program

	
	def execute(self) -> None:
		self.visit(self.program, None)
	

	def visit(self, node, scope) -> Node:
		method_name = f"visit_{(type(node)).__name__}"
		method = getattr(self, method_name)
		return method(node, scope)
	

	def visit_NumberNode(self, node, scope):
		return DeltaNumber(node.tok.value)
	

	def visit_BooleanNode(self, node, scope):
		return DeltaBool(node.tok.value)
	

	def visit_StringNode(self, node, scope):
		return DeltaString(node.tok.value)


	def visit_VarAccessNode(self, node, scope):
		return scope.get_variable(node.name_tok.value)


	def visit_VarAssignNode(self, node, scope):
		scope.set_variable(node.name_tok.value, self.visit(node.node, scope))
		return DeltaNone


	def visit_PrintNode(self, node, scope):
		print(self.visit(node.node, scope))
		return DeltaNone
	

	def visit_ScopeNode(self, node, scope):
		for statement in node.statements:
			if isinstance(statement, ScopeNode):
				statement.parent = node
			
			res = self.visit(statement, node)

			if isinstance(statement, ReturnNode):
				return res
		
		return DeltaNone
	

	def visit_ReturnNode(self, node, scope):
		return self.visit(node.node, scope)


	def visit_IfNode(self, node, scope):
		res = self.visit(node.eval_scope, scope)

		if res.value == True:
			self.visit(node.action_scope, scope)
			return DeltaBool(True)
		
		return DeltaBool(False)


	def visit_BinOpNode(self, node, scope):
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

		left = self.visit(node.left_node, scope)
		right = self.visit(node.right_node, scope)

		op_method = getattr(left, OP_METHODS[node.op_tok.tok_type])
		result = op_method(right)

		return result
	

	def visit_UnaryOpNode(self, node, scope):
		number = self.visit(node.node, scope)

		if node.op_tok.matches(Token.OP_PLUS):
			result = number.abs()
		elif node.op_tok.matches(Token.OP_MINUS):
			result = number.neg()
		
		return result

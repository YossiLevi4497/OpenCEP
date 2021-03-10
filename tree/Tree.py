from typing import List
from copy import deepcopy

from base.Pattern import Pattern
from base.PatternStructure import PatternStructure, CompositeStructure, UnaryStructure, PrimitiveEventStructure, \
    NegationOperator
from misc.ConsumptionPolicy import ConsumptionPolicy
from plan.TreePlan import TreePlan, TreePlanNode, TreePlanLeafNode, TreePlanNestedNode, TreePlanUnaryNode, \
    OperatorTypes, TreePlanInternalNode
from tree.nodes.AndNode import AndNode
from tree.nodes.KleeneClosureNode import KleeneClosureNode
from tree.nodes.LeafNode import LeafNode
from tree.nodes.NegationNode import NegativeSeqNode, NegativeAndNode, NegationNode
from tree.nodes.Node import Node, PatternParameters
from tree.PatternMatchStorage import TreeStorageParameters
from tree.nodes.SeqNode import SeqNode


class Tree:
    """
    Represents an evaluation tree. Implements the functionality of constructing an actual tree from a "tree positive_structure"
    object returned by a tree builder. Other than that, merely acts as a proxy to the tree root node.
    The pattern_id parameter is used in multi-pattern mode.
    """
    def __init__(self, tree_plan: TreePlan, pattern: Pattern, storage_params: TreeStorageParameters,
                 pattern_id: int = None):
        pattern_parameters = PatternParameters(pattern.window, pattern.confidence)
        self.__root = self.__construct_tree(pattern.full_structure, tree_plan.root,
                                            Tree.__get_operator_arg_list(pattern.full_structure),
                                            pattern_parameters, None, pattern.consumption_policy)
        if pattern.consumption_policy is not None and \
                pattern.consumption_policy.should_register_event_type_as_single(True):
            for event_type in pattern.consumption_policy.single_types:
                self.__root.register_single_event_type(event_type)

        self.__apply_condition(pattern)
        self.__root.create_storage_unit(storage_params)

        self.__root.create_parent_to_info_dict()
        self.__root.set_is_output_node(True)
        if pattern_id is not None:
            pattern.id = pattern_id
            self.__root.propagate_pattern_id(pattern_id)

    def __apply_condition(self, pattern: Pattern):
        """
        Applies the condition of the given pattern on the evaluation tree.
        The condition is copied since it is modified inside the recursive apply_condition call.
        """
        condition_copy = deepcopy(pattern.condition)
        self.__root.apply_condition(condition_copy)
        if condition_copy.get_num_conditions() > 0:
            raise Exception("Unused conditions after condition propagation: {}".format(
                condition_copy.get_conditions_list()))

    def get_leaves(self):
        return self.__root.get_leaves()

    def get_matches(self):
        while self.__root.has_unreported_matches():
            yield self.__root.get_next_unreported_match()

    def get_structure_summary(self):
        """
        Returns a tuple summarizing the structure of the tree.
        """
        return self.__root.get_structure_summary()

    @staticmethod
    def __get_operator_arg_list(operator: PatternStructure):
        """
        Returns the list of arguments of the given operator for the tree construction process.
        """
        if isinstance(operator, CompositeStructure):
            return operator.args
        if isinstance(operator, UnaryStructure):
            return [operator.arg]
        # a PrimitiveEventStructure
        return [operator]

    @staticmethod
    def __instantiate_internal_node(operator_node: TreePlanInternalNode, pattern_params: PatternParameters,
                                    parent: Node):
        """
        Creates an internal node representing a given operator.
        """
        if operator_node.operator == OperatorTypes.SEQ:
            return SeqNode(pattern_params, parent)
        if operator_node.operator == OperatorTypes.AND:
            return AndNode(pattern_params, parent)
        if operator_node.operator == OperatorTypes.NSEQ:
            return NegativeSeqNode(pattern_params, operator_node.is_unbounded, parent)
        if operator_node.operator == OperatorTypes.NAND:
            return NegativeAndNode(pattern_params, operator_node.is_unbounded, parent)
        if operator_node.operator == OperatorTypes.KC:
            return KleeneClosureNode(pattern_params, operator_node.min_size, operator_node.max_size, parent)
        raise Exception("Unknown or unsupported operator %s" % (operator_node.operator,))

    def __handle_primitive_event(self, tree_plan_leaf: TreePlanLeafNode, primitive_event_structure: PatternStructure,
                                 pattern_params: PatternParameters, parent: Node, consumption_policy: ConsumptionPolicy):
        """
        Creates a leaf node for a primitive events.
        """
        # this is a temporary hack used until the procedure is modified to extract event details from tree plan leaves
        if isinstance(primitive_event_structure, NegationOperator):
            primitive_event_structure = primitive_event_structure.arg

        if not isinstance(primitive_event_structure, PrimitiveEventStructure):
            raise Exception("Illegal operator for a tree leaf: %s" % (primitive_event_structure,))
        if consumption_policy is not None and \
                consumption_policy.should_register_event_type_as_single(False, primitive_event_structure.type):
            parent.register_single_event_type(primitive_event_structure.type)
        return LeafNode(pattern_params, tree_plan_leaf.event_index, primitive_event_structure, parent)

    def __handle_unary_structure(self, unary_tree_plan: TreePlanUnaryNode,
                                 root_operator: PatternStructure, args: List[PatternStructure],
                                 pattern_params: PatternParameters, parent: Node, consumption_policy: ConsumptionPolicy):
        """
        Creates an internal unary node possibly containing nested operators.
        """
        if parent is None and isinstance(root_operator, UnaryStructure):
            # a special case where the topmost operator of the pattern is unary
            current_operator = root_operator
        else:
            # this unary structure is surrounded with a composite structure, hence need to use the args parameters
            current_operator = args[unary_tree_plan.index]

        if not isinstance(current_operator, UnaryStructure):
            raise Exception("Illegal operator for a unary tree node: %s" % (current_operator,))

        unary_node = self.__instantiate_internal_node(unary_tree_plan, pattern_params, parent)
        nested_operator = current_operator.arg
        unary_operator_child = unary_tree_plan.child
        if isinstance(unary_operator_child, TreePlanLeafNode):
            # non-nested unary operator
            child = self.__construct_tree(current_operator, unary_operator_child,
                                      [nested_operator], pattern_params, unary_node, consumption_policy)
        elif isinstance(unary_operator_child, TreePlanNestedNode):
            # a nested unary operator
            child = self.__construct_tree(nested_operator, unary_operator_child.sub_tree_plan,
                                          Tree.__get_operator_arg_list(nested_operator), pattern_params, unary_node,
                                          consumption_policy)
        else:
            raise Exception("Invalid tree plan node under an unary node")
        unary_node.set_subtree(child)
        return unary_node

    def __construct_tree(self, root_operator: PatternStructure, tree_plan: TreePlanNode,
                         args: List[PatternStructure], pattern_params: PatternParameters, parent: Node,
                         consumption_policy: ConsumptionPolicy):
        """
        Recursively builds an evaluation tree according to the specified structure.
        """
        if isinstance(tree_plan, TreePlanUnaryNode):
            # this is an unary operator (possibly encapsulating a nested structure)
            return self.__handle_unary_structure(tree_plan, root_operator, args,
                                                 pattern_params, parent, consumption_policy)

        if isinstance(tree_plan, TreePlanLeafNode):
            # This is a leaf
            return self.__handle_primitive_event(tree_plan, args[tree_plan.original_event_index],
                                                 pattern_params, parent, consumption_policy)

        if isinstance(tree_plan, TreePlanNestedNode):
            # This is a nested node, therefore needs to use construct a subtree of this nested tree, recursively.
            return self.__construct_tree(args[tree_plan.nested_event_index], tree_plan.sub_tree_plan, tree_plan.args,
                                         pattern_params, parent, consumption_policy)

        # isinstance(tree_plan, TreePlanBinaryNode)
        current = self.__instantiate_internal_node(tree_plan, pattern_params, parent)
        left_subtree = self.__construct_tree(root_operator, tree_plan.left_child, args,
                                             pattern_params, current, consumption_policy)
        right_subtree = self.__construct_tree(root_operator, tree_plan.right_child, args,
                                              pattern_params, current, consumption_policy)
        current.set_subtrees(left_subtree, right_subtree)
        return current

    def get_last_matches(self):
        """
        After the system run is completed, retrieves and returns the last pending matches.
        As of now, the only case in which such matches may exist is if a pattern contains an unbounded negative event
        (e.g., SEQ(A,B,NOT(C)), in which case positive partial matches wait for timeout before proceeding to the root.
        """
        if not isinstance(self.__root, NegationNode):
            return []
        # this is the node that contains the pending matches
        first_unbounded_negative_node = self.__root.get_first_unbounded_negative_node()
        if first_unbounded_negative_node is None:
            return []
        first_unbounded_negative_node.flush_pending_matches()
        # the pending matches were released and have hopefully reached the root
        return self.get_matches()

    def get_root(self):
        """
        Returns the root node of the tree.
        """
        return self.__root

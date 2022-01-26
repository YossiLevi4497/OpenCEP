from plan.negation.NegationAlgorithm import *
from plan.negation.StatisticNegationAlgorithm import StatisticNegationAlgorithm
from plan.TreePlan import TreePlanBinaryNode

class LowestPositionNegationAlgorithm(NegationAlgorithm):
    """
    This class represents the lowest position negation algorithm.
    """
    def _add_negative_part_in_position(self, pattern: Pattern, positive_tree_plan: TreePlanBinaryNode,
                                       node_under_negation: TreePlanLeafNode, index: int, node_name: str,
                                       is_unbounded: bool):
        # position is on right side
        if node_name in positive_tree_plan.right_child.get_event_names():
            if len(positive_tree_plan.right_child.get_event_names()) > 1:
                self._add_negative_part_in_position(pattern, positive_tree_plan.right_child, node_under_negation, index,
                                                    node_name, is_unbounded)
            else:
                positive_tree_plan.right_child = NegationAlgorithm._instantiate_negative_node(pattern, node_under_negation,
                                                                                  positive_tree_plan.right_child, is_unbounded)
        # position is on left side
        else:
            if len(positive_tree_plan.left_child.get_event_names()) > 1:
                self._add_negative_part_in_position(pattern, positive_tree_plan.left_child, node_under_negation, index,
                                                    node_name, is_unbounded)
            else:
                positive_tree_plan.left_child = NegationAlgorithm._instantiate_negative_node(pattern, node_under_negation,
                                                                                  positive_tree_plan.left_child, is_unbounded)

    def _add_negative_part(self, pattern: Pattern, statistics: Dict, positive_tree_plan: TreePlanBinaryNode,
                           all_negative_indices: List[int], unbounded_negative_indices: List[int],
                           negative_index_to_tree_plan_node: Dict[int, TreePlanNode],
                           negative_index_to_tree_plan_cost: Dict[int, float]):
        args = pattern.get_top_level_structure_args()
        positive_events = pattern.get_top_level_structure_args(True, False)
        for i, negative_index in enumerate(all_negative_indices):
            is_unbounded = negative_index in unbounded_negative_indices
            negation_operator_structure = args[negative_index]
            negation_operator_arg = negation_operator_structure.arg
            if negative_index in negative_index_to_tree_plan_node:
                # a negation operator hiding a nested structure
                if not isinstance(negation_operator_arg, CompositeStructure) and \
                        not isinstance(negation_operator_arg, UnaryStructure):
                    raise Exception("Unexpected nested structure inside a negation operator")
                nested_node = negative_index_to_tree_plan_node[negative_index]
                if isinstance(nested_node, TreePlanUnaryNode):
                    node_under_negation = nested_node
                    node_under_negation.index = negative_index
                    if isinstance(node_under_negation.child, TreePlanNestedNode):
                        node_under_negation.child.nested_event_index = negative_index
                else:
                    nested_node_cost = negative_index_to_tree_plan_cost[negative_index]
                    nested_node_args = negation_operator_arg.args \
                        if isinstance(negation_operator_arg, CompositeStructure) \
                        else [negation_operator_arg.arg]
                    node_under_negation = TreePlanNestedNode(negative_index, nested_node,
                                                             nested_node_args, nested_node_cost)
            else:
                # a flat negation operator
                temp_leaf_index = len(pattern.positive_structure.args) + i
                node_under_negation = TreePlanLeafNode(temp_leaf_index,
                                                       negation_operator_arg.type, negation_operator_arg.name)
            # get coi of negation node
            conditions =  pattern.condition.extract_atomic_conditions()
            negation_coi = {negation_operator_arg.name}
            for cond in conditions:
                if negation_operator_arg.name in cond.get_event_names():
                    negation_coi.update(cond.get_event_names())
            negation_coi.remove(negation_operator_arg.name)

            # get index of the lowest position and the name of lowest position node
            lowest_node_name = ""
            lowest_index = 0
            for i, event in enumerate(positive_events):
                names = event.get_all_event_names()
                if names[0] in negation_coi:
                    lowest_node_name = names[0]
                    lowest_index = i
            positive_events.insert(lowest_index, negation_operator_arg)

            #update all nodes indexes
            tree_nodes = positive_tree_plan.get_leaves()
            node_under_negation.event_index = lowest_index
            for tree_node in tree_nodes:
                if tree_node.event_index >= lowest_index:
                    tree_node.event_index = tree_node.event_index + 1

            # insert the node to it's right place
            if lowest_node_name == "":
                #if it can be the first node we will put it first
                positive_tree_plan = NegationAlgorithm._instantiate_negative_node(pattern, node_under_negation,
                                                                                  positive_tree_plan, is_unbounded)
            else:
                # we want to insert the node next to his lastname
                self._add_negative_part_in_position(pattern, positive_tree_plan, node_under_negation, lowest_index,
                                                    lowest_node_name, is_unbounded)
        return positive_tree_plan

"""
This file contains the default parameter values for various system configuration settings.
Each of the values below can be overridden by providing a different value in CEP.__init__ or CEP.run.
"""
from evaluation.EvaluationMechanismTypes import EvaluationMechanismTypes
from misc.SelectionStrategies import SelectionStrategies
from parallel.ParallelExecutionModes import ParallelExecutionModes
from parallel.ParallelExecutionPlatforms import ParallelExecutionPlatforms
from plan.IterativeImprovement import IterativeImprovementType, IterativeImprovementInitType
from plan.multi.MultiPatternEvaluationApproaches import MultiPatternEvaluationApproaches
from plan.TreeCostModels import TreeCostModels
from plan.TreePlanBuilderTypes import TreePlanBuilderTypes


# general settings
DEFAULT_EVALUATION_MECHANISM_TYPE = EvaluationMechanismTypes.TREE_BASED

# plan generation-related defaults
DEFAULT_TREE_PLAN_BUILDER = TreePlanBuilderTypes.TRIVIAL_LEFT_DEEP_TREE
DEFAULT_TREE_COST_MODEL = TreeCostModels.INTERMEDIATE_RESULTS_TREE_COST_MODEL

# default selection strategies
PRIMARY_SELECTION_STRATEGY = SelectionStrategies.MATCH_ANY
SECONDARY_SELECTION_STRATEGY = SelectionStrategies.MATCH_SINGLE

# tree storage settings
SHOULD_SORT_STORAGE = False
CLEANUP_INTERVAL = 10  # the default number of pattern match additions between subsequent storage cleanups
PRIORITIZE_SORTING_BY_TIMESTAMP = True

# iterative improvement defaults
ITERATIVE_IMPROVEMENT_TYPE = IterativeImprovementType.SWAP_BASED
ITERATIVE_IMPROVEMENT_INIT_TYPE = IterativeImprovementInitType.RANDOM

# multi-pattern optimization defaults
MULTI_PATTERN_APPROACH = MultiPatternEvaluationApproaches.TRIVIAL_SHARING_LEAVES

# parallel execution settings
DEFAULT_PARALLEL_EXECUTION_MODE = ParallelExecutionModes.SEQUENTIAL
DEFAULT_PARALLEL_EXECUTION_PLATFORM = ParallelExecutionPlatforms.THREADING

# kleene closure limit constrains
KC_MIN_SIZE = 1
KC_MAX_SIZE = None

# active pattern transformation for nested rules
EXPAND_PATTERN_AND_AND = True
EXPAND_PATTERN_SEQ_OR = True
EXPAND_PATTERN_SEQ_NOT_AND = True

# pattern transformation rules priority (lower number denotes a higher priority)
PRIORITY_PATTERN_TRANSFORMATION_MAX = -999
PRIORITY_PATTERN_TRANSFORMATION_MIN = 999
# PRIORITY_PATTERN_AND_AND = 1
# PRIORITY_PATTERN_SEQ_OR = 2
# PRIORITY_PATTERN_SEQ_NOT_AND = 3
PRIORITY_PATTERN_TRANSFORMATION = {
    "AND_AND" : 1,
    "SEQ_OR" : 2,
    "SEQ_NOT_AND" : 3 }


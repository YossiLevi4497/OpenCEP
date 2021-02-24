"""
This file contains the default parameter values for various system configuration settings.
Each of the values below can be overridden by providing a different value in CEP.__init__ or CEP.run.
"""
from datetime import timedelta

from evaluation.EvaluationMechanismTypes import EvaluationMechanismTypes
from misc.SelectionStrategies import SelectionStrategies
from misc.StatisticsTypes import StatisticsTypes
from misc.OptimizerTypes import OptimizerTypes
from misc.TreeEvaluationMechanismTypes import TreeEvaluationMechanismTypes
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

# statistics collection settings
DEFAULT_STATISTICS_COLLECTOR_TYPE = StatisticsTypes.ARRIVAL_RATES
TIME_WINDOW = timedelta(minutes=2)  # the default time window for The time when we are ready to keep statistics

# Optimizer settings
DEFAULT_OPTIMIZER_TYPE = OptimizerTypes.TRIVIAL
THRESHOLD = 0.5  # the default threshold for statistics changer aware optimizer

# statistics settings
DEFAULT_STATISTICS_TYPE = [StatisticsTypes.ARRIVAL_RATES]

# Tree Evaluation Mechanism settings
DEFAULT_TREE_EVALUATION_MECHANISM_TYPE = TreeEvaluationMechanismTypes.TRIVIAL_TREE_EVALUATION
STATISTICS_UPDATES_TIME_WINDOW = timedelta(seconds=5)  # the default time window for the time when the evaluation ready to get statistics

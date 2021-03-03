from abc import ABC, abstractmethod
from typing import List


class DeviationAwareTester(ABC):
    """
    Abstract class for deviation aware testing function
    """
    def __init__(self, t: float):
        self._t = t

    @abstractmethod
    def is_deviated_by_t(self, new_statistics, prev_statistics):
        """
       Checks if there was a deviation in one of the statistics by a factor of t.
       """
        raise NotImplementedError()


class ArrivalRatesDeviationAwareTester(DeviationAwareTester):
    """
    Checks for deviations in the arrival rates statistics by a factor of t.
    """

    def is_deviated_by_t(self, new_statistics: List[int], prev_statistics: List[int]):

        for i in range(len(new_statistics)):
            if prev_statistics[i] * (1 + self._t) < new_statistics[i] or \
                    prev_statistics[i] * (1 - self._t) > new_statistics[i]:
                return True
        return False


class SelectivityDeviationAwareOptimizerTester(DeviationAwareTester):
    """
    Checks for deviations in the selectivity matrix statistics by a factor of t.
    """

    def is_deviated_by_t(self, new_statistics: List[List[float]], prev_statistics: List[List[float]]):

        for i in range(len(new_statistics)):
            for j in range(i+1):
                if prev_statistics[i][j] * (1 + self._t) < new_statistics[i][j] or \
                        prev_statistics[i][j] * (1 - self._t) > new_statistics[i][j]:
                    return True
        return False


from abc import ABC, abstractmethod
from collections import deque
from sys import float_info


from heapq import heappush, heappop


class PriorityElement:
    def __init__(self, element, score):
        self.value = element
        self.score = score
        self.removed = False

    def __lt__(self, other):
        return self.score < other.score


def _pass_through_key(x):
    return x


class PriorityQueue:
    def __init__(self, items=None, key=None):
        self._dict = {}
        self._heap = []

        if key is None:
            key = _pass_through_key

        self._key = key

        if items:
            for item in items:
                self.add(item)

    def __bool__(self):
        return bool(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def add(self, item):
        if item in self._dict:
            raise ValueError(f"{item} already in queue")

        element = PriorityElement(item, self._key(item))
        self._dict[item] = element
        heappush(self._heap, element)

    def pop(self):
        while True:
            element = heappop(self._heap)

            if not element.removed:
                element.removed = True
                value = element.value
                del self._dict[value]
                return value

    def remove(self, item):
        element = self._dict.pop(item)
        element.removed = True


class PathNotFoundException(Exception):
    pass


class AStarAlgorithm(ABC):
    @abstractmethod
    def get_neighbours(self, node):
        raise NotImplementedError

    @abstractmethod
    def get_g_score(self, current, node):
        raise NotImplementedError

    @abstractmethod
    def get_h_score(self, node):
        raise NotImplementedError

    def find_path(self, start, end):
        g_scores = {start: 0}
        f_scores = {start: self.get_h_score(start)}
        parents = {}

        candidates = PriorityQueue([start], key=f_scores.__getitem__)
        rejects = set()

        i = 0
        while candidates:
            current = candidates.pop()
            i += 1

            if self.is_finished(current, end, parents):
                return self.reconstruct_path(current, end, parents)

            rejects.add(current)

            for neighbour in self.get_neighbours(current):
                if neighbour in rejects:
                    continue

                tentative_g_score = g_scores[current] + self.get_g_score(
                    current, neighbour
                )
                tentative_is_better = tentative_g_score < g_scores.get(
                    neighbour, float_info.max
                )

                if neighbour in candidates and not tentative_is_better:
                    continue

                parents[neighbour] = current
                g_scores[neighbour] = tentative_g_score
                f_scores[neighbour] = tentative_g_score + self.get_h_score(neighbour)

                candidates.add(neighbour)

        raise PathNotFoundException("Couldn't find path for given nodes")

    @abstractmethod
    def is_finished(self, node, goal, parents):
        raise NotImplementedError

    def reconstruct_path(self, node, goal, parents):
        result = deque((node,))

        while True:
            try:
                node = parents[node]
            except KeyError:
                break
            result.appendleft(node)

        return result

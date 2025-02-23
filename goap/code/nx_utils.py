from __future__ import absolute_import
from __future__ import unicode_literals


class OperationFailedError(Exception):
    def __init__(self, reason):
        self.msg = reason


class SensorError(Exception):
    """Sensor's Error base class"""


class SensorMultipleTypeError(SensorError):
    """Sensor can not be two type at once"""


class SensorDoesNotExistError(SensorError):
    """Sensor do not exist"""


class SensorAlreadyInCollectionError(SensorError):
    """Sensor do not exist"""


class PlanError(Exception):
    """Generic plan error"""


class PlanFailed(PlanError):
    """Failed to produce a plan"""


class ActionError(Exception):
    """Action's Error base class"""


class ActionMultipleTypeError(ActionError):
    """Action cannot be two types at once"""


class ActionAlreadyInCollectionError(ActionError):
    """Action with same name already in collection"""


from typing import Callable, List, Optional


class NXAction:
    """The Action class defines the interface used by the planner
        to convert the actions into graph node's edges
    func: Callable, a function or callable object
    name: Action name used as ID
    conditions: the world state condition required for
                this action to be executed
    effect: what is the expected world state after the action execution
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        conditions: dict,
        effects: dict,
        cost: float = 0.1,
    ):
        self.func = func
        self.name = name
        self.conditions = conditions
        self.effects = effects
        self.cost = cost
        self._response: Optional[NXActionResponse] = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        if len(self.__dict__) < len(other.__dict__):
            return -1
        elif len(self.__dict__) > len(other.__dict__):
            return 1
        else:
            return 0

    def __hash__(self):
        return hash(self)

    def __call__(self):
        return self.exec()

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    def exec(self):
        try:
            stdout, stderr, return_code = self.func()
        except RuntimeError as e:
            raise RuntimeError(f"Error executing function {self.func}. Exception: {e}")
        self.response = NXActionResponse(
            stdout=stdout, stderr=stderr, return_code=return_code
        )
        return self.response


class NXActionResponse:
    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
        trim_chars: str = "\r\n",
    ):
        """

        :param return_code:
        :param stdout:
        :param stderr:
        """
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.trim_chars = trim_chars
        self.response = None

    def __call__(self):
        return self.response

    def __str__(self):
        return f"{self.response}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def __trim(string: str):
        return string.strip("\r\n")

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, value: str):
        self._stdout = self.__trim(value)

    @property
    def stderr(self):
        return self._stderr

    @stderr.setter
    def stderr(self, value: str):
        self._stderr = self.__trim(value)

    @property
    def return_code(self):
        return self._return_code

    @return_code.setter
    def return_code(self, value: int):
        self._return_code = value

    @property
    def response(self):
        if self.stdout:
            return self.stdout
        elif self.stderr:
            return self.stderr

    @response.setter
    def response(self, value):
        self._response = value


class NXActions:

    def __init__(self, actions: List[NXAction] = None):
        self.actions = actions if actions else []

    def __str__(self):
        names = [action.name for action in self.actions]
        return "{}".format(names)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.actions)

    def __len__(self):
        if self.actions:
            return len(self.actions)
        else:
            return 0

    def __getitem__(self, key: str) -> Optional[NXAction]:
        for action in self.actions:
            if action.name == key:
                return action
            else:
                return None

    def get(self, name: str) -> Optional[NXAction]:
        result = None
        if not self.actions:
            return result

        for action in self.actions:
            if action.name == name:
                result = action

        return result

    def get_by_conditions(self, conditions: dict) -> Optional[List[NXAction]]:
        result = []
        for action in self.actions:
            if action.conditions == conditions:
                result.append(action)
        return result

    def get_by_effects(self, effects: dict) -> Optional[List[NXAction]]:
        result = []
        for action in self.actions:
            if action.effects == effects:
                result.append(action)
        return result

    def add(
        self,
        name: str,
        conditions: dict,
        effects: dict,
        func: Callable,
        cost: float = 0.1,
    ):
        if self.get(name):
            raise ActionAlreadyInCollectionError(
                f"The action name {name} is already in use"
            )
        self.actions.append(NXAction(func, name, conditions, effects, cost))

    def remove(self, name: str):
        result = False
        if not self.actions:
            return result
        action = self.get(name)
        if action:
            self.actions.remove(action)
            result = True
        return result

    def run_all(self) -> list:
        responses = [action.exec() for action in self.actions]
        return responses

    @staticmethod
    def compare_actions(action1: NXAction, action2: NXAction) -> bool:
        result = False
        if (
            action1.conditions == action2.conditions
            and action1.effects == action2.effects
        ):
            result = True

        return result


import networkx as nx


class Node(object):

    def __init__(self, attributes: dict, weight: float = 0.0):
        self.attributes = attributes
        self.weight = weight
        self.name = str(self.attributes)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Edge(object):

    def __init__(
        self,
        name,
        predecessor: Node,
        successor: Node,
        cost: float = 0.0,
        obj: object = None,
    ):
        self.name = name
        self.cost = cost
        self.predecessor = predecessor
        self.successor = successor
        self.obj = obj

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class Nodes(object):

    def __init__(self):
        self.nodes = []

    def __add__(self, other: Node):
        self.nodes.append(other)

    def __iter__(self):
        return iter(self.nodes)

    def add(self, other: Node):
        if other not in self.nodes:
            self.__add__(other)

    def get(self, attr):
        result = None
        for node in self.nodes:
            if node.attributes == attr:
                result = node
        return result


class Edges(object):

    def __init__(self, edges: list = None):
        if edges:
            for edge in edges:
                self.add(edge)
        else:
            self.edges = []

    def __add__(self, other: Edge):
        self.edges.append(other)

    def __iter__(self):
        return iter(self.edges)

    def add(self, other: Edge):
        self.__add__(other)


class Graph(object):
    def __init__(self, nodes: Nodes, edges: Edges):
        self.directed = nx.DiGraph()
        self.add_nodes_from(nodes=nodes)
        self.add_edges_from(edges=edges)
        self.__size = self.size

    def __repr__(self):
        return self.directed

    @staticmethod
    def __is_dst(src: dict, dst: dict) -> bool:
        if src == dst:
            return True
        else:
            return False

    @property
    def size(self):
        return len(self.directed.nodes)

    def __add_node(self, node: Node, attribute: dict):
        self.directed.add_node(node, attr_dict=attribute, label=node.name, object=node)

    def __add_edge(self, edge: Edge):
        self.directed.add_edge(
            edge.predecessor,
            edge.successor,
            object=edge.obj,
            weight=edge.cost,
            label=edge.name,
        )

    def add_nodes_from(self, nodes: Nodes):
        [self.__add_node(node, attribute=node.attributes) for node in nodes]

    def add_edges_from(self, edges: Edges):
        [self.__add_edge(edge=edge) for edge in edges]

    def edge_between_nodes(self, path: list, data: bool = True):
        return self.directed.edges(path, data=data)

    def nodes(self, data: bool = True):
        return self.directed.nodes(data=data)

    def edges(self, data: bool = True):
        return self.directed.edges(data=data)

    def search_node(self, attr: dict = None):
        result = None
        if attr:
            for node in self.directed.nodes(data=True):
                if node[1]["attr_dict"].items() == attr.items():
                    result = node[0]
        return result

    def path(self, src: dict, dst: dict):
        if not self.__is_dst(src, dst):
            # self.plot("graph.png")
            # print(self.directed)
            return nx.astar_path(self.directed, src, dst, weight="weight")

    def plot(self, file_path: str):
        try:
            import matplotlib.pyplot as plt
        except ImportError as err:
            raise ImportError(f"matplotlib not installed. Failed at: {err}")

        try:
            pos = nx.nx_agraph.graphviz_layout(self.directed)
            nx.draw(
                self.directed,
                pos=pos,
                node_size=1200,
                node_color="lightblue",
                linewidths=0.25,
                font_size=8,
                font_weight="bold",
                with_labels=True,
                # dpi=5000,
            )
            # edge_labels = nx.get_edge_attributes(self.directed, name='attr_dict')
            # nx.draw_networkx_edge_labels(self.directed, pos=pos, edge_labels=edge_labels)
            plt.savefig(file_path)
        except IOError as err:
            raise IOError(f"Could not create plot image: {err}")



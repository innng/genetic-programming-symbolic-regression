import parameters
from math import cos
from math import sin
from math import sqrt
from math import log
from copy import deepcopy
from random import random
from random import randint
from random import uniform


# ----------------------- MAIN METHODS ------------------------ #
class Node:
    def __init__(self, nodeType=None, nodeKey=None, nodeDepth=0, nodeLeft=None, nodeRight=None):
        self.type = nodeType
        self.key = nodeKey
        self.depth = nodeDepth
        self.left = nodeLeft
        self.right = nodeRight


class Individual:
    def __init__(self):
        self.tree = _buildTree()
        self.fitness = _fitness(self)
        self.depth = _depth(self.tree)


def _buildTree(nodeDepth=parameters.MIN_DEPTH_TREE):
    # select type
    selected = newSelection(nodeDepth)
    nodeType = parameters.NODE_TYPE[selected]

    # select key based on type
    if nodeType is 'variable':
        selected = variableSelection()
        nodeKey = parameters.VARIABLES[selected]
    elif nodeType is 'constant':
        nodeKey = constantSelection()
    else:
        selected = operatorSelection()
        nodeKey = parameters.OPERATORS[selected]

    # create new node
    new = Node(nodeType, nodeKey, nodeDepth)

    # treat node's children
    if nodeType is 'operator':
        if nodeKey is 'log':
            new.left = None
            new.right = _buildTree(nodeDepth=(nodeDepth + 1))
        else:
            new.left = _buildTree(nodeDepth=(nodeDepth + 1))
            new.right = _buildTree(nodeDepth=(nodeDepth + 1))

    # return new subtree
    return new


def _fitness(ind):
    # initialize sum variable
    value = 0

    # sum (expression - y) for all dataset
    for i in range(0, parameters.MAX_ROW):
        value += round(pow(expressionEval(ind.tree, parameters.DATASET[i]) - float(parameters.DATASET[i][-1]), 2), parameters.PRECISION_DIGITS)

    # finish calculating the whole formula
    result = round(sqrt(value / parameters.MAX_ROW), parameters.PRECISION_DIGITS)

    # return fitness
    return result


def _depth(tree, depth=-1):
    # choose the greater value between the paths on the tree
    if tree is None:
        return depth
    else:
        return max(_depth(tree.left, depth + 1), _depth(tree.right, depth + 1))


def _mutation(ind):
    # select depth where the mutation is going to occur
    chosen = depthSelection()

    # adjust selected depth based on the tree's depth
    selectedDepth = adjustDepth(ind.depth, chosen)

    # select a node in the given depth
    node = nodeSelection(ind, selectedDepth)

    # create new subtree based on the node's father
    growTree(ind, node)

    # update individual's attributes
    ind.depth = _depth(ind.tree)
    ind.fitness = _fitness(ind)


def _crossover(ind1, ind2):
    # create a copy of each individual
    new1 = deepcopy(ind1)
    new2 = deepcopy(ind2)

    # choose a depth where the trees can crossover
    chosen = depthSelection()

    # adjust selected depth based on the trees' depth
    selectedDepth1 = adjustDepth(new1.depth, chosen)
    selectedDepth2 = adjustDepth(new2.depth, chosen)

    # select two nodes from each individual
    node1 = deepcopy(nodeSelection(new1, selectedDepth1))
    node2 = deepcopy(nodeSelection(new2, selectedDepth2))

    # cross the subtrees
    changeSubTree(new1, node1, node2)
    changeSubTree(new2, node2, node1)

    # calculate children's attributes
    new1.depth = _depth(new1.tree)
    new1.fitness = _fitness(new1)
    new2.depth = _depth(new2.tree)
    new2.fitness = _fitness(new2)

    # return the new individuals
    result = [new1, new2]
    return result


# --------------------- AUXILIAR METHODS ---------------------- #
def newSelection(nodeDepth=parameters.MIN_DEPTH_TREE):
    if nodeDepth == parameters.MIN_DEPTH_TREE:
        selected = 0

    # if the current node is the root or a inner node
    elif nodeDepth < parameters.MAX_DEPTH_TREE:
        selected = innerNodeSelection()

    # if the current node is a leaf
    elif nodeDepth >= parameters.MAX_DEPTH_TREE:
        selected = randint(1, 2)

    # return type selection based on the position of the node
    return selected


def variableSelection():
    # choose a variable between the variables accepted (info extracted from dataset)
    selected = randint(0, parameters.MAX_VAR - 1)
    return selected


def constantSelection():
    # select a constant between a minimum value and a maximum value, with defined number of digits after dot
    selected = round(uniform(parameters.MIN_VALUE_CONSTANT, parameters.MAX_VALUE_CONSTANT), parameters.PRECISION_DIGITS)
    return selected


def operatorSelection():
    # choose an operand between the ones avaliable for this execution
    selected = randint(0, parameters.MAX_OPERATORS - 1)
    return selected


def innerNodeSelection():
    # with the intention of expanding the individuals created theres a 30% chance of cutting the tree in the current node
    # else the tree expand with another operator
    leaf = random()
    if leaf >= parameters.PROB_NOT_LEAF:
        selected = randint(0, 2)
    else:
        selected = 0
    return selected


def traverse(ind):
    # algorithm to print the tree of an individual
    # based on the BFS traversal, which permit walking on the tree level-by-level
    thisLevel = [ind.tree]
    while thisLevel:
        nextLevel = list()
        for n in thisLevel:
            print(n.key, end=" ")
            if n.left:
                nextLevel.append(n.left)
            if n.right:
                nextLevel.append(n.right)
        print('\n')
        thisLevel = nextLevel


def expressionEval(tree, varList):
    # evaluate a given expression tree
    if tree is None:
        value = round(0)
        return value

    # the current node is a leaf:
    # 1. if its a variable, search for the respective value on the variable list
    # 2. if its a constant, return its value
    if tree.left is None and tree.right is None:
        if tree.type is 'variable':
            index = parameters.VARIABLES.index(tree.key)
            value = round(float(varList[index]), parameters.PRECISION_DIGITS)
        else:
            value = round(tree.key, parameters.PRECISION_DIGITS)
        return value

    # to evaluate subtrees must use recursion
    left_sum = expressionEval(tree.left, varList)
    right_sum = expressionEval(tree.right, varList)

    # after evaluating the subtrees, the algorithm step in the father node (an operator) and calculate the expression
    # formed by the operator and the results of the subtress
    if tree.key is '+':
        value = round(left_sum + right_sum, parameters.PRECISION_DIGITS)
        return value
    elif tree.key is '-':
        value = round(left_sum - right_sum, parameters.PRECISION_DIGITS)
        return value
    elif tree.key is '*':
        value = round(left_sum * right_sum, parameters.PRECISION_DIGITS)
        return value
    elif tree.key is '/':
        # definition: if is going to be a division by zero, the value is defined as zero
        if right_sum == 0:
            value = round(0)
            return value
        else:
            value = round(left_sum / right_sum, parameters.PRECISION_DIGITS)
            return value
    elif tree.key is 'log':
        if right_sum <= 0:
            value = 0
        else:
            value = round(log(right_sum))
        return value


def depthSelection(treeDepth=parameters.MIN_DEPTH_TREE):
    # choose a depth between the minimum and maximum
    selected = randint(parameters.MIN_DEPTH_TREE + 1, parameters.MAX_DEPTH_TREE)
    return selected


def adjustDepth(treeDepth, givenDepth):
    depth = 0

    # case 1: the tree is a root
    if givenDepth == 0:
        depth = 0

    # case 2: the tree doesn't have the givenDepth
    elif givenDepth > treeDepth and treeDepth != 0:
        depth = givenDepth % treeDepth
        if depth == 0:
            depth += 1

    # case 2: givenDepth exists in the tree
    elif givenDepth <= treeDepth:
        depth = givenDepth

    # return the chosen depth
    return depth


def nodeSelection(ind, depth):
    # algorithm to choose a node of an individual
    # based on the BFS traversal, which permit walking on the tree level-by-level
    if ind.tree.depth == depth:
        selected = ind.tree
        return selected

    thisLevel = [ind.tree]
    while thisLevel:

        if thisLevel[0].depth == depth:
            chosen = randint(0, len(thisLevel) - 1)
            selected = thisLevel[chosen]
            return selected

        nextLevel = list()
        for n in thisLevel:
            if n.left:
                nextLevel.append(n.left)
            if n.right:
                nextLevel.append(n.right)
        thisLevel = nextLevel


def growTree(ind, node):
    # algorithm to grow a randomic subtree in an individual
    # based on the BFS traversal, which permit walking on the tree level-by-level
    # case 1: if the selected node is the root
    if ind.tree == node:
        ind.tree = _buildTree(nodeDepth=(ind.tree.depth + 1))
        return

    # if it's not the root, start the BFS algorithm
    thisLevel = [ind.tree]
    while thisLevel:
        nextLevel = list()
        for n in thisLevel:
            if n.left:
                if n.left == node:
                    n.left = _buildTree(nodeDepth=(n.depth + 1))
                    return
                else:
                    nextLevel.append(n.left)
            if n.right:
                if n.right == node:
                    n.right = _buildTree(nodeDepth=(n.depth + 1))
                    return
                else:
                    nextLevel.append(n.right)
        thisLevel = nextLevel


def changeSubTree(ind, oldSubTree, newSubTree):
    # algorithm to change a subtree of an individual
    # based on the BFS traversal, which permit walking on the tree level-by-level
    # case 1: if the selected node is the root
    if ind.tree == oldSubTree:
        ind.tree = newSubTree
        return

    # if it's not the root, start the BFS algorithm
    thisLevel = [ind.tree]
    while thisLevel:
        nextLevel = list()
        for n in thisLevel:
            if n.left:
                if n.left == oldSubTree:
                    n.left = newSubTree
                    return
                else:
                    nextLevel.append(n.left)
            if n.right:
                if n.right == oldSubTree:
                    n.right = newSubTree
                    return
                else:
                    nextLevel.append(n.right)
        thisLevel = nextLevel

import parameters
import individual
import csv
from copy import deepcopy
from random import random
from random import randint


# ----------------------- MAIN METHODS ------------------------ #
def _initialPopulation():
    # create the initial population
    new = []
    for i in range(0, parameters.INITIAL_POPULATION):
        i = individual.Individual()
        new.append(i)
    return new


def _tournamentSelection(population):
    selected = []

    # adjust the tournamente size
    if parameters.TOURNAMENT_SIZE < len(population):
        size = parameters.TOURNAMENT_SIZE
    else:
        size = len(population)

    # choose individuals for the tournament
    for i in range(0, size):
        index = randint(0, len(population) - 1)
        selected.append(population[index])

    # select the winner by choosing the minimum fitness
    winner = min(selected, key=lambda x: x.fitness)
    return winner


def _runGeneration(oldPopulation):
    newPopulation = []

    # select elitism individuals and add in the new population
    for i in range(0, parameters.ELITISM):
        best = min(oldPopulation, key=lambda x: x.fitness)
        newPopulation.append(deepcopy(best))

    # if population exceed the maximum size, select at random individuals and remove then
    if len(oldPopulation) > parameters.MAX_POPULATION:
        diff = len(oldPopulation) - parameters.MAX_POPULATION
        for i in range(parameters.ELITISM + 1, diff):
            worst = max(oldPopulation, key=lambda x: x.fitness)
            oldPopulation.remove(worst)

    children = []
    while oldPopulation:
        # check if two tournaments can be made
        # case 1: make two tournaments to select the local best individual and remove it from old population
        if len(oldPopulation) >= 2:
            ind1 = _tournamentSelection(oldPopulation)
            oldPopulation.remove(ind1)

            ind2 = _tournamentSelection(oldPopulation)
            oldPopulation.remove(ind2)

            # choose whether cross the two selected individuals
            _random = random()
            if _random <= parameters.PROB_CROSSOVER:
                # make the crossover
                children = individual._crossover(ind1, ind2)

            # crossover didn't happen: pass the parents
            else:
                parents = [ind1, ind2]
                winner = _tournamentSelection(parents)
                children.append(winner)

        # case 2: if just one individual was left, pass it
        else:
            children.append(oldPopulation[0])
            oldPopulation.pop()

    # choose whether mutate the new individuals generated
    for i in range(0, len(children)):
        _random = random()
        if _random <= parameters.PROB_MUTATION:
            individual._mutation(children[i])

    # insert the new individuals in the new population
    newPopulation += children

    # return new population
    return newPopulation


def _runExecution():
    # set the parameters that are not free (depends on others parameters or attributes)
    setParameters()

    # take info from file .csv
    readCSV()

    # start a randomic population
    population = []
    population = _initialPopulation()

    # initialize the number of generation the algorithm is going to be executed (if its a train, gen = max generation)
    gen = parameters.MAX_GENERATION

    # for every generation, run the algorithm
    for i in range(0, parameters.MAX_GENERATION):
        print("generation ", i)
        population = _runGeneration(population)

        # set the logs of population
        setLogResultsGeneration(population)

        parameters.AVERAGE_BEST_GEN[i] = round(parameters.AVERAGE_BEST_GEN[i] + parameters.BEST_FITNESS_GEN[i], parameters.PRECISION_DIGITS)
        parameters.AVERAGE_MEAN_GEN[i] = round(parameters.AVERAGE_MEAN_GEN[i] + parameters.MEAN_FITNESS_GEN[i], parameters.PRECISION_DIGITS)
        parameters.AVERAGE_WORST_GEN[i] = round(parameters.AVERAGE_WORST_GEN[i] + parameters.WORST_FITNESS_GEN[i], parameters.PRECISION_DIGITS)

        # check if the execution is for training or testing
        if parameters.TYPE is "test":
            if parameters.BEST_FITNESS_GEN[i] <= parameters.MIN_OPTIMAL_SOL:
                gen = i
                break
    return gen


def _main():
    for i in range(0, parameters.MAX_GENERATION):
        parameters.AVERAGE_BEST_GEN.append(round(0, parameters.PRECISION_DIGITS))
        parameters.AVERAGE_MEAN_GEN.append(round(0, parameters.PRECISION_DIGITS))
        parameters.AVERAGE_WORST_GEN.append(round(0, parameters.PRECISION_DIGITS))

    # run executions
    for i in range(0, parameters.EXEC):
        print("executing ", i)
        gen = _runExecution()
        setLogResultsExecution(gen)

    for i in range(0, parameters.MAX_GENERATION):
        parameters.AVERAGE_BEST_GEN[i] = round(parameters.AVERAGE_BEST_GEN[i] / parameters.EXEC, parameters.PRECISION_DIGITS)
        parameters.AVERAGE_MEAN_GEN[i] = round(parameters.AVERAGE_MEAN_GEN[i] / parameters.EXEC, parameters.PRECISION_DIGITS)
        parameters.AVERAGE_WORST_GEN[i] = round(parameters.AVERAGE_WORST_GEN[i] / parameters.EXEC, parameters.PRECISION_DIGITS)

    # write the log file
    writeLog(gen)


# --------------------- AUXILIAR METHODS ---------------------- #
def setParameters():
    # set the parameters
    parameters.PROB_MUTATION = float(1) - parameters.PROB_CROSSOVER
    parameters.LOG_NAME = parameters.CSV_NAME + parameters.LOG_ADD
    # clean parameters
    parameters.BEST_FITNESS_GEN = []
    parameters.WORST_FITNESS_GEN = []
    parameters.MEAN_FITNESS_GEN = []


def readCSV():
    with open(parameters.CSV_DIR + parameters.CSV_NAME + parameters.EXT_CSV) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        parameters.DATASET = list(reader)
        parameters.MAX_ROW = len(parameters.DATASET)
        parameters.MAX_COL = len(parameters.DATASET[1])
        parameters.MAX_VAR = parameters.MAX_COL - 1


def writeLog(generation):
    writer = open(parameters.LOG_DIR + parameters.LOG_NAME + parameters.EXT_LOG, 'w')

    writer.write("parameters:\n")
    writer.write("population = {0: > 3}\tgenerations = {1: > 3}\n".format(parameters.MAX_POPULATION, parameters.MAX_GENERATION))
    writer.write("crossover prob = {0: > 3}\tmutation prob = {1: > 3}\n".format(parameters.PROB_CROSSOVER, parameters.PROB_MUTATION))
    writer.write("tournament size = {0: > 3}\telitism = {1: > 3}\n".format(parameters.TOURNAMENT_SIZE, parameters.ELITISM))
    writer.write("average best fitness = {0}\n".format(parameters.MEAN_BEST_FITNESS))
    writer.write("average mean fitness = {0}\n".format(parameters.MEAN_MEAN_FITNESS))
    writer.write("average worst fitness = {0}\n\n".format(parameters.MEAN_WORST_FITNESS))

    writer.write("exec / best / mean / worst\n")
    for i in range(0, parameters.EXEC):
        writer.write("{0: > 2} {1: > 20} {3: > 20} {3: > 20}\n".format(i, parameters.BEST_FITNESS_EXEC[i], parameters.MEAN_FITNESS_EXEC[i], parameters.WORST_FITNESS_EXEC[i]))
    writer.write("\n\n")

    writer.write("gen / best / mean / worst\n")
    for i in range(0, generation):
        writer.write("{0: > 2} {1: > 20} {3: > 20} {3: > 20}\n".format(i, parameters.AVERAGE_BEST_GEN[i], parameters.AVERAGE_MEAN_GEN[i], parameters.AVERAGE_WORST_GEN[i]))
    writer.write("\n")

    writer.close()


def getFitness(ind):
    return ind.fitness


def setLogResultsGeneration(population):
    # save the statistics in log for each generation
    # best fitness
    best = min(population, key=lambda x: x.fitness)
    best_fitness = best.fitness
    parameters.BEST_FITNESS_GEN.append(best_fitness)

    # worst fitness
    worst = max(population, key=lambda x: x.fitness)
    worst_fitness = worst.fitness
    parameters.WORST_FITNESS_GEN.append(worst_fitness)

    # mean fitness
    mean_fitness = (sum(ind.fitness for ind in population) / len(population))
    parameters.MEAN_FITNESS_GEN.append(mean_fitness)


def setLogResultsExecution(generation):
    # mean of the best fitness of each execution
    best = (sum(parameters.BEST_FITNESS_GEN) / generation)
    parameters.BEST_FITNESS_EXEC.append(best)

    # mean of the worst fitness of each generation
    worst = (sum(parameters.WORST_FITNESS_GEN) / generation)
    parameters.WORST_FITNESS_EXEC.append(worst)

    # mean of the mean fitness of each generation
    mean = (sum(parameters.MEAN_FITNESS_GEN) / generation)
    parameters.MEAN_FITNESS_EXEC.append(mean)

    # average best fitness from all executions
    parameters.MEAN_BEST_FITNESS = (sum(parameters.BEST_FITNESS_EXEC) / parameters.EXEC)

    # average worst fitness from all executions
    parameters.MEAN_WORST_FITNESS = (sum(parameters.WORST_FITNESS_EXEC) / parameters.EXEC)

    # average mean fitness from all executions
    parameters.MEAN_MEAN_FITNESS = (sum(parameters.MEAN_FITNESS_EXEC) / parameters.EXEC)


if __name__ == '__main__':
    _main()

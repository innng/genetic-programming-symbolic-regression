# --------------------------- FILES --------------------------- #
# names for log and dataset
CSV_NAME = "house-train"
CSV_DIR = "../datasets/"
LOG_ADD = "-prob6"
LOG_DIR = "../logs/"
EXT_LOG = ".dat"

LOG_NAME = ""
EXT_CSV = ".csv"

# -------------------- GENETIC PROGRAMMING -------------------- #
# free parameters used in algorithm
INITIAL_POPULATION = 5
MAX_POPULATION = 10
MAX_GENERATION = 100
PROB_CROSSOVER = 0.6
PROB_MUTATION = 0.3
TOURNAMENT_SIZE = 2
MIN_OPTIMAL_SOL = 0.2
ELITISM = 1
EXEC = 30
TYPE = "train"
MAX_DEPTH_TREE = 4

# -------------------------- VALUES --------------------------- #
# fixed/dependent parameters
MIN_DEPTH_TREE = 0
MIN_VALUE_CONSTANT = 0
MAX_VALUE_CONSTANT = 10
PRECISION_DIGITS = 5
MAX_OPERATORS = 5
PROB_NOT_LEAF = 0.6

# ---------------------- REPRESENTATIONS ---------------------- #
# important strings
NODE_TYPE = ['operator', 'variable', 'constant']
VARIABLES = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10']
OPERATORS = ['+', '-', '*', '/', 'log']

# -------------------------- DATASET -------------------------- #
# information taken from dataset
DATASET = []
MAX_ROW = 0
MAX_COL = 0
MAX_VAR = 0

# --------------------------- LOGS ---------------------------- #
# list of information from each generation
BEST_FITNESS_GEN = []
WORST_FITNESS_GEN = []
MEAN_FITNESS_GEN = []

# list of average fitness per generation
AVERAGE_BEST_GEN = []
AVERAGE_MEAN_GEN = []
AVERAGE_WORST_GEN = []

# list of information from each execution (average from generation)
BEST_FITNESS_EXEC = []
WORST_FITNESS_EXEC = []
MEAN_FITNESS_EXEC = []

# average information from executios
MEAN_BEST_FITNESS = 0
MEAN_WORST_FITNESS = 0
MEAN_MEAN_FITNESS = 0

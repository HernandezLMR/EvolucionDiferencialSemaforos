import re
import numpy as np
import random
import csv
import math

def parse_params(file_path):
    params = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Evaluate numbers, but keep expressions as strings
                try:
                    value = eval(value)
                except:
                    pass
                
                params[key] = value
    return params


def extract_variables(expression):
    # Define a list of known functions to exclude
    functions = {'sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'abs', 'math', 'pi'}  # Add any other functions you need
    # Find all alphabetic sequences that could be variables or functions
    all_identifiers = re.findall(r'[a-zA-Z_]\w*', expression)
    # Filter out any known functions
    variables = [var for var in all_identifiers if var not in functions]
    # Extract unique variables
    unique_variables = set(variables)
    return len(unique_variables)


def extract_individual(individual, VARNUM):
    var_names = ['x', 'y', 'z', 'w', 'u', 'v', 'a', 'b']
    variables = {var_names[i]: individual[i] for i in range(VARNUM)}
    return variables

def check_restrictions(RESTRICT, variables, INTER):
    valid = True
    # Check bounds
    for i, var in enumerate(variables):
        min_val, max_val = INTER[i]
        if variables[var] < min_val or variables[var] > max_val:
            return False
    #Check restrictions
    for restriction in RESTRICT:
        if not eval(restriction, {"math": math}, variables):
            valid = False
            break
    return valid

def create_population(VARNUM, PSIZE, RESTRICT, INTER):
    population = []
    for _ in range(PSIZE):
        while True:
            individual = []
            for i in range(VARNUM):
                min_bound, max_bound = INTER[i]
                # Generate a random number between MINB and MAXB
                value = random.uniform(min_bound, max_bound)
                individual.append(value)
            #Extract variables for evaluation (limit of 6 variables)
            var_names = ['x', 'y', 'z', 'w', 'u', 'v']
            variables = extract_individual(individual, VARNUM)
            #Check if individual clears all restrictions
            #If program crashes here check all words on config are lowercase
            valid = check_restrictions(RESTRICT, variables, INTER)
            #If all restrictions are met, add individual to population
            if valid:
                break
                
                        
        population.append(individual)
    return population

def process_ind(target, child, FUNCION, RESTRICT, OBJECTIVE, VARNUM, INTER):
    variablesC = extract_individual(child, VARNUM)
    #Check if child is valid
    child_valid = check_restrictions(RESTRICT,variablesC, INTER)
    if not child_valid:
        return False

    variablesT = extract_individual(target, VARNUM)

    child_value = eval(FUNCION, {"math": math}, variablesC)
    target_value = eval(FUNCION, {"math": math}, variablesT)

    win = (child_value > target_value) if OBJECTIVE == 'MAX' else (child_value < target_value)

    return win

def evaluate_fitness(individual, FUNCION):
    variables = extract_individual(individual, len(individual))
    return eval(FUNCION, {"math": math}, variables)


def main():
    #Get parameters from text file
    file_path = 'config.txt'
    parameters = parse_params(file_path)
    FM = parameters.get('FMUTACION')
    CR = parameters.get('CRECOMBINACION')
    FUNCION = parameters.get('FUNCION')
    NGEN = parameters.get('NGENERACIONES')
    PSIZE = parameters.get('TPOBLACION')
    INTER = parameters.get('INTERVALO')
    RESTRICT = parameters.get('RESTRICT')
    OBJECTIVE = parameters.get('OBJETIVO')

    #Get the number of variables
    VARNUM = extract_variables(FUNCION)
    #Open csv to log results
    with open('genetic_algorithm_log.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Generation', 'Individual', 'Fitness'])    
        #Create initial population
        population = create_population(VARNUM,PSIZE,RESTRICT,INTER)
        #print("Poblacion inicial")
        #print(population)

        for individual in population:
            fitness_value = evaluate_fitness(individual, FUNCION)
            writer.writerow(['Poblacion inicial', individual, fitness_value])
        


        #Main algorithm
        for n in range(NGEN):
            for i, target in enumerate(population):
                populationEX = [ind for j, ind in enumerate(population) if j != i]
                values = random.sample(populationEX, 3)
                child = np.add(values[0],(FM * (np.subtract(values[1],values[2]))))

                evaluate = random.uniform(-1, 1) <= CR
                if evaluate:
                    replace = process_ind(target, child, FUNCION, RESTRICT, OBJECTIVE, VARNUM, INTER)
                    if replace == True:
                        #print(f"Se reemplaza individuo {i} de valor {target} con nuevo valor {child}")
                        population[i] = child
            #print(f"Generacion {n}:")
            #print(population)

            for individual in population:
                fitness_value = evaluate_fitness(individual, FUNCION)
                writer.writerow([n, individual, fitness_value])

    minimun = 0
    best_individual = None
    for individual in population:
        value = evaluate_fitness(individual, FUNCION)
        if value < minimun:
            minimun = value
            best_individual = individual
    print(f"El valor minimo encontrado es: {minimun:.16f}")
    print(f"El individuo con el valor minimo es: {best_individual[0]:.16f} {best_individual[1]:.16f}")

                




if __name__ == "__main__":
    main()
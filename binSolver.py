from sympy import *

def eval_solution(concrete_solution):
    concrete_solution_eval = list(map(lambda x: 1 if x == 1 or x == 0 else 0,concrete_solution))
    aux = 0
    for i in concrete_solution_eval:
      aux += i
    if aux == len(concrete_solution):
        return True

    return False

def enumerate_solutions(Sols):
    if Sols.free_symbols == set(): # no free variables. see if all variables belong to {0,1}

        concrete_solution = Sols.args[0]
        if concrete_solution == set(): # no solutions
            return []
        if eval_solution(concrete_solution):
            return [concrete_solution]
        else:
            return []
    # create a list of tuples of free variables, one for each valid value
    free_vars = []
    for i in range(2**len(Sols.free_symbols)):
        free_vars.append(tuple(Sols.free_symbols))

    # generate values to substitute for free variables
    free_vals = [list(bin(i))[2:] for i in range(2**len(Sols.free_symbols))] 
    free_vals = [tuple(map(int, list('0'*(len(Sols.free_symbols)-len(s)))+s )) for s in free_vals] 

    # zip twice to generate lists of pairs of variable and value
    free_zip = zip(free_vars,free_vals)
    free_zip_fin = list([list( zip( x[0], x[1] )) for x in free_zip ] )

    correct_solutions = []

    for substitution in free_zip_fin:
        concrete_solution = list(map(lambda x: x.subs(substitution),Sols.args[0]))
        if eval_solution(concrete_solution):
            correct_solutions.append(concrete_solution)

    return correct_solutions

def solveSystem(equations,variables):
    res=linsolve(equations,variables)
    
    if len(res) == 0:
      return {}

    solutions = enumerate_solutions(res)

    buildSolution = {}

    for sol in solutions:
        for i,value in enumerate(sol):
            variable = variables[i]
            if not (variable in buildSolution):
                buildSolution[variable] = value
            else:
                if not(value == buildSolution[variable]):
                    buildSolution.pop(variable,None)
                    
    return buildSolution

if __name__ == '__main__':
    xa_1_2,xa_2_8,xa_1_8,xa_1_3,xa_3_8 = symbols('xa_1_2,xa_2_8,xa_1_8,xa_1_3,xa_3_8')

    variables = [xa_1_2,xa_2_8,xa_1_8,xa_1_3,xa_3_8]


    listEquations = [Eq(xa_1_2, 1), Eq(xa_1_8, 0), Eq(xa_2_8, 1), xa_1_2 + xa_1_3 + xa_2_8 - xa_3_8]

    print(solveSystem(listEquations,variables))

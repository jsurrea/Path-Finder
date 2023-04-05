import os
import json
from gurobipy import Model, GRB, quicksum

def read_data(path):
    """
    Lee el archivo de datos (.json) y devuelve los parámetros del problema
    """
    with open(path, "r") as file:
        data = json.load(file)
    
    r = data["r"]
    c = data["c"]
    I = data["I"]

    # Convierte los arreglos r,c indexables desde 1 (en lugar de 0)
    r = {(idx + 1) : i for idx, i in enumerate(r)}
    c = {(idx + 1) : j for idx, j in enumerate(c)}

    assert len(r) == len(c), "No hay igual número de filas y columnas"
    n = len(r)

    return n, r, c, I

def solve(n, r, c, I):
    """
    Resuelve el modelo general de encontrar un camino de rieles
    Parámetros:
        n: Número de filas/columnas del tablero
        r: Requerimiento de rieles por fila para 1 <= i <= n
        c: Requerimiento de rieles por columna para 1 <= j <= n
        I: Conjunto de rieles iniciales de la forma (i,j,k)
    Devuelve una matrix nxn con el tipo de riel que debe ir en cada posición
    """

    ########## MODELO ##########

    m = Model("RailPath")

    ######## CONJUNTOS #########

    F = {i for i in range(1, n+1)}
    C = {j for j in range(1, n+1)}
    T = {"A", "B", "C", "D", "E", "F"}
    D = {"Up", "Down", "Left", "Right"}

    ####### SUBCONJUNTOS #######

    Td = {
        "Up": {"A", "D", "F"},
        "Down": {"A", "C", "E"},
        "Left": {"B", "E", "F"},
        "Right": {"B", "C", "D"}
    }

    ######## VARIABLES #########

    x = m.addVars(F,C,T, vtype = GRB.BINARY, name = "x")

    ###### RESTRICCIONES #######

    # Requerimiento de rieles por fila
    for i in F:
        m.addConstr(
            quicksum(x[i,j,k] for j in C for k in T) == r[i]
        )

    # Requerimiento de rieles por columna
    for j in C:
        m.addConstr(
            quicksum(x[i,j,k] for i in F for k in T) == c[j]
        )

    # Máximo un riel por casilla
    for i in F:
        for j in C:
            m.addConstr(
                quicksum(x[i,j,k] for k in T) <= 1
            )

    # Los rieles cuyo tipo sea Up deben conectarse por arriba con uno tipo Down
    for k in Td["Up"]:
        for i in F:
            if i == 1:  # Excepto la primera fila
                continue
            for j in C:
                m.addConstr(
                    x[i,j,k] <= quicksum(x[i-1,j,k] for k in Td["Down"])
                )

    # Los rieles cuyo tipo sea Down deben conectarse por abajo con uno tipo "Up"
    for k in Td["Down"]:
        for i in F:
            if i == n:  # Excepto la última fila
                continue
            for j in C:
                m.addConstr(
                    x[i,j,k] <= quicksum(x[i+1,j,k] for k in Td["Up"])
                )

    # Los rieles cuyo tipo sea Left deben conectarse por la izquierda con uno tipo "Right"
    for k in Td["Left"]:
        for i in F:
            for j in C:
                if j == 1:  # Excepto la primera columna
                    continue
                m.addConstr(
                    x[i,j,k] <= quicksum(x[i,j-1,k] for k in Td["Right"])
                )

    # Los rieles cuyo tipo sea Right deben conectarse por la derecha con uno tipo "Left"
    for k in Td["Right"]:
        for i in F:
            for j in C:
                if j == n:  # Excepto la última columna
                    continue
                m.addConstr(
                    x[i,j,k] <= quicksum(x[i,j+1,k] for k in Td["Left"])
                )

    # Puede haber máximo dos salidas 
    m.addConstr(
        quicksum(x[1,j,k] for j in C for k in Td["Up"]) +
        quicksum(x[n,j,k] for j in C for k in Td["Down"]) +
        quicksum(x[i,1,k] for i in F for k in Td["Left"]) +
        quicksum(x[i,n,k] for i in F for k in Td["Right"]) <= 2
    )

    # Los rieles iniciales deben estar ubicados
    for (i,j,k) in I:
        m.addConstr(x[i,j,k] == 1)


    ##### FUNCIÓN OBJETIVO #####

    m.setObjective(0, GRB.MAXIMIZE)

    ######### SOLUCIÓN #########

    m.update()
    m.setParam('Outputflag', 0)
    m.optimize()

    # Crear la matriz resultado
    matrix = []

    for i in F:
        row = []
        for j in C:
            kind = "N"
            for k in T:
                if x[i,j,k].x > 0:
                    kind = k
                    break
            row.append(kind)
        matrix.append(row)

    return matrix


def print_results(path, matrix, r, c):
    """
    Imprime los resultados y los guarda en un archivo
    """

    # Añadir la información de requerimientos por fila/columna
    for i, row in enumerate(matrix, start = 1):
        row.append(r[i])
    matrix.append(list(c.values()))

    # Crear el string resultado
    string_matrix = [" ".join(map(str, row)) for row in matrix]
    string_results = "\n".join(string_matrix)
    print(string_results)

    # Guardar el archivo (.opti)
    with open(path, "w") as file:
        file.write(string_results)


if __name__ == "__main__":
    
    problems = ["Ejemplo", "ProblemA", "ProblemB", "ProblemC"]
    for path in problems:
        n, r, c, I = read_data(os.path.join("data", path + ".json"))
        matrix = solve(n, r, c, I)
        print(f"Resultados para el problema {path}:")
        print_results(os.path.join("solutions", path + ".opti"), matrix, r, c)
        print()

    print(f"Dirígase a la ruta {os.path.join(os.getcwd(), 'visualization', 'index.html')} en su navegador para visualizar los resultados :)")
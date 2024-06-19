import tkinter as tk
import numpy as np
import random

class Sudoku:
    def __init__(self, board):
        self.board = np.array(board)

    def is_valid(self, num, pos):
        for i in range(9):
            if self.board[pos[0], i] == num and pos[1] != i:
                return False
            if self.board[i, pos[1]] == num and pos[0] != i:
                return False

        box_x, box_y = pos[1] // 3, pos[0] // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i, j] == num and (i, j) != pos:
                    return False

        return True

class GASolver:
    def __init__(self, sudoku):
        self.sudoku = sudoku

    def fitness(self, board):
        row_score = sum(len(set(row)) for row in board)
        col_score = sum(len(set(board[:, col])) for col in range(9))
        box_score = 0
        for box_x in range(3):
            for box_y in range(3):
                box = board[box_x * 3:(box_x + 1) * 3, box_y * 3:(box_y + 1) * 3]
                box_score += len(set(box.flatten()))
        return row_score + col_score + box_score

    def selection(self, population, fitnesses):
        total_fitness = sum(fitnesses)
        probabilities = [fitness / total_fitness for fitness in fitnesses]
        selected = np.random.choice(len(population), size=2, p=probabilities)
        return population[selected[0]], population[selected[1]]

    def crossover(self, parent1, parent2):
        crossover_point = np.random.randint(1, 8)
        child = np.vstack((parent1[:crossover_point], parent2[crossover_point:]))
        return child

    def mutate(self, board):
        for i in range(9):
            if random.random() < 0.1:  # Mutation probability
                non_fixed_indices = [j for j in range(9) if self.sudoku.board[i, j] == 0]
                if len(non_fixed_indices) > 1:
                    idx1, idx2 = random.sample(non_fixed_indices, 2)
                    board[i, idx1], board[i, idx2] = board[i, idx2], board[i, idx1]
        return board

    def solve(self, max_generations=1000, population_size=100):
        population = [self.initialize_individual() for _ in range(population_size)]
        for generation in range(max_generations):
            fitnesses = np.array([self.fitness(ind) for ind in population])
            if np.max(fitnesses) == 243:  # 81 (rows) + 81 (columns) + 81 (subgrids)
                return population[np.argmax(fitnesses)]

            new_population = []
            for _ in range(population_size // 2):
                parent1, parent2 = self.selection(population, fitnesses)
                child1, child2 = self.crossover(parent1, parent2), self.crossover(parent2, parent1)
                new_population.extend([self.mutate(child1), self.mutate(child2)])

            population = new_population

        return population[np.argmax(fitnesses)]

    def initialize_individual(self):
        individual = np.copy(self.sudoku.board)
        for i in range(9):
            missing_nums = list(set(range(1, 10)) - set(individual[i]))
            random.shuffle(missing_nums)
            for j in range(9):
                if individual[i, j] == 0:
                    individual[i, j] = missing_nums.pop()
        return individual

class CSPSolver:
    def __init__(self, sudoku):
        self.sudoku = sudoku

    def is_valid(self, num, pos):
        return self.sudoku.is_valid(num, pos)

    def solve(self):
        return self.backtrack()

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.sudoku.board[i, j] == 0:
                    return (i, j)
        return None

    def backtrack(self):
        empty = self.find_empty()
        if not empty:
            return self.sudoku.board
        row, col = empty

        for num in range(1, 10):
            if self.is_valid(num, (row, col)):
                self.sudoku.board[row, col] = num
                if self.backtrack() is not False:
                    return self.sudoku.board
                self.sudoku.board[row, col] = 0

        return False

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.create_widgets()

    def create_widgets(self):
        self.entries = [[tk.Entry(self.root, width=2, font=('Arial', 18), justify='center') for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.entries[i][j].grid(row=i, column=j, padx=5, pady=5)

        self.solve_ga_button = tk.Button(self.root, text="Solve with GA", command=self.solve_with_ga)
        self.solve_ga_button.grid(row=10, column=0, columnspan=3)

        self.solve_csp_button = tk.Button(self.root, text="Solve with CSP", command=self.solve_with_csp)
        self.solve_csp_button.grid(row=10, column=3, columnspan=3)

        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear_board)
        self.clear_button.grid(row=10, column=6, columnspan=3)

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)

    def get_board(self):
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                val = self.entries[i][j].get()
                if val == "":
                    row.append(0)
                else:
                    row.append(int(val))
            board.append(row)
        return board

    def display_board(self, board):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, board[i, j])

    def solve_with_ga(self):
        board = self.get_board()
        sudoku = Sudoku(board)
        solver = GASolver(sudoku)
        solved_board = solver.solve()
        if solved_board is not None:
            self.display_board(solved_board)
        else:
            print("No solution found with GA")

    def solve_with_csp(self):
        board = self.get_board()
        sudoku = Sudoku(board)
        solver = CSPSolver(sudoku)
        solved_board = solver.solve()
        if solved_board is not False:
            self.display_board(solved_board)
        else:
            print("No solution found with CSP")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

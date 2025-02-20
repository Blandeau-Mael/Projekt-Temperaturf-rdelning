import numpy as np
import sys
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

WIDTH = 275
LENGTH = 365
WINDOW_WIDTH = 75
WINDOW_LENGTH = 55
RADIATOR_LENGTH = 100
BED_WIDTH = 140
BED_LENGTH = 200
SCALE = 5
A_WINDOW = 0.01*SCALE
A_OUTER_WALL = 0.001*SCALE
A_INNER_WALL = 0.002*SCALE
S = 0.012 * SCALE**2
OUTSIDE_TEMPERATURE = -10
INSIDE_TEMPERATURE = 20


class T():
    '''A class for the individual temperatures t1, t2, ..., tn, each has a number 1-n, a row and a column
    representing their position in the room with row 1 being the top wall and column 1 being the leftmost wall,
    aswell as a type being, "normal", "window", "outer_wall", "inner_wall" or "radiator"'''
    def __init__(self, number, row, column):
        self.number = number
        self.row = row
        self.column = column
        self.type = "normal"

    def surrounding_numbers(self):
        '''A method that returns a list containing the numbers of the surrounding temperatures,
        either 2, 3 or 4 entries depending on whether self is located at a corner, an edge or in the middle'''
        if self.row == 1 and self.column == 1:
            return [2, self.number + (int(WIDTH/SCALE) + 2)]
        if self.row == 1 and self.column == (int(WIDTH/SCALE) + 2):
            return [self.number - 1, self.number + (int(WIDTH/SCALE) + 2)]
        elif self.row == (int(LENGTH/SCALE) + 2) and self.column == 1:
            return [self.number - (int(WIDTH/SCALE) + 2), self.number + 1]
        elif self.row == (int(LENGTH/SCALE) + 2) and self.column == (int(WIDTH/SCALE) + 2):
            return [self.number - (int(WIDTH/SCALE) + 2), self.number - 1]
        elif self.row == 1:
            return [self.number - 1, self.number + 1, self.number + (int(WIDTH/SCALE) + 2)]
        elif self.row == (int(LENGTH/SCALE) + 2):
            return [self.number - 1, self.number + 1, self.number - (int(WIDTH/SCALE) + 2)]
        elif self.column == 1:
            return [self.number - (int(WIDTH/SCALE) + 2), self.number + (int(WIDTH/SCALE) + 2), self.number + 1]
        elif self.column == (int(WIDTH/SCALE) + 2):
            return [self.number - (int(WIDTH/SCALE) + 2), self.number + (int(WIDTH/SCALE) + 2), self.number - 1]
        else:
            return [self.number - 1, self.number + 1, self.number - (int(WIDTH/SCALE) + 2), self.number + (int(WIDTH/SCALE) + 2)]



def make_dictionary():
    '''Creates a dictionary with the keys' numbers representing t1, t2 ... tn
    also links the keys to t objects with the correct numbers, rows and columns.
    Lastly assigns the correct type (except for the radiator)'''
    t_dict = {(key + 1): None for key in range((int(LENGTH/SCALE) + 2)*(int(WIDTH/SCALE) + 2))}
    key = 1
    for i in range(int(LENGTH/SCALE) + 2):
        for j in range(int(WIDTH/SCALE) + 2):
            t_dict[key] = T(key, (i + 1), (j + 1))
            key += 1
    for key in t_dict:
            if t_dict[key].column == 1: t_dict[key].type = "inner_wall"
            if t_dict[key].row == (int(LENGTH/SCALE) + 2): t_dict[key].type = "inner_wall"
            if t_dict[key].row == 1: t_dict[key].type = "outer_wall"
            if t_dict[key].column == (int(WIDTH/SCALE) + 2): t_dict[key].type = "outer_wall"
            if t_dict[key].row == 1 and t_dict[key].column > int((WIDTH - WINDOW_WIDTH)/SCALE) + 1: t_dict[key].type = "window"
            if t_dict[key].column == (int(WIDTH/SCALE) + 2) and t_dict[key].row <= int(WINDOW_LENGTH/SCALE) + 1: t_dict[key].type = "window"
    return(t_dict)


def solve_matrix(t_dict):
    '''Makes and solves the matrix, returns the solution as an array'''
    matrix = np.full(((int(LENGTH/SCALE) + 2)*(int(WIDTH/SCALE) + 2), (int(LENGTH/SCALE) + 2)*(int(WIDTH/SCALE) + 2)), 0, dtype=float)
    b = np.full(((int(LENGTH/SCALE) + 2)*(int(WIDTH/SCALE) + 2), 1), 0, dtype=float)
    for key in t_dict:
        if t_dict[key].type == "normal":
            matrix[key - 1, t_dict[key].number - 1] = -1
            s_n = t_dict[key].surrounding_numbers()
            for i in range(4):
                matrix[key - 1, s_n[i] - 1] = 1/4
        elif t_dict[key].type == "outer_wall":
            matrix[key - 1, t_dict[key].number-1] = -1
            b[key - 1, 0] = -((A_OUTER_WALL/(4 + A_OUTER_WALL))*OUTSIDE_TEMPERATURE)
            s_n = t_dict[key].surrounding_numbers()
            if len(s_n) == 2:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 2/(4 + A_OUTER_WALL)
            else:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 1/(4 + A_OUTER_WALL)
                matrix[key - 1, s_n[2] - 1] = 2/(4 + A_OUTER_WALL)
        elif t_dict[key].type == "inner_wall":
            matrix[key - 1, t_dict[key].number-1] = -1
            b[key - 1, 0] = -((A_INNER_WALL/(4 + A_INNER_WALL))*INSIDE_TEMPERATURE)
            s_n = t_dict[key].surrounding_numbers()
            if len(s_n) == 2:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 2/(4 + A_INNER_WALL)
            else:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 1/(4 + A_INNER_WALL)
                matrix[key - 1, s_n[2] - 1] = 2/(4 + A_INNER_WALL)
        elif t_dict[key].type == "window":
            matrix[key - 1, t_dict[key].number-1] = -1
            b[key - 1, 0] = -((A_WINDOW/(2 + A_WINDOW))*OUTSIDE_TEMPERATURE)
            s_n = t_dict[key].surrounding_numbers()
            if len(s_n) == 2:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 2/(4 + A_WINDOW)
            else:
                for i in range(2):
                    matrix[key - 1, s_n[i] - 1] = 1/(4 + A_WINDOW)
                matrix[key - 1, s_n[2] - 1] = 2/(4 + A_WINDOW)
        elif t_dict[key].type == "radiator":
            matrix[key - 1, t_dict[key].number-1] = -1
            b[key - 1, 0] = -S
            s_n = t_dict[key].surrounding_numbers()
            for i in range(4):
                matrix[key - 1, s_n[i] - 1] = 1/4 
    return(np.linalg.solve(matrix, b))


def calculate_average(x, t_dict, position):
    '''Returns the average temperature over the entire room and over the bed respectively,
    aswell as the position of the radiator for those average'''
    temporary = 0
    for i in range(len(x)):
        if t_dict[i+1].column > 1\
        and t_dict[i+1].column < WIDTH/SCALE + 2\
        and t_dict[i+1].row > 1\
        and t_dict[i+1].row < LENGTH/SCALE + 2:
            temporary+= x[i][0]
    average_room = (temporary/((WIDTH/SCALE)*(LENGTH/SCALE)))
    temporary = 0
    for i in range(len(x)):
        if t_dict[i+1].column > 1\
        and t_dict[i+1].column <= BED_WIDTH/SCALE + 1\
        and t_dict[i+1].row > 1\
        and t_dict[i+1].row <= BED_LENGTH/SCALE + 1:
            temporary+= x[i][0]
    average_bed = (temporary/((BED_WIDTH/SCALE)*(BED_LENGTH/SCALE)))
    return [average_room, average_bed, position]


def plot(x, average_room, average_bed):
    '''Makes a heatmap of the temperatures and also displays the avrages'''
    temperaturelist = []
    row = []
    counter = 0
    for i in range((int(LENGTH/SCALE) + 2)):
        row = []
        for j in range((int(WIDTH/SCALE) + 2)):
            row.append((x[counter][0]))
            counter += 1
        temperaturelist.append(row)
    plt.imshow(temperaturelist, cmap='gnuplot2', interpolation='nearest')
    plt.colorbar()
    plt.text(0, -2, ('Average Room temperature={:.4f}\nAverage Bed temperature={:.4f}'.format(float(average_room), float(average_bed))), fontsize=10)
    plt.text((WIDTH/SCALE)+SCALE, -2, 'Temperatur\n(i Grader Celsius)', fontsize=8)
    plt.show()


def radiator_top(t_dict, averages):
    '''Goes over all the possible radiator possitions along the top wall, and assigns all t's the right type (for each position of the radiator)'''
    for i in range(int((WIDTH - BED_WIDTH - RADIATOR_LENGTH)/SCALE) + 1):
        for key in t_dict:
            if t_dict[key].row != 1 and t_dict[key].row != (int(LENGTH/SCALE) + 2)\
            and t_dict[key].column != 1 and t_dict[key].column != (int(WIDTH/SCALE) + 2):
                t_dict[key].type = "normal"
            if t_dict[key].row == 2\
            and t_dict[key].column > 1 + BED_WIDTH/SCALE + i\
            and t_dict[key].column <= 1 + BED_WIDTH/SCALE + RADIATOR_LENGTH/SCALE + i:
                t_dict[key].type = "radiator"
        x = solve_matrix(t_dict)
        averages.append(calculate_average(x, t_dict, (1 + BED_WIDTH/SCALE + i, 1 + BED_WIDTH/SCALE + RADIATOR_LENGTH/SCALE + i, "top")))


def radiator_right(t_dict, averages):
    '''Goes over all the possible radiator possitions along the right wall, and assigns all t's the right type (for each position of the radiator)'''
    for i in range(int((LENGTH - RADIATOR_LENGTH)/SCALE) + 1):
        for key in t_dict:
            if t_dict[key].row != 1 and t_dict[key].row != (int(LENGTH/SCALE) + 2)\
            and t_dict[key].column != 1 and t_dict[key].column != (int(WIDTH/SCALE) + 2):
                t_dict[key].type = "normal"
            if t_dict[key].column == (int(WIDTH/SCALE) + 2) - 1\
            and t_dict[key].row > 1 + i\
            and t_dict[key].row <= 1 + RADIATOR_LENGTH/SCALE + i:
                t_dict[key].type = "radiator" 
        x = solve_matrix(t_dict)
        averages.append(calculate_average(x, t_dict, (1 + i, 1 + RADIATOR_LENGTH/SCALE + i, "right")))


def final_plot(t_dict, best_average):
    '''Puts the radiator in the calculated best position, and calls the plot function to display the best possible radiator placement on a heatmap.'''
    for key in t_dict:
        if t_dict[key].row != 1 and t_dict[key].row != (int(LENGTH/SCALE) + 2)\
        and t_dict[key].column != 1 and t_dict[key].column != (int(WIDTH/SCALE) + 2):
            t_dict[key].type = "normal"
        if best_average[2][2] == "top":
            if t_dict[key].row == 2\
            and t_dict[key].column > best_average[2][0]\
            and t_dict[key].column <= best_average[2][1]:
                t_dict[key].type = "radiator"
        if best_average[2][2] == "right":
            if t_dict[key].column == (int(WIDTH/SCALE) + 2) - 1\
            and t_dict[key].row > best_average[2][0]\
            and t_dict[key].row <= best_average[2][1]:
                t_dict[key].type = "radiator"
    x = solve_matrix(t_dict)
    plot(x, best_average[0], best_average[1])


def compare_averages(averages):
    '''Compares the list of averages to find the one where the difference in average
    temperature over the room and over the bed is as close to three as possible'''
    best_average = averages[0]
    for i in range(len(averages)):
        if averages[i][0] - averages[i][1] > 0 and abs(averages[i][0] - averages[i][1] - 3) < abs(best_average[0] - best_average[1] - 3): 
            best_average = averages[i]
    return best_average


def main():
    '''Calls all the different funktions and finally prints the optimal placement of the radiator'''
    averages = [] #A list for the different averages
    t_dict = make_dictionary()
    radiator_top(t_dict, averages)
    radiator_right(t_dict, averages)
    best_average = compare_averages(averages)
    if best_average[2][2] == "top":
        print("Elementet ska sitta intill den övre väggen  " + str(WIDTH - (best_average[2][1] - 1)*SCALE) + " cm från den högra väggen")
    if best_average[2][2] == "right":
        print("Elementet ska sitta intill den högra väggen " + str(LENGTH - (best_average[2][1] - 1)*SCALE) + " cm från den nedre väggen")
    final_plot(t_dict, best_average)
    

if __name__ == '__main__':
    main()
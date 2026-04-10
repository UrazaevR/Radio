from pprint import pprint


def transpose(matrix):
    matrix1 = []
    n = len(matrix)
    m = len(matrix[0])
    for k in range(m):
        stolb = []
        for i in range(n):
            stolb += [matrix[i][k]]
        matrix1 = matrix1 + [stolb]
    matrix = matrix1
    return matrix


matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


for row in matrix:
    print(*row, sep=' ')
print()

temp = transpose(matrix)
for row in temp:
    print(*row, sep=' ')
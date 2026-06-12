# by karam mahameed - 213029143
# parser_utils.py
# Reading TSP / CSV input files and building the distance matrix.

import csv
import math
import os

"""
   Read all non-empty lines from a file.
   We strip spaces from each line 
   """
def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

#Extract the value from a TSPLIB header line.
def get_value(line):
    if ":" in line:
        return line.split(":", 1)[1].strip()
    return line.split()[-1].strip()

# Parse a simple CSV file with city coordinates.
def parse_csv(path):
    coords = []
    name = os.path.splitext(os.path.basename(path))[0]

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        rows = list(reader)

    start = 1 if rows and not rows[0][0].strip().isdigit() else 0

    for row in rows[start:]:
        if len(row) >= 3:
            coords.append((float(row[1]), float(row[2])))

    return name, coords, "EUC_2D", None

#Build an explicit distance matrix from numbers in a TSPLIB file.
def build_matrix_from_numbers(nums, n, fmt):
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    idx = 0
    fmt = fmt.upper()

    if fmt == "FULL_MATRIX":
        for i in range(n):
            for j in range(n):
                matrix[i][j] = nums[idx]
                idx += 1

    elif fmt == "UPPER_ROW":
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j] = nums[idx]
                matrix[j][i] = nums[idx]
                idx += 1

    elif fmt == "LOWER_ROW":
        for i in range(1, n):
            for j in range(i):
                matrix[i][j] = nums[idx]
                matrix[j][i] = nums[idx]
                idx += 1

    elif fmt == "UPPER_DIAG_ROW":
        for i in range(n):
            for j in range(i, n):
                matrix[i][j] = nums[idx]
                matrix[j][i] = nums[idx]
                idx += 1

    elif fmt == "LOWER_DIAG_ROW":
        for i in range(n):
            for j in range(i + 1):
                matrix[i][j] = nums[idx]
                matrix[j][i] = nums[idx]
                idx += 1

    else:
        raise ValueError(f"Unsupported EDGE_WEIGHT_FORMAT: {fmt}")

    return matrix

#Parse a .tsp file.
def parse_tsplib(path):
    lines = read_lines(path)

    name = os.path.splitext(os.path.basename(path))[0]
    dimension = None
    edge_weight_type = "EUC_2D"
    edge_weight_format = "FULL_MATRIX"

    for line in lines:
        upper = line.upper()

        if upper.startswith("NAME"):
            name = get_value(line)

        elif upper.startswith("DIMENSION"):
            dimension = int(get_value(line))

        elif upper.startswith("EDGE_WEIGHT_TYPE"):
            edge_weight_type = get_value(line).upper()

        elif upper.startswith("EDGE_WEIGHT_FORMAT"):
            edge_weight_format = get_value(line).upper()

    if dimension is None:
        raise ValueError("DIMENSION not found in TSP file")

    coords = []
    explicit_matrix = None

    if any(line.upper() == "NODE_COORD_SECTION" for line in lines):
        start = lines.index("NODE_COORD_SECTION") + 1

        for line in lines[start:]:
            upper = line.upper()

            if upper == "EOF" or upper.startswith("DISPLAY_DATA_SECTION"):
                break

            parts = line.split()

            if len(parts) >= 3:
                coords.append((float(parts[1]), float(parts[2])))

    if any(line.upper() == "EDGE_WEIGHT_SECTION" for line in lines):
        start = lines.index("EDGE_WEIGHT_SECTION") + 1
        nums = []

        for line in lines[start:]:
            upper = line.upper()

            if upper == "EOF" or upper.startswith("DISPLAY_DATA_SECTION"):
                break

            for part in line.split():
                nums.append(int(float(part)))

        explicit_matrix = build_matrix_from_numbers(nums, dimension, edge_weight_format)

    if not coords:
        coords = [(0.0, 0.0) for _ in range(dimension)]

    return name, coords, edge_weight_type, explicit_matrix

#Load a problem file.
def load_problem(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        return parse_csv(path)

    return parse_tsplib(path)

#Calculate EUC_2D distance between two points.
def euc_2d_distance(p1, p2):
    return int(round(math.hypot(p1[0] - p2[0], p1[1] - p2[1])))

#Calculate ATT distance.
def att_distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]

    rij = math.sqrt((dx * dx + dy * dy) / 10.0)
    tij = int(round(rij))

    if tij < rij:
        return tij + 1

    return tij

#Convert GEO coordinate format to radians.
def geo_to_rad(x):
    deg = int(x)
    minutes = x - deg
    return math.pi * (deg + 5.0 * minutes / 3.0) / 180.0

#Calculate GEO distance between two cities.
def geo_distance(p1, p2):
    rrr = 6378.388

    lat1 = geo_to_rad(p1[0])
    lon1 = geo_to_rad(p1[1])
    lat2 = geo_to_rad(p2[0])
    lon2 = geo_to_rad(p2[1])

    q1 = math.cos(lon1 - lon2)
    q2 = math.cos(lat1 - lat2)
    q3 = math.cos(lat1 + lat2)

    return int(rrr * math.acos(0.5 * ((1.0 + q1) * q2 - (1.0 - q1) * q3)) + 1.0)

#Build the distance matrix for the problem.
def make_distance_matrix(coords, edge_weight_type, explicit_matrix=None):
    '''
    If the TSP file already contains an explicit distance matrix,
    we use it directly.

    Otherwise, we calculate all pairwise distances from the coordinates
    according to the EDGE_WEIGHT_TYPE.
    '''
    if explicit_matrix is not None:
        return explicit_matrix

    n = len(coords)
    dist = [[0 for _ in range(n)] for _ in range(n)]
    kind = edge_weight_type.upper()

    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0

            elif kind == "ATT":
                dist[i][j] = att_distance(coords[i], coords[j])

            elif kind == "GEO":
                dist[i][j] = geo_distance(coords[i], coords[j])

            else:
                dist[i][j] = euc_2d_distance(coords[i], coords[j])

    return dist
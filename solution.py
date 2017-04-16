from pprint import pprint
from collections import Counter

assignments = []


def cross(a, b):
    return [s + t for s in a for t in b]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(row, cols) for row in rows]
"""Element example: This is the top most row.
row_units[0] = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
"""

column_units = [cross(rows, col) for col in cols]
"""Element example: This is the left most column.
column_units[0] = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
"""

square_units = [
    cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
    for cs in ('123', '456', '789')
]
"""Element example: This is the top left square.
square_units[0] = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
"""

diagonals = [[a[0] + a[1] for a in zip(rows, cols)],
             [a[0] + a[1] for a in zip(rows, cols[::-1])]]
"""Element example: This is the two diagonals.
diagonals[0] = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']
diagonals[1] = ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']
"""

unitlist = row_units + column_units + square_units + diagonals
units = dict((box, [u for u in unitlist if box in u]) for box in boxes)
peers = dict((box, set(sum(units[box], [])) - set([box])) for box in boxes)


def display(values):
    """Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[box]) for box in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + col].center(width) + ('|' if col in '36' else
                                                       '') for col in cols))
        if r in 'CF': print(line)
    return


def assign_value(values, box, value):
    """Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        # Find if he have values with 2 digits
        doubles = [values[box] for box in unit if len(values[box]) == 2]
        if not doubles: continue
        # Find if we have twin values
        twins = [item for item, count in Counter(doubles).items() if count > 1]
        if not twins: continue

        for box in unit:
            # Remove all twin digits from peers
            # Only if he have values with more than 1 digit
            if not len(values[box]) > 1: continue
            for twin in twins:
                if values[box] == twin: continue
                for digit in twin:
                    if digit in values[box]:
                        # Remove the digit fro the peer
                        values[box] = values[box].lstrip(digit)

    return values


def grid_values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for value in grid:
        if value == '.':
            values.append(all_digits)
        elif value in all_digits:
            values.append(value)
    assert len(values) == 81
    return dict(zip(boxes, values))


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # Use assign_value so we can enable the vizualization.
                # values[dplaces[0]] = digit
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """Iterate eliminate() and only_choice(). If at some point,
    there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same,
    return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available vals:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[box]) == 1 for box in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[box]), box) for box in boxes
               if len(values[box]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[box]:
        new_sudoku = values.copy()
        new_sudoku[box] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4.....'
    Returns:
        The dictionary representation of the final sudoku grid.
        False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print(
            'We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.'
        )

import random
from typing import Tuple, List, Callable


class State:
    def __init__(self, tiles, man_dist, path):
        self.tiles = tiles
        self.man_dist = man_dist
        self.path = path

    def __lt__(self, other):
        return (len(self.path) + self.man_dist) < (
            len(other.path) + other.man_dist
        )


# Return True if the move (e.g. "H") is legal and False otherwise.
def is_valid_move(tiles: Tuple[int, ...], move: str) -> bool:

    dim = int(len(tiles) ** 0.5)

    return not (
        move == "K"
        and 0 in tiles[-dim:]
        or move == "J"
        and 0 in tiles[:dim]
        or move == "L"
        and 0 in tiles[0::dim]
        or move == "H"
        and 0 in tiles[dim - 1::dim]
    )


def manhattan_distance(x: Tuple[int, int], y: Tuple[int, int]) -> int:
    return sum(abs(a - b) for a, b in zip(x, y))


def get_manhattan_distance(tiles: Tuple[int, ...]) -> int:

    dim = int(len(tiles) ** 0.5)

    tiles_list = list(tiles)
    tiles_list.remove(0)
    return sum(
        [
            manhattan_distance(
                (tiles.index(x) % dim, tiles.index(x) // dim),
                (x % dim, x // dim),
            )
            for x in tiles_list
        ]
    )


def get_new_tile_layout(
    old_tiles: Tuple[int, ...], direction: str, puzzle_dim: int
) -> Tuple[int, ...]:

    index0 = old_tiles.index(0)
    indexOfMovingPiece = -1
    a_list = list(old_tiles)

    if direction == "H":
        indexOfMovingPiece = index0 + 1

    elif direction == "L":
        indexOfMovingPiece = index0 - 1

    elif direction == "K":
        indexOfMovingPiece = index0 + puzzle_dim

    elif direction == "J":
        indexOfMovingPiece = index0 - puzzle_dim

    a_list[index0], a_list[indexOfMovingPiece] = (
        a_list[indexOfMovingPiece],
        a_list[index0],
    )

    return tuple(a_list)


def remove_prev_direction(
    curr_directions: List[str], previous_move: str
) -> List[str]:
    opposites = {"H": "L", "J": "K", "K": "J", "L": "H"}
    dirs_copy = curr_directions.copy()
    undoing_move = opposites[previous_move]

    dirs_copy.remove(undoing_move)
    return dirs_copy


def is_solvable(tiles: Tuple[int, ...]) -> bool:

    dim = int(len(tiles) ** 0.5)
    indexOf0 = tiles.index(0)

    # remove the 0
    tilesList = list(tiles)
    tilesList.remove(0)
    tilesNoZero = tuple(tilesList)

    # call merge sort to get # of inversions
    _, inversions = mergesort(tilesNoZero)

    # run logic to determine true or false

    # if size is odd
    if dim % 2:
        # needs even inversions
        return not inversions % 2

    # If the blank tile is in an even row (zero-indexed)
    if not (indexOf0 // dim) % 2:
        # number of inversions in the puzzle is an even number
        return not inversions % 2

    return bool(inversions % 2)


def mergesort(tiles: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int]:
    left_inversions = 0
    right_inversions = 0

    # base case, its sorted
    if len(tiles) <= 1:
        return tiles, 0

    left = tiles[: len(tiles) // 2]
    right = tiles[len(tiles) // 2:]

    # Recursively sort both sublists.
    left, left_inversions = mergesort(left)
    right, right_inversions = mergesort(right)

    # Then merge the now-sorted sublists.
    return merge(left, right, left_inversions, right_inversions)


def merge(
    left: Tuple[int, ...], right: Tuple[int, ...], ai: int, bi: int
) -> Tuple[Tuple[int, ...], int]:
    result: Tuple[int, ...] = ()
    inversions = ai + bi

    while len(left) != 0 and len(right) != 0:
        if left[0] <= right[0]:
            result += (left[0],)
            left = left[1:]
        else:
            result += (right[0],)
            right = right[1:]
            inversions += len(left)

    result += left
    result += right

    return result, inversions


def make_solvable_random_tiles(width: int) -> Tuple[int, ...]:

    # get a random set of tiles
    random_tiles = tuple(random.sample(range(width ** 2), width ** 2))

    # make sure it is solvable. if it isn't try again until it is
    while not is_solvable(random_tiles):
        random_tiles = tuple(random.sample(range(width ** 2), width ** 2))

    return random_tiles


def get_boosted_start(
    width: int, k: int, get_len: Callable[[Tuple[int, ...]], int]
) -> Tuple[Tuple[int, ...], int]:

    # get k random tiles as starting points
    random_tiles_list = [make_solvable_random_tiles(width) for _ in range(k)]

    # calculat all optimal lens, and pick top prospect from there
    optimal_soln_list = [get_len(x) for x in random_tiles_list]

    optimal_soln = max(optimal_soln_list)
    best_tiles = random_tiles_list[optimal_soln_list.index(optimal_soln)]

    return best_tiles, optimal_soln


def hillclimb(
    tiles: Tuple[int, ...],
    optimal_soln: int,
    width: int,
    get_len: Callable[[Tuple[int, ...]], int],
) -> Tuple[Tuple[int, ...], int]:

    # get all frontier states (all possible moves we can go in)
    valid_directions = [x for x in "HJKL" if is_valid_move(tiles, x)]

    # for each frontier state/direction:
    for direction in valid_directions:

        # move in that direction
        new_tiles = get_new_tile_layout(tiles, direction, width)

        # calculate optimal solution
        optimal_soln_temp = get_len(new_tiles)

        # if the optimal solution is longer, then it becomes the best!
        if optimal_soln_temp >= optimal_soln:
            optimal_soln = optimal_soln_temp
            tiles = new_tiles
    return tiles, optimal_soln


def shuffle_tiles(
    width: int, min_len: int, get_len: Callable[[Tuple[int, ...]], int]
) -> Tuple[int, ...]:

    k = 10
    count = 0

    if width == 4:
        return make_solvable_random_tiles(width)

    # choose k random arrangements and pick from the best one
    tiles, optimal_soln = get_boosted_start(width, k, get_len)

    prev_optimal_soln = optimal_soln

    # if its not, then raw hill climb - gen_len possible moves and pick best
    while optimal_soln < min_len:

        # hill climb as high as you can and then return that result
        tiles, optimal_soln = hillclimb(tiles, optimal_soln, width, get_len)

        if optimal_soln == prev_optimal_soln:
            count += 1

        prev_optimal_soln = optimal_soln

        if count > 2:
            tiles, optimal_soln = get_boosted_start(width, k, get_len)
            count = 0

    return tiles

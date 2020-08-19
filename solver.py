import queue
from typing import Tuple, List


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
        move == "K" and 0 in tiles[-dim:] or
        move == "J" and 0 in tiles[:dim] or
        move == "L" and 0 in tiles[0::dim] or
        move == "H" and 0 in tiles[dim - 1::dim]
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


def solve_puzzle(tiles: Tuple[int, ...]) -> str:

    puzzle_dim = int(len(tiles) ** 0.5)
    q: queue.PriorityQueue = queue.PriorityQueue()

    # create the first state
    man_dist = get_manhattan_distance(tiles)
    curr_state = State(tiles, man_dist, "")

    # A* loop. if the manhat distance is 0, means we're done!
    while curr_state.man_dist != 0:

        # get directions
        valid_directions = [
            x for x in "HJKL" if is_valid_move(curr_state.tiles, x)
        ]

        # prevent it from moving in direction it just moved
        if len(curr_state.path) > 0:
            valid_directions = remove_prev_direction(
                valid_directions, curr_state.path[-1]
            )

        # add the new fontier states to the queue
        for direction in valid_directions:
            new_tiles = get_new_tile_layout(
                curr_state.tiles, direction, puzzle_dim
            )
            man_dist = get_manhattan_distance(new_tiles)
            path_taken = curr_state.path + direction
            new_state = State(new_tiles, man_dist, path_taken)
            q.put(new_state)

        # now pop off the state with the lowest total cost
        curr_state = q.get()

    return curr_state.path


if __name__ == "__main__":
    print(solve_puzzle((3, 7, 1, 4, 0, 2, 6, 8, 5)))

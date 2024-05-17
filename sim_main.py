def preprocess_input(filename: str):
    return []


glb_cycles = 0
add_rs_size = 3
mul_rs_size = 2
issue_width = 2
instruction_queue: list[tuple[str, str, str | None]] = preprocess_input("input.txt")
all_mem_addr = set()


class RSEntry:
    # Reserved station entries
    def __init__(self):
        self.busy: bool = False
        self.sink_tag: int = 0
        self.sink_value: int = 0
        self.source_tag: int = 0
        self.source_value: int = 0

    def __bool__(self):
        return self.busy


add_reservation_station = [RSEntry() for i in range(add_rs_size)]
mul_reservation_station = [RSEntry() for i in range(mul_rs_size)]

while instruction_queue:
    # update cycles
    glb_cycles += 1
    # Check if the command can be issued
    # Commands cannot be issued when the reserved station is full.
    for i in range(issue_width):
        if not instruction_queue:
            break
        instruction: tuple[str, str, str | None] = instruction_queue[0]
        match instruction[0]:
            case "ADD":
                pass
            case "MUL":
                pass
            case "ST":
                pass
            case "LD":
                pass
            case _:
                raise RuntimeError("unsupported instruction ... ")

    # run
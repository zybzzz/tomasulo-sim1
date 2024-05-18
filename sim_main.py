from typing import List, Tuple, Set
from itertools import chain


def preprocess_input(filename: str) -> List[Tuple[str, str, str | None]]:
    return []


glb_cycles = 0
add_rs_size = 3
mul_rs_size = 2
flb_size = 6
flr_size = 4
sdb_size = 3
issue_width = 2
instruction_queue: List[Tuple[str, str, str | None]] = preprocess_input("input.txt")
all_mem_addr: Set[int] = set()


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


add_reservation_station: List[RSEntry] = [RSEntry() for _ in range(add_rs_size)]
mul_reservation_station: List[RSEntry] = [RSEntry() for _ in range(mul_rs_size)]


class FLREntry:
    # FLR entry
    def __init__(self):
        self.busy: bool = False
        self.tag: int = 0
        self.value: int = 0

    def __bool__(self):
        return self.busy


flr: List[FLREntry] = [FLREntry() for _ in range(flr_size)]


class SDBEntry:
    # FLR entry
    def __init__(self):
        self.busy: bool = False
        self.tag: int = 0
        self.value: int = 0
        self.addr: int = 0


sdb: List[SDBEntry] = [SDBEntry() for _ in range(sdb_size)]


def snoop_tag_and_update(tag: int, value: int) -> None:
    assert tag != 0
    for rs_entry in chain(add_reservation_station, mul_reservation_station):
        if not rs_entry.busy:
            continue
        if tag == rs_entry.sink_tag:
            rs_entry.sink_value = value
        if tag == rs_entry.source_tag:
            rs_entry.source_value = value

    for flr_entry in flr:
        if not flr_entry.busy:
            continue
        if tag == flr_entry.tag:
            flr_entry.value = value

    for sdb_entry in sdb:
        if not sdb_entry:
            continue
        if tag == sdb_entry.tag:
            sdb_entry.value = value

    return

class ExecContext:
    def __init__(self):
        self.cycle_counts: int = 0
        self.rs_entry: RSEntry = None
        self.boardcast_tag: int = None
        self.boardcast_value: int = None

    def __init__(self, cycle_counts: int, rs_entry: RSEntry):
        self.cycle_counts = cycle_counts
        self.rs_entry = rs_entry

    def reset(self, cycle_counts: int, rs_entry: RSEntry):
        self.cycle_counts = cycle_counts
        self.rs_entry = rs_entry

    def __bool__(self):
        return self.cycle_counts <= 0

    def is_exec_finish(self):
        return self.__bool__()

add_exec_context = ExecContext()
mul_exec_context = ExecContext()

while instruction_queue:
    # update cycles
    glb_cycles += 1
    # Check if the command can be issued
    # Commands cannot be issued when the reserved station is full.
    for i in range(issue_width):
        if not instruction_queue:
            break
        instruction: Tuple[str, str, str | None] = instruction_queue[0]
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

    # random load, work before this
    snoop_tag_and_update()
    # add execute and mul execute
    if add_exec_context.is_exec_finish():
        for index, add_entry in enumerate(add_reservation_station):
            if add_entry.busy and add_entry.source_tag == 0 and add_entry.sink_tag == 0:
                # release entry
                add_entry.busy = False
                break
    else:
        add_exec_context.cycle_counts -= 1
        if add_exec_context.is_exec_finish():
            # boardcast
            add_exec_context.boardcast_tag = add_exec_context.rs_entry.sink_tag
            add_exec_context.boardcast_value = add_exec_context.rs_entry.sink_value + add_exec_context.rs_entry.source_value



    # store
    for sdb_entry in sdb:
        if not sdb_entry:
            continue
        all_mem_addr.add(sdb_entry.addr)


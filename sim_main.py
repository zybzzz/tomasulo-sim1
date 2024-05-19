import re
from typing import List, Tuple, Set, Dict
from itertools import chain
from copy import deepcopy
import fileinput
from enum import Enum, auto


class OPCODEType(Enum):
    ADD = auto()
    MUL = auto()
    LD = auto()
    ST = auto()


opcode_type_dict: Dict[str, OPCODEType] = {
    "ADD": OPCODEType.ADD,
    "MUL": OPCODEType.MUL,
    "LD": OPCODEType.LD,
    "ST": OPCODEType.ST
}


class OPType(Enum):
    FLB = auto()
    FLR = auto()
    SDB = auto()
    ADDR = auto()


op_type_dict: Dict[str, OPType] = {
    "FLB": OPType.FLB,
    "FLR": OPType.FLR,
    "SDB": OPType.SDB,
    "ADDR": OPType.ADDR
}


class MetaInstruction:
    import re
    pattern_dict: Dict[str, str] = {
        "instruction_split_pattern": r"\s*,\s*",  # use for string split
        "op_analyse_pattern": r"(?P<name>[A-Z]{3})(?P<index>\d)$"
    }

    op_analyse_pattern: re.Pattern = re.compile(pattern_dict["op_analyse_pattern"])

    def __init__(self, naive_instruction: str):
        decode_instruction_list: List[str] = naive_instruction.split(self.pattern_dict["instruction_split_pattern"])
        decode_instruction_list[:] = [s.strip() for s in decode_instruction_list]
        assert len(decode_instruction_list) == 3, "decode instruction must equal to 3"

        self.naive_opcode: str
        self.naive_op1: str
        self.naive_op2: str
        self.naive_opcode, self.naive_op1, self.naive_op2 = decode_instruction_list

        self.opcode_type: OPCODEType
        self.op1_type: OPType
        self.op2_type: OPType
        self.op1_value: int | None
        self.op1_index: int | None
        self.op2_value: int | None
        self.op2_index: int | None

        if self.naive_opcode in opcode_type_dict.keys():
            self.opcode_type = opcode_type_dict[self.naive_opcode]
        else:
            raise RuntimeError("invalid opcode")

        self.op1_analyse_res: re.Match = self.op_analyse_pattern.match(self.naive_op1)
        if self.op1_analyse_res:
            self.op1_type = op_type_dict[self.op1_analyse_res.group("name")]
            self.op1_index = int(self.op1_analyse_res.group("index"))
        else:
            raise RuntimeError("invalid op1")

        self.op2_analyse_res: re.Match = self.op_analyse_pattern.match(self.naive_op2)
        if self.op1_analyse_res:
            self.op2_type = op_type_dict[self.op2_analyse_res.group("name")]
            self.op2_index = int(self.op2_analyse_res.group("index"))
        else:
            self.op2_type = OPType.ADDR
            self.op2_value = int(self.naive_op2)

        return

    def __str__(self):
        print(self.__dict__)
        pass


def preprocess_input(filename: str) -> List[MetaInstruction]:
    meta_insruction_list = []
    with fileinput.input(files=filename, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            meta_insruction_list.append(MetaInstruction(line))
    return meta_insruction_list


glb_cycles = 0
add_rs_size = 3
mul_rs_size = 2
add_cycles = 2
mul_cycles = 3
flb_size = 6
flr_size = 4
sdb_size = 3
issue_width = 2
instruction_queue: List[MetaInstruction] = preprocess_input("input.txt")
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
    assert tag != 0, "update tag can't be zero"
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
        self.rs_entry: RSEntry | None = None
        self.broadcast_tag: int | None = None
        self.broadcast_value: int | None = None

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
        instruction: MetaInstruction = instruction_queue[0]
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
    # if execute finish issue, else continue to execute
    if add_exec_context.is_exec_finish():
        for index, add_entry in enumerate(add_reservation_station):
            if add_entry.busy and add_entry.source_tag == 0 and add_entry.sink_tag == 0:
                # release entry
                add_entry.busy = False
                # assign to exec unit
                add_exec_context.reset(add_cycles, deepcopy(add_entry))
                break
    else:
        add_exec_context.cycle_counts -= 1
        if add_exec_context.is_exec_finish():
            # broadcast
            add_exec_context.broadcast_tag = add_exec_context.rs_entry.sink_tag
            add_exec_context.broadcast_value = (add_exec_context.rs_entry.sink_value +
                                                add_exec_context.rs_entry.source_value)

    if mul_exec_context.is_exec_finish():
        for index, mul_entry in enumerate(mul_reservation_station):
            if mul_entry.busy and mul_entry.source_tag == 0 and mul_entry.sink_tag == 0:
                # release entry
                mul_entry.busy = False
                # assign to exec unit
                mul_exec_context.reset(mul_cycles, deepcopy(mul_entry))
                break
    else:
        mul_exec_context.cycle_counts -= 1
        if mul_exec_context.is_exec_finish():
            # broadcast
            mul_exec_context.broadcast_tag = mul_exec_context.rs_entry.sink_tag
            mul_exec_context.broadcast_value = (mul_exec_context.rs_entry.sink_value *
                                                mul_exec_context.rs_entry.source_value)

    if add_exec_context.is_exec_finish():
        snoop_tag_and_update(add_exec_context.broadcast_tag, add_exec_context.broadcast_value)

    if mul_exec_context.is_exec_finish():
        snoop_tag_and_update(mul_exec_context.broadcast_tag, mul_exec_context.broadcast_value)

    # store
    for sdb_entry in sdb:
        if not sdb_entry:
            continue
        all_mem_addr.add(sdb_entry.addr)

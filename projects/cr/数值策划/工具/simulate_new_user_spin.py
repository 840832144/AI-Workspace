"""模拟 VIP0 新用户从最低 Bet 开始 Spin 的消耗、返还和进度。"""

from __future__ import annotations

import argparse
import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CELL_RE = re.compile(r"([A-Z]+)(\d+)")
RTP_BY_TIER = {1: 0.95, 2: 0.85, 3: 2.50, 4: 1.30}


@dataclass(frozen=True)
class Segment:
    """一个等级区间内使用固定 Bet 的期望体验。"""

    level: int
    next_level: int
    bet_level: int
    bet: int
    spins: int
    rtp: float
    cost: int
    slot_return: float
    level_reward: int
    vip_exp: int
    building_coins: float
    balance: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-root",
        type=Path,
        required=True,
        help="目标 dev 或 trunk 的 ExcelConfigExport/Excel 目录。",
    )
    parser.add_argument("--start-level", type=int, default=0)
    parser.add_argument("--vip", type=int, default=0)
    parser.add_argument(
        "--start-coins",
        type=int,
        default=33_600,
        help="老虎机启动资金；默认取第1建筑满额产出33,600金币，创角账户初始金币为0",
    )
    parser.add_argument("--target-level", type=int, default=15)
    return parser.parse_args()


def column_index(reference: str) -> int:
    match = CELL_RE.match(reference)
    if not match:
        return 0
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - ord("A") + 1
    return value - 1


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ElementTree.parse(archive.open("xl/sharedStrings.xml")).getroot()
    except KeyError:
        return []
    return [
        "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
        for item in root.findall(f"{{{MAIN_NS}}}si")
    ]


def sheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ElementTree.parse(archive.open("xl/workbook.xml")).getroot()
    relations = ElementTree.parse(
        archive.open("xl/_rels/workbook.xml.rels")
    ).getroot()
    targets = {
        item.attrib["Id"]: item.attrib["Target"]
        for item in relations.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    sheets = workbook.find(f"{{{MAIN_NS}}}sheets")
    if sheets is None:
        raise KeyError("workbook.xml 缺少 sheets 节点")
    for sheet in sheets:
        if sheet.attrib["name"] != sheet_name:
            continue
        target = targets[sheet.attrib[f"{{{REL_NS}}}id"]].lstrip("/")
        return target if target.startswith("xl/") else str(PurePosixPath("xl") / target)
    raise KeyError(f"缺少 Sheet：{sheet_name}")


def cell_value(cell: ElementTree.Element, strings: list[str]) -> object:
    if cell.attrib.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
    node = cell.find(f"{{{MAIN_NS}}}v")
    if node is None or node.text is None:
        return None
    raw = node.text
    if cell.attrib.get("t") == "s":
        return strings[int(raw)]
    if cell.attrib.get("t") in {"str", "e"}:
        return raw
    try:
        number = float(raw)
        return int(number) if number.is_integer() else number
    except ValueError:
        return raw


def read_sheet(path: Path, sheet_name: str) -> list[list[object]]:
    """用标准库只读解析 XLSX，不依赖 Excel 客户端。"""

    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        root = ElementTree.parse(archive.open(sheet_path(archive, sheet_name))).getroot()
        result: list[list[object]] = []
        for row in root.findall(f".//{{{MAIN_NS}}}row"):
            values: dict[int, object] = {}
            for cell in row.findall(f"{{{MAIN_NS}}}c"):
                values[column_index(cell.attrib.get("r", ""))] = cell_value(
                    cell, strings
                )
            width = max(values, default=-1) + 1
            result.append([values.get(index) for index in range(width)])
        return result


def data_rows(path: Path, sheet_name: str) -> list[list[object]]:
    """跳过表头、类型、端标记和注释四行。"""

    return read_sheet(path, sheet_name)[4:]


def integer(value: object, default: int = 0) -> int:
    return int(value) if isinstance(value, (int, float)) else default


def load_parameters(config_root: Path) -> dict[str, object]:
    levels = {
        integer(row[0]): {
            "type": integer(row[1]),
            "requirement": integer(row[2]),
        }
        for row in data_rows(config_root / "LevelCfg.xlsx", "Sheet1")
        if len(row) >= 3 and isinstance(row[0], (int, float))
    }
    bets = {
        integer(row[0]): {
            "exp": integer(row[4]),
            "bet": integer(row[5]),
        }
        for row in data_rows(config_root / "SlotsCasinoBetList.xlsx", "Sheet1")
        if len(row) >= 6 and isinstance(row[0], (int, float))
    }
    unlocks: dict[int, int] = {}
    for row in data_rows(config_root / "SlotsCasinoBetUnlock.xlsx", "Sheet2"):
        if len(row) < 3 or not isinstance(row[0], (int, float)) or row[1] != 0:
            continue
        level = integer(row[0])
        unlocks[level] = max(unlocks.get(level, 0), integer(row[2]))
    newbie_rtp = [
        (integer(row[1]), integer(row[2]), RTP_BY_TIER[integer(row[3])])
        for row in data_rows(config_root / "SlotsCasinoNewbieConfig.xlsx", "Sheet1")
        if len(row) >= 4 and integer(row[3]) in RTP_BY_TIER
    ]
    awards = {
        integer(row[0]): {
            "money": integer(row[3]),
            "vip_exp": integer(row[5]),
        }
        for row in data_rows(config_root / "LevelAward.xlsx", "Sheet1")
        if len(row) >= 6 and isinstance(row[0], (int, float))
    }
    building = {
        integer(row[0]): integer(row[1]) / 100 * integer(row[4])
        for row in data_rows(config_root / "SpinDropBuildingCoins.xlsx", "Sheet1")
        if len(row) >= 5 and isinstance(row[0], (int, float))
    }
    vip_need = {
        integer(row[0]): integer(row[1])
        for row in data_rows(config_root / "VipCfg.xlsx", "Sheet1")
        if len(row) >= 2 and isinstance(row[0], (int, float))
    }
    return {
        "levels": levels,
        "bets": bets,
        "unlocks": unlocks,
        "newbie_rtp": newbie_rtp,
        "awards": awards,
        "building": building,
        "vip_need": vip_need,
    }


def max_bet_level(level: int, unlocks: dict[int, int]) -> int:
    available = [bet_level for gate, bet_level in unlocks.items() if gate <= level]
    return max(available, default=1)


def level_rtp(level: int, ranges: list[tuple[int, int, float]]) -> float:
    for minimum, maximum, rtp in ranges:
        if minimum <= level <= maximum:
            return rtp
    return 0.95


def simulate(
    parameters: dict[str, object],
    *,
    start_level: int,
    vip: int,
    start_coins: int,
    target_level: int,
) -> list[Segment]:
    # 程序配置从 level=1 开始；输入 level=0 视为“显示0、内部配置1”。
    level = max(1, start_level)
    levels = parameters["levels"]
    bets = parameters["bets"]
    unlocks = parameters["unlocks"]
    rtp_ranges = parameters["newbie_rtp"]
    awards = parameters["awards"]
    building = parameters["building"]
    if not all(
        isinstance(value, dict) for value in (levels, bets, unlocks, awards, building)
    ) or not isinstance(rtp_ranges, list):
        raise TypeError("配置参数结构无效。")

    balance = float(start_coins)
    total_spins = 0
    result: list[Segment] = []
    while level < target_level:
        level_config = levels.get(level)
        if not isinstance(level_config, dict):
            raise KeyError(f"LevelCfg 缺少等级 {level}")
        bet_level = max_bet_level(level, unlocks)
        bet_config = bets.get(bet_level)
        if not isinstance(bet_config, dict):
            raise KeyError(f"SlotsCasinoBetList 缺少 BetLevel {bet_level}")
        requirement = integer(level_config.get("requirement"))
        if integer(level_config.get("type")) == 1:
            spins = requirement
        else:
            exp_per_spin = max(1, integer(bet_config.get("exp")))
            spins = math.ceil(requirement / exp_per_spin)
        bet = integer(bet_config.get("bet"))
        rtp = level_rtp(level, rtp_ranges)
        cost = spins * bet
        slot_return = cost * rtp
        next_level = level + 1
        award = awards.get(next_level, {})
        level_reward = integer(award.get("money")) if isinstance(award, dict) else 0
        vip_exp = integer(award.get("vip_exp")) if isinstance(award, dict) else 0
        building_coins = sum(
            float(building.get(spin_index, 0))
            for spin_index in range(total_spins + 1, total_spins + spins + 1)
        )
        balance += slot_return - cost + level_reward
        result.append(
            Segment(
                level=level,
                next_level=next_level,
                bet_level=bet_level,
                bet=bet,
                spins=spins,
                rtp=rtp,
                cost=cost,
                slot_return=slot_return,
                level_reward=level_reward,
                vip_exp=vip_exp,
                building_coins=building_coins,
                balance=balance,
            )
        )
        total_spins += spins
        level = next_level
    return result


def money(value: float) -> str:
    return f"{value:,.0f}"


def main() -> int:
    args = parse_args()
    config_root = args.config_root.resolve()
    parameters = load_parameters(config_root)
    segments = simulate(
        parameters,
        start_level=args.start_level,
        vip=args.vip,
        start_coins=args.start_coins,
        target_level=args.target_level,
    )

    print("# 新用户 Spin 期望模拟")
    print()
    print(
        f"- 输入：VIP={args.vip}，显示等级={args.start_level}，"
        f"起始金币={args.start_coins:,}，目标等级={args.target_level}"
    )
    print("- 约定：显示等级0映射到程序配置等级1；每次升级后使用当前最高已解锁 Bet。")
    print("- RTP：等级0–10按250%期望、11–50按130%期望；不模拟方差和破产概率。")
    print()
    print(
        "| 配置等级 | Bet档 | 单次Bet | Spin | 消耗 | Slot期望返还 | "
        "升级金币 | 本段净变化 | 建设币期望 | 段末金币 |"
    )
    print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    total_vip_exp = 0
    for segment in segments:
        net = segment.slot_return - segment.cost + segment.level_reward
        total_vip_exp += segment.vip_exp
        print(
            f"| {segment.level}→{segment.next_level} | {segment.bet_level} | "
            f"{segment.bet:,} | {segment.spins} | {segment.cost:,} | "
            f"{money(segment.slot_return)} | {segment.level_reward:,} | "
            f"{money(net)} | {money(segment.building_coins)} | "
            f"{money(segment.balance)} |"
        )
    total_cost = sum(segment.cost for segment in segments)
    total_return = sum(segment.slot_return for segment in segments)
    total_rewards = sum(segment.level_reward for segment in segments)
    total_spins = sum(segment.spins for segment in segments)
    total_building = sum(segment.building_coins for segment in segments)
    vip_need = parameters["vip_need"]
    vip1_need = vip_need.get(1, 0) if isinstance(vip_need, dict) else 0
    print()
    print(
        f"合计：{total_spins} Spin，消耗 {total_cost:,}，"
        f"Slot期望返还 {money(total_return)}，升级金币 {total_rewards:,}，"
        f"建设币期望 {money(total_building)}。"
    )
    print(
        f"VIP经验累计 {total_vip_exp}/{vip1_need}；"
        f"模拟结束时仍为 VIP0。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

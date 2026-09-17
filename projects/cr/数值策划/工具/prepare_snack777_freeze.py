"""TASK-0035：将定向 SVN 导出整理为零数值改动的受控阅读候选。

python prepare_snack777_freeze.py --input <受控任务目录> --prior <TASK-0034/round2> --output <新的受控候选目录>
输入目录含 source-lock.json、export-receipt.json、read-r7004/*.json。
read-r7004 来自既有 extract_xlsx.py 对固定 r7004 导出的只读提取。
不连接 SVN、不写 XLSX、不运行旧盘点/成本模型、不计算哈希。
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from inventory_all_numerics import unit

TABLES = (
    'QuestPickGet', 'QuestPointsCheatSheet', 'QuestGetLevel', 'QuestInitItem',
    'SnackDropItemCfg', 'SnackAddLuck', 'QuestJackpotCfg', 'SnackPassReward',
    'StrikeLucky', 'StrikeLuckyRound', 'Item', 'ItemExchange', 'PriceCheatSheet', 'Activity',
)
ITEM_IDS = {215001, 215003, 215006}


def force_due(n: int | None, next_paid_draw: int, natural_hit: bool,
              special: bool = False, paid: bool = True) -> bool:
    """阅读层规则：next_paid_draw 为当前圈即将发生的第几次付费抽奖。"""
    return bool(paid and not special and n and n > 0 and
                not natural_hit and next_paid_draw == n)


def force_checks() -> list[dict]:
    # 各场景期望来自 User 定义；不把此规则演示当作游戏程序验收。
    cases = [
        ('到期前', (3, 2, False), False),
        ('第N次未自然命中', (3, 3, False), True),
        ('此前已自然命中', (3, 3, True), False),
        ('特殊格永不强制', (3, 3, False, True), False),
        ('临时内圈免费奖励不计付费抽奖', (3, 3, False, False, False), False),
        ('进入新圈计数从1重启', (3, 1, False), False),
        ('进入新轮重置自然命中历史后的第N次', (3, 3, False), True),
        ('未配置强制次数', (None, 1, False), False),
    ]
    return [{'case': name, 'expected': expected, 'actual': force_due(*args),
             'passed': force_due(*args) == expected} for name, args, expected in cases]


def selected(name: str, record: dict) -> bool:
    if name in TABLES[:4]:
        return record.get('questType') in (4, 5)
    if name == 'QuestJackpotCfg':
        return record.get('Type') in (4, 5)
    if name == 'Activity':
        return record.get('id') in (1033, 1034)
    if name in ('Item', 'ItemExchange'):
        return record.get('itemID' if name == 'Item' else 'itemId') in ITEM_IDS
    # 保留整表只读源作共用价值依赖；不重跑价格查档或生成全量价格阅读层。
    return name != 'PriceCheatSheet'


def dump_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('input', 'prior', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or any((p / '.git').exists() for p in (output, *output.parents)):
        raise ValueError('输出必须是新的 Git 外受控目录')
    lock = json.loads((args.input / 'source-lock.json').read_text(encoding='utf-8'))
    receipt = json.loads((args.input / 'export-receipt.json').read_text(encoding='utf-8'))
    if lock['selected_revision'] != 7004 or lock['changed_tables']:
        raise ValueError('本候选仅适用已检查14表无变化的r7004，不静默套用其他版本')
    if {r['file'] for r in receipt} != {n + '.xlsx' for n in TABLES} or any(r['revision'] != 7004 for r in receipt):
        raise ValueError('需要全部14个r7004定向导出回执')
    output.mkdir(parents=True)
    cells, manifest = [], []
    for name in TABLES:
        raw = json.loads((args.input / 'read-r7004' / (name + '.json')).read_text(encoding='utf-8'))
        for sheet in raw['sheets']:
            rows = {r['row']: r['cells'] for r in sheet['rows']}
            headers = {ref[:-1]: v['value'] for ref, v in rows.get(1, {}).items() if v['value'] is not None}
            count = 0
            for index, values in rows.items():
                if index <= 4:
                    continue
                record = {str(field): values.get(f'{col}{index}', {}).get('value') for col, field in headers.items()}
                if not selected(name, record):
                    continue
                count += 1
                identity = {k: record[k] for k in ('questType', 'Type', 'Id', 'id', 'gridId', 'round', 'inout',
                            'boxNum', 'luck', 'level', 'category', 'levelId', 'itemID') if k in record}
                for col, field in headers.items():
                    cell = values.get(f'{col}{index}', {})
                    comment = str(rows.get(4, {}).get(f'{col}4', {}).get('value') or '')
                    cells.append({'table': name + '.xlsx', 'sheet': sheet['name'], 'excel_row': index,
                        'row_key': json.dumps(identity, ensure_ascii=False), 'field': field, 'cell': f'{col}{index}',
                        'current_value': json.dumps(cell.get('value'), ensure_ascii=False),
                        'action': 'KEEP', 'revision': 7004, 'source_comment': comment,
                        'unit_hint': unit(comment, str(field)), 'formula': cell.get('formula', ''),
                        'source_error': cell.get('error', '')})
            manifest.append({'file': name + '.xlsx', 'sheet': sheet['name'], 'revision': 7004,
                'selected_rows': count, 'role': '共用价值依赖；源文件只读保留，不重算查档' if name == 'PriceCheatSheet'
                else '空Sheet保留' if not rows else '薯片/777指定范围阅读层',
                'numeric_changes': 0, 'source': '../source-r7004/' + name + '.xlsx'})
    dump_csv(output / '现值阅读层.csv', list(cells[0]), cells)
    dump_csv(output / '冻结候选清单.csv', list(manifest[0]), manifest)
    dump_csv(output / '数值变更清单.csv', ['table', 'sheet', 'row_id', 'field', 'before', 'after', 'reason'], [])
    with (args.prior / 'G07-连续积分阶段成本.csv').open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        stages = [dict(r, evidence_revision=6961, applicability_revision=7004,
                       reuse_basis='14表路径差异为空；原计算不重跑') for r in reader if r['questType'] in ('4', '5')]
    dump_csv(output / 'Accepted阶段成本引用.csv', list(stages[0]), stages)
    old = json.loads((args.prior / 'decision-models.json').read_text(encoding='utf-8'))
    reuse = {'evidence_revision': 6961, 'applicability_revision': 7004, 'recomputed': False,
             'G07': {k: v for k, v in old['G07'].items() if k in ('4', '5')},
             'G08': old['G08'], 'G13': {'SnackPassReward': old['G13']['SnackPassReward']}}
    (output / 'Accepted规则与Pass引用.json').write_text(json.dumps(reuse, ensure_ascii=False, indent=2), encoding='utf-8')
    checks = force_checks()
    result = {'task_id': 'TASK-0035', 'revision': 7004, 'files': len(receipt), 'sheets': len(manifest),
              'selected_rows': sum(m['selected_rows'] for m in manifest), 'reading_cells': len(cells),
              'reused_stage_rows': len(stages), 'numeric_changes': 0, 'source_writes': 0,
              'source_error_cells': [f"{c['table']}/{c['sheet']}/{c['cell']}" for c in cells if c['source_error']],
              'force_turn_examples': checks, 'scope_check': 'questType=4/5；不纳入拳击/挖矿',
              'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL',
              'evidence_limit': '新候选读取及业务规则演示；不证明游戏运行时，不重跑Accepted模型；尚未冻结'}
    (output / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('force_turn_examples', 'source_error_cells')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

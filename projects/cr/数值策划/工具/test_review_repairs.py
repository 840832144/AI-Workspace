"""R1/R2 最小回归；仅合成样例，无公司数值。python -m unittest discover -s <工具目录> -p test_review_repairs.py"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from inspect_exported_workbook import inspect_workbook
from recalculate_numerical_inventory import divide, source_formula_evidence, special_rtp_reading


class ReviewRepairs(unittest.TestCase):
    def test_cache_categories_are_independent(self) -> None:
        rows = [{'_excel_row': i + 5, '_row_id': str(i), 'note': value, '_formulas': {'note': formula}}
                for i, (value, formula) in enumerate([(None, '=1'), ('#REF!', '=[1]Sheet1!A1'), (0, '=0')])]
        data = {'file': 'Synthetic.xlsx', 'revision': 1, 'sheets': [{'name': 'Sheet1',
                'fields': [{'key': 'note', 'column': 'A', 'comment': '//说明'}], 'records': rows}]}
        evidence = source_formula_evidence(data)
        self.assertEqual([len(evidence[k]) for k in ('missing', 'errors', 'external')], [1, 1, 1])
        self.assertEqual(evidence['errors'][0]['单元格'], 'A6')
        self.assertEqual(evidence['errors'][0]['字段注释'], '//说明')
        self.assertEqual(evidence['errors'][0]['缓存现行值'], '#REF!')
        self.assertEqual(evidence['external'][0]['单元格'], 'A6')
        self.assertIsNone(divide('#REF!', 2))
        self.assertEqual(divide(0, 2), 0)

    def test_special_rtp_preserves_rows_types_and_source_enum(self) -> None:
        source = {'name': 'Sheet1', 'fields': [{'key': 'rtpTier', 'comment': 'RTP\n7：12%'},
                  {'key': 'activityId_5_0', 'comment': '活动条件'}],
                  'records': [{'_excel_row': i + 5, '_row_id': str(i), 'id': ident,
                               'rtpTier': 7, 'activityId_5_0': '001'} for i, ident in enumerate([None, 2, 2])]}
        result = special_rtp_reading(source, 1)
        self.assertEqual([r['id'] for r in result], [None, 2, 2])
        self.assertEqual([r['Excel行'] for r in result], [5, 6, 7])
        self.assertEqual(result[0]['本行rtpTier注释解释'], '12%')
        self.assertEqual(result[0]['activityId_5_0'], '001')
        self.assertIsNone(result[0]['activityId_5_4'])
        self.assertIn('G01/G02', result[0]['优先级与生效缺口'])

    def test_final_xml_counts_formulas_not_equal_prefix_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.xlsx'
            with ZipFile(path, 'w') as z:
                z.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Example" sheetId="1" r:id="rId1"/></sheets></workbook>')
                z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="/xl/worksheets/sheet1.xml"/></Relationships>')
                z.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>=1 is text</t></is></c><c r="B1"><f>1+1</f><v>2</v></c><c r="C1" t="str"><f>""</f><v/></c><c r="D1" t="e"><f>1/0</f><v>#DIV/0!</v></c><c r="E1"><f>1</f></c></row></sheetData></worksheet>')
            result = inspect_workbook(path)
        self.assertEqual(result['formula_cells'], 4)
        self.assertEqual(result['missing_formula_caches'], 1)
        self.assertEqual(result['formula_error_caches'], 1)
        self.assertEqual(result['sheets'][0]['missing_cache_cells'], ['E1'])


if __name__ == '__main__':
    unittest.main()

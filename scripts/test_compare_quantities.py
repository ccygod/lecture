"""Tests for data-reference arithmetic and comparison boundaries."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).with_name('compare_quantities.py')
MODULE=None
if PATH.exists():
    spec=importlib.util.spec_from_file_location('compare_quantities',PATH)
    MODULE=importlib.util.module_from_spec(spec);spec.loader.exec_module(MODULE)

def q(ident,value,unit='亿元',metric='市场规模',subject='全球',period='2025',status='forecast'):
    return dict(id=ident,value=value,unit=unit,metric=metric,subject=subject,period=period,status=status,source='https://example.org/report')

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(MODULE, 'comparison arithmetic helper is not implemented')

    def test_currency_scales_are_normalized(self):
        r=MODULE.compare(q('a','10000','万元'),q('b','1','亿元'),'like_for_like')
        self.assertEqual(r['ratio'],'1')

    def test_scale_reference_preserves_distinct_metrics(self):
        a=q('a','195.25');b=q('b','3659.064',metric='企业营收',subject='小米',period='2024',status='actual')
        r=MODULE.compare(a,b,'scale_reference')
        self.assertAlmostEqual(float(r['percentage_of_reference']),5.336064,places=5)
        self.assertEqual(r['target']['status'],'forecast')
        self.assertTrue(r['warnings'])
        self.assertNotIn('relative_change_percent',r)

    def test_cross_metric_is_not_like_for_like(self):
        with self.assertRaises(ValueError):
            MODULE.compare(q('a','195'),q('b','3659',metric='企业营收'),'like_for_like')

    def test_different_period_is_not_same_period_comparison(self):
        with self.assertRaises(ValueError):
            MODULE.compare(q('a','195'),q('b','2326',period='2030'),'like_for_like')

    def test_forecast_trend_is_calculated_and_labeled(self):
        r=MODULE.compare(q('future','2326.3',period='2030'),q('base','195.25'),'trend')
        self.assertAlmostEqual(float(r['ratio']),11.914469,places=5)
        self.assertEqual(r['target']['status'],'forecast')
        self.assertTrue(any('forecast' in s for s in r['warnings']))

    def test_currencies_cannot_be_silently_converted(self):
        with self.assertRaises(ValueError):
            MODULE.compare(q('a','100','元'),q('b','100','美元'),'scale_reference')

    def test_zero_denominator_is_rejected(self):
        with self.assertRaises(ValueError): MODULE.compare(q('a','10'),q('b','0'),'scale_reference')

    def test_nonfinite_value_is_rejected(self):
        with self.assertRaises(ValueError): MODULE.compare(q('a','NaN'),q('b','10'),'scale_reference')

    def test_trend_cannot_change_subject(self):
        with self.assertRaises(ValueError): MODULE.compare(q('a','20',subject='中国',period='2030'),q('b','10',subject='全球'),'trend')

    def test_duplicate_quantity_ids_are_rejected(self):
        with self.assertRaises(ValueError): MODULE.evaluate({'quantities':[q('a','10'),q('a','20')],'comparisons':[]})

    def test_missing_reference_is_rejected(self):
        with self.assertRaises(ValueError): MODULE.evaluate({'quantities':[q('a','10')],'comparisons':[dict(id='c',target='a',reference='missing',purpose='scale_reference')]})

    def test_source_and_unknown_status_are_not_dropped(self):
        a=q('a','10',status='estimate');a['source']=''
        with self.assertRaises(ValueError): MODULE.compare(a,q('b','20'),'scale_reference')

if __name__=='__main__': unittest.main()

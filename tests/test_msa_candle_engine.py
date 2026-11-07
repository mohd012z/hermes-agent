import unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D
from msa_market_intelligence.candle_engine import Candle, aggregate

T = datetime(2026, 11, 6, tzinfo=timezone.utc)
def c(i, symbol="XAUUSD", complete=True):
    p = D(2600+i)
    return Candle(symbol, 60, T+timedelta(minutes=i), p, p+1, p-1, p, complete)

class CandleTests(unittest.TestCase):
    def test_m1_to_m5(self):
        out = aggregate([c(i) for i in range(10)], 300)
        self.assertEqual(len(out), 2)
        self.assertEqual((out[0].open,out[0].close,out[0].high,out[0].low),(D(2600),D(2604),D(2605),D(2599)))
    def test_gap(self):
        self.assertEqual(aggregate([c(i) for i in (0,1,3,4)],300),[])
    def test_incomplete(self):
        with self.assertRaises(ValueError): aggregate([c(0,complete=False)],300)
    def test_unsorted(self):
        with self.assertRaises(ValueError): aggregate([c(1),c(0)],300)
    def test_duplicate(self):
        with self.assertRaises(ValueError): aggregate([c(0),c(0)],300)
    def test_mixed(self):
        with self.assertRaises(ValueError): aggregate([c(0),c(1,"BTCUSD")],300)
    def test_invalid_ohlc(self):
        with self.assertRaises(ValueError): Candle("XAUUSD",60,T,D(3),D(2),D(1),D(3))
    def test_invalid_target(self):
        with self.assertRaises(ValueError): aggregate([c(0)],100)
    def test_btc_weekend(self):
        rows=[Candle("BTCUSD",60,datetime(2026,11,7,tzinfo=timezone.utc)+timedelta(minutes=i),D(100),D(101),D(99),D(100)) for i in range(5)]
        self.assertEqual(len(aggregate(rows,300)),1)
    def test_no_partial_bucket(self):
        self.assertEqual(aggregate([c(0),c(1)],300),[])

if __name__ == "__main__":
    unittest.main()

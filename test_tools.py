import check, graph
import unittest

files = {
'g0' : "../grammar_samples/grammar0.txt",
'g1' : "../grammar_samples/grammar1.txt",
'g2' : "../grammar_samples/grammar2.txt",
'g3' : "../grammar_samples/grammar3.txt",
'g4' : "../grammar_samples/grammar4.txt",
'g5' : "../grammar_samples/grammar5.txt",
'g6' : "../grammar_samples/grammar6.txt"
}

class TestTools(unittest.TestCase):

    def test_check_grammar0(self):
        with open(files['g0'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            with self.assertRaises(check.GrammarError) as err:
                checker.check()
            self.assertEqual(err.exception.value, "NORULE")

    def test_check_grammar1(self):
        with open(files['g1'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            with self.assertRaises(check.GrammarError) as err:
                checker.check()
            self.assertEqual(err.exception.value, "NORH")

    def test_check_grammar2(self):
        with open(files['g2'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            with self.assertRaises(check.GrammarError) as err:
                checker.check()
            self.assertEqual(err.exception.value, "BADRULE")

    def test_check_grammar3(self):
        with open(files['g3'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            with self.assertRaises(check.GrammarError) as err:
                checker.check()
            self.assertEqual(err.exception.value, "NONDECLARED")

    def test_check_grammar4(self):
        with open(files['g4'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            self.assertEqual(checker.check(), 2) # shift/reduce conflict

    def test_check_grammar5(self):
        with open(files['g5'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            self.assertEqual(checker.check(), 1) # reduce/reduce conflict

    def test_check_grammar6(self):
        with open(files['g6'], 'r') as fpt:
            checker = check.SLR1Checker(fpt.readlines())
            self.assertEqual(checker.check(), 0) # ok

if __name__ == "__main__":
    unittest.main()

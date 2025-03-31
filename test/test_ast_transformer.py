import unittest
from modules.ast_transformer import transform_code

class TestASTTransformer(unittest.TestCase):
    def test_simple_assignment(self):
        source_code = "x = 1"
        transformed_code = transform_code(source_code)
        self.assertIn("obf_x", transformed_code)
        self.assertNotIn(" x =", transformed_code)

    def test_special_names_unchanged(self):
        source_code = "__init__ = 2"
        transformed_code = transform_code(source_code)
        self.assertIn("__init__", transformed_code)
        self.assertNotIn("obf___init__", transformed_code)

    def test_function_definition(self):
        source_code = "def foo(bar):\n    return bar"
        transformed_code = transform_code(source_code)
        # 関数名 foo は obf_foo に変換、引数 bar は obf_bar に変換されるはず
        self.assertIn("def obf_foo(", transformed_code)
        self.assertIn("(obf_bar):", transformed_code)
        self.assertIn("return obf_bar", transformed_code)

if __name__ == '__main__':
    unittest.main()

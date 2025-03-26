import ast
import logging
import sys

class Obfuscator(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # 関数名を変換（特殊名 __ で囲まれている場合は除外）
        if not (node.name.startswith("__") and node.name.endswith("__")):
            node.name = "obf_" + node.name
        # 関数の引数も変換
        for arg in node.args.args:
            if not (arg.arg.startswith("__") and arg.arg.endswith("__")):
                arg.arg = "obf_" + arg.arg
        # さらに、関数内のデフォルト引数やキーワード引数も変換可能ですが、今回はシンプルに
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        # __ で囲まれている特殊な名前は変換しない
        if node.id.startswith("__") and node.id.endswith("__"):
            return node
        # すでに "obf_" が付いている場合は再付加しない
        if not node.id.startswith("obf_"):
            node.id = "obf_" + node.id
        return node

def transform_code(source_code):
    try:
        # ソースコードをASTにパース
        tree = ast.parse(source_code)
        obfuscator = Obfuscator()
        transformed_tree = obfuscator.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        # Python 3.9+ なら ast.unparse を使用、それ以前は astor を利用
        if hasattr(ast, "unparse"):
            transformed_code = ast.unparse(transformed_tree)
        else:
            import astor
            transformed_code = astor.to_source(transformed_tree)
        return transformed_code
    except Exception as e:
        logging.error(f"AST transformation failed: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python ast_transformer.py <source_file.py>")
        sys.exit(1)

    source_file = sys.argv[1]
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        logging.error(f"Failed to read source file {source_file}: {e}")
        sys.exit(1)

    transformed_code = transform_code(source_code)
    if transformed_code is not None:
        output_file = f"transformed_{source_file}"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(transformed_code)
            logging.info(f"Transformed code written to {output_file}")
        except Exception as e:
            logging.error(f"Failed to write transformed code to {output_file}: {e}")
    else:
        logging.error("Transformation failed. No output generated.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()

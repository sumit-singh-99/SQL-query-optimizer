import sys
import os
from app.lexer import tokenize
from app.parser import Parser
from app.semantic import validate as semantic_check
from app.optimizer import optimize
from app.ir_generator import generate_ir, normalize_condition
from app.utils import save_to_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py '<SQL query>'")
        sys.exit(1)

    sql_query = " ".join(sys.argv[1:]).strip()
    print("🔍 Original SQL Input:\n" + sql_query + "\n")

    try:
        tokens = tokenize(sql_query)
        print("🧩 Tokens:")
        for token in tokens:
            print(token)
        print()

        parser = Parser(tokens)
        ast = parser.parse()

        print("🌳 Abstract Syntax Tree (AST):")
        print(ast)
        print()

        errors = semantic_check(ast)
        if errors:
            print("❌ Semantic Errors:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("✔️ Semantic check passed.\n")

        optimized_ast = optimize(ast)
        print("⚙️ Optimized AST:")
        print(optimized_ast)
        print()

        for stmt in optimized_ast:
            if stmt.get("where"):
                stmt["where"] = normalize_condition(stmt["where"])

        ir = generate_ir(optimized_ast)
        print("🛠 Intermediate Representation (Relational Algebra):")
        print(ir)
        print()

        from app.optimizer import ast_to_sql
        optimized_sql = ast_to_sql(optimized_ast)

        print("📄 Optimized SQL Query:")
        print(optimized_sql)
        print()

        os.makedirs("outputs", exist_ok=True)
        save_to_file(optimized_sql, "outputs/optimized_query.sql")
        print("✅ Optimized SQL query saved to outputs/optimized_query.sql")

    except Exception as e:
        import traceback
        print(f"❌ Error during compilation pipeline: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

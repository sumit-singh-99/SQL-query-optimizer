import sys
import os
from app.lexer import tokenize
from app.parser import Parser
from app.semantic import validate as semantic_check
from app.optimizer import optimize
from app.ir_generator import generate_ir
from app.ir_generator import normalize_condition
from app.utils import save_to_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py '<SQL query>'")
        sys.exit(1)

    # Join all args except the first (script name) to support queries with spaces
    sql_query = " ".join(sys.argv[1:]).strip()

    print("🔍 Original SQL Input:\n" + sql_query + "\n")

    try:
        # Lexical Analysis
        tokens = tokenize(sql_query)
        print("🧩 Tokens:")
        for token in tokens:
            print(token)
        print()

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        print("🌳 Abstract Syntax Tree (AST):")
        print(ast)
        print()

        # Semantic Analysis
        errors = semantic_check(ast)
        if errors:
            print("❌ Semantic Errors:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("✔️ Semantic check passed.\n")

        # Optimization
        optimized_ast = optimize(ast)
        print("⚙️ Optimized AST:")
        print(optimized_ast)
        print()

        # Intermediate Representation
        for stmt in optimized_ast:
            if stmt.get("where"):
                stmt["where"] = normalize_condition(stmt["where"])

        ir = generate_ir(optimized_ast)
        print("🛠 Intermediate Representation (Relational Algebra):")
        print(ir)
        print()

        # Generate optimized SQL
        # Ensure the AST or optimizer returns a string SQL; else implement to_sql or similar
        from app.optimizer import ast_to_sql
        optimized_sql = ast_to_sql(optimized_ast)


        print("📄 Optimized SQL Query:")
        print(optimized_sql)
        print()

        # Save to file (ensure folder exists)
        os.makedirs("outputs", exist_ok=True)
        save_to_file(optimized_sql, "outputs/optimized_query.sql")
        print("✅ Optimized SQL query saved to outputs/optimized_query.sql")

    except Exception as e:
        print(f"❌ Error during compilation pipeline: {e}")

if __name__ == "__main__":
    main()

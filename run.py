import sys
from app.lexer import tokenize
from app.parser import Parser
from app.semantic import validate as semantic_check
from app.optimizer import optimize
from app.ir_generator import generate_ir
from app.visualizer import visualize_ast, print_tree_structure
from app.utils import save_to_file, ast_to_sql


def run_pipeline(sql_query, visualize=False, output_file="outputs/optimized_query.sql"):
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
            print("❌ Semantic Errors found:")
            for error in errors:
                print(" - " + error)
            return  # Stop pipeline on semantic error
        else:
            print("✔️ Semantic check passed.\n")

        # Optimization
        optimized_ast = optimize(ast)
        print("⚙️ Optimized AST:")
        print(optimized_ast)
        print()

        # Intermediate Representation (IR)
        ir = generate_ir(optimized_ast)
        print("🛠 Intermediate Representation (Relational Algebra):")
        print(ir)
        print()

        # Visualization (optional)
        if visualize:
            print("🔎 Generating AST visualization...")
            visualize_ast(ast)
            print("✅ Visualization done.\n")

        # Generate optimized SQL query string from optimized AST
        optimized_sql = ast_to_sql(optimized_ast)
        print("📄 Optimized SQL Query:")
        print(optimized_sql)
        print()

        # Save optimized query to file
        save_to_file(optimized_sql, output_file)
        print(f"✅ Optimized SQL query saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error during compilation pipeline: {e}")


def main():
    if len(sys.argv) > 1:
        sql_query = " ".join(sys.argv[1:])
    else:
        sql_query = input("Enter SQL query to optimize:\n")

    run_pipeline(sql_query, visualize=True)


if __name__ == "__main__":
    main()

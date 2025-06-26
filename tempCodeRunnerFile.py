import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor, QPixmap, QBrush

# Import from your main app structure
from app.lexer import tokenize
from app.parser import Parser
from app.semantic import validate as semantic_check
from app.optimizer import optimize, ast_to_sql
from app.ir_generator import generate_ir, normalize_condition


class SQLQueryOptimizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Query Optimizer")
        self.resize(1080, 720)
        self.setMinimumSize(920, 600)
        self.setAutoFillBackground(True)
        self.set_background_image("assets/background.jpg")
        self.init_ui()

    def set_background_image(self, image_path):
        if os.path.exists(image_path):
            palette = self.palette()
            palette.setBrush(self.backgroundRole(), QBrush(QPixmap(image_path).scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)
        else:
            print("❌ Background image not found:", image_path)

    def resizeEvent(self, event):
        self.set_background_image("assets/background.jpg")
        super().resizeEvent(event)

    def init_ui(self):
        font = QFont("Consolas", 12)
        font.setBold(True)

        # Header Title
        title = QLabel("SQL Query Optimizer")
        title.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: bold;")
        subtitle = QLabel("Analyze, optimize, and visualize your SQL queries")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 16px; margin-bottom: 12px;")

        # Input Query
        self.input_query = QTextEdit()
        self.input_query.setFont(font)
        self.input_query.setStyleSheet("""
            background-color: rgba(30, 41, 59, 0.95);
            color: #ffffff;
            border-radius: 6px;
            padding: 12px;
        """)
        input_box = self.create_box("➕ Input Query", self.input_query)

        # Output Query
        self.output_query = QTextEdit()
        self.output_query.setFont(font)
        self.output_query.setReadOnly(True)
        self.output_query.setStyleSheet("""
            background-color: rgba(30, 41, 59, 0.95);
            color: #ffffff;
            border-radius: 6px;
            padding: 12px;
        """)
        output_box = self.create_box("✅ Optimized Query", self.output_query)

        queries_layout = QHBoxLayout()
        queries_layout.setSpacing(20)
        queries_layout.addWidget(input_box, 1)
        queries_layout.addWidget(output_box, 1)

        # Execution Log
        self.execution_log = QTextEdit()
        self.execution_log.setFont(font)
        self.execution_log.setReadOnly(True)
        self.execution_log.setStyleSheet("""
            background-color: rgba(15, 23, 42, 0.95);
            color: #ffffff;
            border-radius: 6px;
            padding: 12px;
        """)
        execution_box = self.create_box("🖥️ Execution Simulation", self.execution_log)

        # Optimize Button
        self.run_button = QPushButton("⚡ Optimize Query")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        self.run_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.run_button.clicked.connect(self.run_optimizer)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(queries_layout)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(execution_box)

        self.setLayout(main_layout)

    def create_box(self, title, widget):
        group_box = QGroupBox(title)
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 5px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        group_box.setLayout(layout)
        return group_box

    def append_log(self, text):
        self.execution_log.append(text)
        self.execution_log.moveCursor(QTextCursor.End)

    def run_optimizer(self):
        sql_query = self.input_query.toPlainText().strip()
        self.execution_log.clear()
        self.output_query.clear()

        if not sql_query:
            self.append_log("❌ No SQL query provided.")
            return

        self.append_log("> Initializing SQL query optimizer...")

        try:
            tokens = tokenize(sql_query)
            self.append_log(f"> Tokens:\n{tokens}")

            parser = Parser(tokens)
            ast = parser.parse()
            self.append_log(f"> AST:\n{ast}")

            errors = semantic_check(ast)
            if errors:
                for err in errors:
                    self.append_log(f"❌ Semantic Error: {err}")
                return
            self.append_log("✔️ Semantic check passed.")

            optimized_ast = optimize(ast)
            for stmt in optimized_ast:
                if stmt.get("where"):
                    stmt["where"] = normalize_condition(stmt["where"])
            self.append_log(f"> Optimized AST:\n{optimized_ast}")

            ir = generate_ir(optimized_ast)
            self.append_log("> Relational Algebra:\n" + ir)

            optimized_sql = ast_to_sql(optimized_ast)
            self.output_query.setPlainText(optimized_sql)
            self.append_log("✅ Optimization Complete.")

        except Exception as e:
            self.append_log(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLQueryOptimizerGUI()
    window.show()
    sys.exit(app.exec_())

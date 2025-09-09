import sqlite3
import datetime

class DatabaseManager:
    """Clase para gestionar la base de datos SQLite."""

    def __init__(self, db_name="fast_food_pos.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Crea las tablas necesarias para la aplicación."""
        
        # Tabla de Productos (con stock)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price_usd REAL NOT NULL,
                stock INTEGER NOT NULL,
                type TEXT NOT NULL
            )
        ''')
        
        # Tabla de Subproductos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subproducts (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                name TEXT NOT NULL,
                price_variation REAL NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')

        # Tabla de Ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                date_time TEXT NOT NULL,
                total_usd REAL NOT NULL,
                payment_method TEXT NOT NULL,
                client_id INTEGER,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        ''')

        # Tabla de Items de Venta
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY,
                sale_id INTEGER,
                product_name TEXT NOT NULL,
                subproduct_name TEXT,
                quantity INTEGER NOT NULL,
                price_per_unit_usd REAL NOT NULL,
                FOREIGN KEY(sale_id) REFERENCES sales(id)
            )
        ''')

        # Tabla de Clientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT
            )
        ''')

        # Tabla de Tasa de Cambio
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rate (
                id INTEGER PRIMARY KEY,
                rate REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    # --- Métodos de Inventario ---
    def add_product(self, name, price_usd, stock, prod_type):
        self.cursor.execute("INSERT INTO products (name, price_usd, stock, type) VALUES (?, ?, ?, ?)", 
                            (name, price_usd, stock, prod_type))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def add_product_stock(self, product_id, stock_to_add):
        self.cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (stock_to_add, product_id))
        self.conn.commit()

    def get_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return self.cursor.fetchone()

    def add_subproduct(self, product_id, name, price_variation):
        self.cursor.execute("INSERT INTO subproducts (product_id, name, price_variation) VALUES (?, ?, ?)",
                            (product_id, name, price_variation))
        self.conn.commit()

    def get_subproducts(self, product_id):
        self.cursor.execute("SELECT * FROM subproducts WHERE product_id = ?", (product_id,))
        return self.cursor.fetchall()

    def add_client(self, name, phone):
        self.cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()
        
    def record_sale(self, total_usd, payment_method, client_id=None):
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO sales (date_time, total_usd, payment_method, client_id) VALUES (?, ?, ?, ?)",
                            (date_time, total_usd, payment_method, client_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_sale_item(self, sale_id, product_name, subproduct_name, quantity, price_per_unit_usd):
        self.cursor.execute("INSERT INTO sale_items (sale_id, product_name, subproduct_name, quantity, price_per_unit_usd) VALUES (?, ?, ?, ?, ?)",
                            (sale_id, product_name, subproduct_name, quantity, price_per_unit_usd))
        self.conn.commit()
        
    def get_sales_report(self, start_date, end_date):
        self.cursor.execute("SELECT * FROM sales WHERE date_time BETWEEN ? AND ?", (start_date, end_date))
        return self.cursor.fetchall()
        
    # --- Métodos de Reportes Detallados ---
    def get_sales_by_product_summary(self, start_date, end_date):
        self.cursor.execute('''
            SELECT product_name, SUM(quantity) as total_quantity, SUM(price_per_unit_usd * quantity) as total_usd
            FROM sale_items
            JOIN sales ON sale_items.sale_id = sales.id
            WHERE sales.date_time BETWEEN ? AND ?
            GROUP BY product_name
            ORDER BY total_quantity DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_sales_by_payment_method(self, start_date, end_date):
        self.cursor.execute('''
            SELECT payment_method, SUM(total_usd)
            FROM sales
            WHERE date_time BETWEEN ? AND ?
            GROUP BY payment_method
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def set_exchange_rate(self, rate):
        self.cursor.execute("DELETE FROM exchange_rate")
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO exchange_rate (rate, last_updated) VALUES (?, ?)", (rate, date_time))
        self.conn.commit()

    def get_exchange_rate(self):
        self.cursor.execute("SELECT rate FROM exchange_rate ORDER BY last_updated DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()
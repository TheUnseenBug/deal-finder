import psycopg2
import os

# Database connection settings (use environment variables or defaults)
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_NAME = os.getenv('POSTGRES_DB', 'products_db')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

def get_connection():
    """Create a connection to the PostgreSQL database"""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def setup():
    """Set up the database and create tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        price TEXT,
        category TEXT,
        offerText TEXT,
        image TEXT
    )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print(f"Database setup complete: {DB_NAME}")

def add_data(data_list):
    """
    Add multiple products to the database
    
    Args:
        data_list: List of dictionaries containing product data
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert each product
    for product in data_list:
        cursor.execute('''
        INSERT INTO products (title, price, category, offerText, image)
        VALUES (%s, %s, %s, %s, %s)
        ''', (
            product.get('title', ''),
            product.get('price', ''),
            product.get('category', ''),
            product.get('offerText', ''),
            product.get('image', '')
        ))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print(f"Added {len(data_list)} products to the database")

def get_all_products():
    """Retrieve all products from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    # Convert to list of dictionaries
    columns = ['id', 'title', 'price', 'category', 'offerText', 'image']
    result = []
    for product in products:
        result.append(dict(zip(columns, product)))
    
    conn.close()
    return result

def clear_database():
    """Clear all data from the products table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM products')
    conn.commit()
    conn.close()
    
    print("Database cleared")

# Run setup when the script is executed directly
if __name__ == "__main__":
    setup()
    print("Database is ready to use")
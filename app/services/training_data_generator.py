# app/services/training_data_generator.py

import pandas as pd
from app.db.mariadb import get_connection

def generate_training_data():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        s.franchise_id,
        DATE(s.sold_at) AS date,
        SUM(sd.amount) AS total_sales,
        ef.avg_temp,
        ef.precipitation,
        ef.sentiment_index
    FROM sales s
    JOIN sales_detail sd ON s.sales_id = sd.sales_id
    JOIN external_factors ef ON DATE(s.sold_at) = ef.date AND ef.region = (
        SELECT SUBSTRING_INDEX(f.franchise_address, ' ', 2)
        FROM franchise f
        WHERE f.franchise_id = s.franchise_id
    )
    GROUP BY s.franchise_id, DATE(s.sold_at)
    ORDER BY DATE(s.sold_at)
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)

    cursor.close()
    conn.close()

    return df

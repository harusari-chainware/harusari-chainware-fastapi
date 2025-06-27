from app.db.mariadb import get_connection

def get_all_franchise_addresses() -> list[dict]:
    """
    모든 가맹점의 {'franchise_id': int, 'franchise_address': str} 목록을 반환합니다.
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()  
        cursor.execute("SELECT franchise_id, franchise_address FROM franchise")
        rows = cursor.fetchall()

        print("📋 가맹점 주소 목록:")
        for row in rows:
            print(f"👀 raw row: {row}")
            print(f"  - ID {row['franchise_id']}: {row['franchise_address']}")

        return rows
    finally:
        cursor.close()
        conn.close()

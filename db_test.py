from sqlalchemy import create_engine

try:
    engine = create_engine(
        "postgresql+psycopg2://postgres:xt226s@localhost:5432/inv_mgmt"
    )

    conn = engine.connect()
    print("DB接続成功")
    conn.close()

except Exception as e:
    print("DB接続失敗")
    print(e)
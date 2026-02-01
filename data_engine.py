import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta
import os

DB_NAME = "traffic_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS routes
                 (route_name TEXT, day_of_week INTEGER, hour INTEGER, duration_min INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def generate_demo_data():
    # Only generate if DB doesn't exist (prevents resetting every refresh)
    if os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    print("Generating database...")
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        dow = current_date.weekday() 
        
        for hour in range(24):
            # Complex Logic: Highway vs Local
            if not (dow >= 5) and (hour in [8, 9, 17, 18]):
                d_highway = 55 # Rush hour
            else:
                d_highway = 20 # Clear
            
            d_local = 35 # Always average
            d_toll = 18  # Always fast

            data.append(("Route A: Highway", dow, hour, d_highway + random.randint(-2,2), current_date))
            data.append(("Route B: Local", dow, hour, d_local + random.randint(-2,2), current_date))
            data.append(("Route C: Toll Rd", dow, hour, d_toll + random.randint(-1,1), current_date))

    df = pd.DataFrame(data, columns=['route_name', 'day_of_week', 'hour', 'duration_min', 'timestamp'])
    df.to_sql('routes', conn, if_exists='replace', index=False)
    conn.close()
    print("Database generated successfully.")

if __name__ == "__main__":
    init_db()
    generate_demo_data()

import psycopg2
from psycopg2.extras import RealDictCursor
import config
import json

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def init_db():
    connection = get_db_connection()
    if connection is None:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensors (
                    sensor_id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE,
                    vbat DOUBLE PRECISION,
                    status VARCHAR(20),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS values (
                    id BIGSERIAL PRIMARY KEY,
                    sensor_id INT REFERENCES sensors(sensor_id),
                    type VARCHAR(20),
                    value DOUBLE PRECISION,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_type_time ON values(type, created_at);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_value ON values(sensor_id, value);
            """)
            connection.commit()
    except Exception as e:
        print(f"Error initializing the database: {e}")
    finally:
        connection.close()

def save_message(topic, payload):
    connection = get_db_connection()
    if connection is None:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sensor_id FROM sensors WHERE name = %s;", (topic,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute(
                    "INSERT INTO sensors (name, status) VALUES (%s, %s) RETURNING sensor_id;",
                    (topic, 'online')
                )
                sensor_id = cursor.fetchone()[0]
            else:
                sensor_id = result[0]

            try:
                data = json.loads(payload)
                
                if 'vbat' in data:
                    vbat_value = data.pop('vbat')
                    cursor.execute(
                            "UPDATE sensors SET vbat = %s, status = %s, updated_at = NOW() WHERE sensor_id = %s;",
                            (float(vbat_value), "online", sensor_id)
                        )
                
                for sensor_type, sensor_value in data.items():
                    cursor.execute(
                        "INSERT INTO values (sensor_id, type, value) VALUES (%s, %s, %s);",
                        (sensor_id, sensor_type, float(sensor_value))
                    )
            except Exception as e:
                print(f"Error parsing payload: {e}")
                return
            connection.commit()
    except Exception as e:
        print(f"Error saving message to the database: {e}")
    finally:
        connection.close()

def update_sensor_status(sensor_name, status):
    connection = get_db_connection()
    if connection is None:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE sensors SET status = %s, updated_at = NOW() WHERE name = %s;",
                (status, sensor_name)
            )
            connection.commit()
    except Exception as e:
        print(f"Error updating sensor status: {e}")
    finally:
        connection.close()
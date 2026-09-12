import psycopg2

conn = psycopg2.connect('postgresql://postgres:aothecode@127.0.0.1:5433/admin')
cur = conn.cursor()

sqls = [
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone VARCHAR(20)',
    "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS avatar VARCHAR(255) DEFAULT 'avatar-19.jpg'",
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS dark_mode BOOLEAN DEFAULT false',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP',
]

for sql in sqls:
    try:
        cur.execute(sql)
        print(f'OK: {sql[:50]}')
    except Exception as e:
        print(f'SKIP: {e}')

cur.execute('''CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
print('OK: activity_log table')

conn.commit()
print('Database updated successfully!')
conn.close()

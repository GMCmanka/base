import psycopg2

conn = psycopg2.connect('postgresql://postgres:aothecode@127.0.0.1:5433/admin')
cur = conn.cursor()

# Reset admin to default
cur.execute("""UPDATE "user" 
    SET full_name='System Admin', 
        email='admin@agriculture.com', 
        phone=NULL 
    WHERE username='admin'""")

conn.commit()
print('Admin reset to default!')
conn.close()

import psycopg2

conn = psycopg2.connect('postgresql://postgres:aothecode@127.0.0.1:5433/admin')
cur = conn.cursor()
cur.execute('SELECT full_name, email, phone FROM "user" WHERE username=%s', ('admin',))
row = cur.fetchone()
print('Name:', row[0])
print('Email:', row[1])
print('Phone:', row[2])
conn.close()

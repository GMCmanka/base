import psycopg2

conn = psycopg2.connect('postgresql://postgres:aothecode@127.0.0.1:5433/admin')
cur = conn.cursor()

cur.execute("""UPDATE "user" 
    SET full_name='Abdirahman Mohamed Jimale', 
        email='shapecrown521@gmail.com', 
        phone='+252 617036936' 
    WHERE username='admin'""")

conn.commit()
print('Admin updated with real info!')
conn.close()

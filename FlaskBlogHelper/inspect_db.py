import sqlite3

def main():
    db = 'db.sqlite3'
    conn = None
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        print('Tables:')
        for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            print('-', row[0])

        print('\nSample django_migrations:')
        try:
            for r in cur.execute("SELECT app, name FROM django_migrations ORDER BY app, name LIMIT 50"):
                print(' ', r)
        except Exception as e:
            print('django_migrations not found or error:', e)

    except sqlite3.Error as e:
        print('Error opening database', db, ':', e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()

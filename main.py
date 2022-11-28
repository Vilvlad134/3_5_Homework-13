import psycopg2


def create_db(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Client(
            client_id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            surname VARCHAR(40) NOT NULL,
            email VARCHAR(50) NOT NULL);
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Phone(
            phone_id SERIAL PRIMARY KEY,
            phone_number INTEGER);
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ClientPhone(
            phone INTEGER REFERENCES Phone(phone_id),
            client INTEGER REFERENCES Client(client_id),
            CONSTRAINT cp PRIMARY KEY (phone , client));
    """)
    conn.commit()


def add_client(cursor, name, surname, email, phone=None):
    cursor.execute("""
    insert INTO Client(name, surname, email)
    VALUES(%s, %s, %s) RETURNING client_id;
    """, (name, surname, email))
    clientid = cur.fetchone()[0]
    if phone:
        cursor.execute("""
        insert INTO Phone(phone_number)
        VALUES(%s) RETURNING phone_id;
        """, (phone,))
        phoneid = cur.fetchone()[0]

        cursor.execute("""
        insert INTO ClientPhone(phone, client)
        VALUES(%s, %s);
        """, (phoneid, clientid))

    conn.commit()


def add_phone(cursor, client_id, phone):
    cursor.execute("""
    insert INTO Phone(phone_number)
    VALUES(%s) RETURNING phone_id;
    """, (phone,))
    phoneid = cur.fetchone()[0]

    cursor.execute("""
    insert INTO ClientPhone(phone, client)
    VALUES(%s, %s);
    """, (phoneid, client_id))
    conn.commit()


def update_phone(cursor, client_id, phone):
    cursor.execute("""
    UPDATE Phone
    SET Phone_number = %s
    WHERE phone_id = (SELECT phone FROM Clientphone WHERE client = %s);
    """, (phone, client_id))
    conn.commit()


def update_phone_number(cursor, client_id, phone):
    phone_old = input('У клиента несколько телефонов, введите телефон, который хотите заменить')
    cursor.execute("""
    UPDATE Phone p 
    SET	phone_number = %s
    FROM clientphone c
    WHERE p.phone_number = %s and c.client = %s;
    """, (phone, int(phone_old), int(client_id)))
    conn.commit()


def update_client(cursor, client_id, name=None, surname=None, email=None, phone=None):
    # arguments = locals()
    # del arguments['cursor']
    arguments = vars()
    del arguments['cursor']

    for argument, argvalue in arguments.items():
        if argvalue and argument == 'phone':
            cur.execute("""
            SELECT count(phone)
            FROM Clientphone
            WHERE client = %s;
            """, (client_id,))
            count_phone = cur.fetchone()[0]
            if count_phone == 0:
                add_phone(cur, client_id, phone)
            elif count_phone == 1:
                update_phone(cur, client_id, phone)
            else:
                update_phone_number(cur, client_id, phone)

        elif argvalue and argument != 'client_id':
            cur.execute(
                f"UPDATE Client SET {argument}=%s WHERE client_id=%s;"
                , (argvalue, client_id))
            conn.commit()


def delete_phone(cursor, client_id, phone):
    cur.execute("""
    delete from clientphone using phone
    where phone = phone.phone_id and phone.phone_number = %s and client = %s returning phone.phone_id;
    """, (phone, client_id))
    phone_number = cur.fetchone()[0]

    cur.execute("""
    DELETE FROM Phone
    WHERE phone_id = %s ;
    """, (phone_number,))
    conn.commit()


def delete_client(curcor, client_id):
    cur.execute("""
        delete from clientphone
        where client = %s returning phone;
        """, (client_id,))
    phone_numbers = cur.fetchall()

    for number in phone_numbers:
        if number:
            cur.execute("""
                DELETE FROM Phone
                WHERE phone_id = %s ;
                """, (number,))

    cur.execute("""
    DELETE FROM Client
    WHERE client_id = %s ;
    """, (client_id,))
    conn.commit()


def find_client(cursor, name=None, surname=None, email=None, phone=None):
    arguments = locals()
    del arguments['cursor']
    if phone:
        cur.execute("""
        SELECT * 
        FROM Client 
        WHERE Client_id = (SELECT client 
                            FROM Clientphone c JOIN phone p on c.phone = p.phone_id 
                            WHERE p.phone_number = %s);
        """, (phone,))
        print('Client', cur.fetchall())
    else:
        for argument, values in arguments.items():
            if values != None:
                where_arg = []
                where_arg.append(f"{argument} = '{values}'")
        where_exp = ' AND '.join(where_arg)
        cur.execute(
            f"SELECT * FROM Client WHERE {where_exp};")
        print('Client', cur.fetchall())


conn = psycopg2.connect(database="netology_db", user="postgres", password="52449yfbkm")
with conn.cursor() as cur:
    add_client(cur, 'kot', 'vasya', 'travalerkot@mail.ru', 123123)
    # add_phone(cur, 4, 999777)
    # update_phone(cur, 4, 44444)
    # update_phone_number(cur, 1, 123123)
    # update_client(cur, 1, name="sobako", surname="dada", phone=789789)
    # delete_phone(cur, 1, 33333)
    # delete_client(cur, 4)
    # find_client(cur, phone=123123)
conn.close()
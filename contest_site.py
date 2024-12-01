from flask import Flask, render_template, request, url_for
import sqlite3

app = Flask(__name__)

def create_people_table(cur, conn):
    cur.execute("""
        CREATE TABLE 'Baking Contest People' (
            "User Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Age INTEGER NOT NULL,
            "Phone Number" TEXT NOT NULL,
            "Security Level" INTEGER NOT NULL,
            "Login Password" TEXT NOT NULL
        );
    """)
    conn.commit()
    contestUsers = [(1, 'PDiana', 34, '123-675-7645', 1, 'test123'),
                    (2, 'TJones', 68, '895-345-6523', 2, 'test123'),
                    (3, 'AMath', 29, '428-197-3967', 3, 'test123'),
                    (4, 'BSmith', 37, '239-567-3498', 2, 'test123')]
    cur.executemany("""INSERT INTO "Baking Contest People" VALUES (?,?,?,?,?,?)""", contestUsers)
    conn.commit()

def create_entries_table(cur, conn):
    cur.execute("""
        CREATE TABLE "Baking Contest Entries" (
            "Entry Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "User Id" INTEGER NOT NULL,
            "Name of Baking Item" TEXT NOT NULL,
            "Number of Excellent Votes" INTEGER NOT NULL,
            "Number of Ok Votes" INTEGER NOT NULL,
            "Number of Bad Votes" INTEGER NOT NULL,
            FOREIGN KEY ("User Id") REFERENCES "Baking Contest People"("User Id")
        );
    """)
    conn.commit()
    contestResults = [(1, 1, 'Whoot Whoot Brownies', 1, 2, 4),
                    (2, 2, 'Cho Chip Cookies', 4, 1, 2),
                    (3, 3, 'Cho Cake', 2, 4, 1),
                    (4, 1, 'Sugar Cookies', 2, 2, 1)]
    cur.executemany("""INSERT INTO "Baking Contest Entries" VALUES (?,?,?,?,?,?)""", contestResults)
    conn.commit()

@app.route('/')
def home():
    conn = sqlite3.connect('./sql_db/Contest.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest People'")
    if not cur.fetchone():
        create_people_table(cur, conn)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest Entries'")
    if not cur.fetchone():
        create_entries_table(cur, conn)
    conn.close()
    return render_template('home.html')

@app.route('/enternew')
def add_contest_user():
    return render_template('add_contest_user.html')

@app.route('/addrec', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        try:
            name = request.form['Name']
            age = request.form['Age']
            phoneNum = request.form['Phone Number']
            secLvl = request.form['Security Level']
            pwd = request.form['Login Password']
        except:
            return render_template('results.html', message="Record not added")
        finally:
            msg = list()

            if name.strip() == "":
                msg.append("You can not enter in an empty name")
            
            if phoneNum.strip() == "":
                msg.append("You can not enter in an empty phone number")
            elif len(phoneNum) == 10:
                phoneNum = phoneNum[:3] + "-" + phoneNum[3:6] + "-" + phoneNum[-4:]

            ageNum = 0
            try:
                ageNum = int(age)
            except:
                ageNum = 0
            finally:
                if ageNum <= 0 or ageNum >= 121:
                    msg.append("The Age must be a whole number greater than 0 and less than 121.")
            
            secNum = 0
            try:
                secNum = int(secLvl)
            except:
                secNum = 0
            finally:
                if secNum < 1 or secNum > 3:
                    msg.append("The SecurityLevel must be a numeric between 1 and 3.")
            
            if pwd.strip() == "":
                msg.append("You can not enter in an empty pwd")
            
            if len(msg) == 0:
                conn = sqlite3.connect('./sql_db/Contest.db')
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest People'")
                if not cur.fetchone():
                    create_people_table(cur, conn)
                cur.execute(f"""INSERT INTO 'Baking Contest People' ('Name','Age','Phone Number','Security Level','Login Password') VALUES ('{name}', {ageNum}, '{phoneNum}', {secNum}, '{pwd}')""")
                conn.commit()
                msg.append("Record successfully added")
                conn.close()
            return render_template('results.html', message=msg)


@app.route('/list')
def list_contest_users():
    conn = sqlite3.connect('./sql_db/Contest.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest People'")
    if not cur.fetchone():
        create_people_table(cur, conn)
    rslt = cur.execute("""SELECT Name, Age, "Phone Number", "Security Level", "Login Password" FROM 'Baking Contest People'""")
    rsltList = list()
    for row in rslt:
        rowItems = list()
        for item in row:
            rowItems.append(item)
        rsltList.append(rowItems)
    conn.close()
    return render_template('list_contest_users.html', result=rsltList)

@app.route('/contestResults')
def list_contest_results():
    rsltList = list()
    conn = sqlite3.connect('./sql_db/Contest.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest Entries'")
    if not cur.fetchone():
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest People'")
        if cur.fetchone():
            create_entries_table(cur, conn)
            rslt = cur.execute("SELECT * FROM 'Baking Contest Entries'")
            rsltList = list()
            for row in rslt:
                rowItems = list()
                for item in row:
                    rowItems.append(item)
                rsltList.append(rowItems)
    else:
        rslt = cur.execute("SELECT * FROM 'Baking Contest Entries'")
        rsltList = list()
        for row in rslt:
            rowItems = list()
            for item in row:
                rowItems.append(item)
            rsltList.append(rowItems)
    conn.close()
    return render_template('list_contest_results.html', result=rsltList)

@app.route('/delete')
def delete_tables():
    conn = sqlite3.connect('./sql_db/Contest.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest People'")
    if cur.fetchone():
        cur.execute("""DROP TABLE 'Baking Contest People'""")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Baking Contest Entries'")
    if cur.fetchone():
        cur.execute("""DROP TABLE 'Baking Contest Entries'""")
    conn.commit()
    url = url_for('home')
    deletePage = f"""<html><body><p>Tables deleted.</p><br><a href="{url}">back to home</a></body></html>"""
    conn.close()
    return deletePage

if __name__ == '__main__':
    app.run(port=50000, debug=True)
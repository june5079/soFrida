import os
import json
import sqlite3

class Assets:
    def __init__(self):
        self.db_init()

    def db_init(self):
        self.db_path = os.path.join("./assets.db")
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self.cur.execute('''create table if not exists assets (
            package_name text primary key, 
            title text,
            popular integer,
            category text,
            status text,
            exist_sdk integer,
            access_key_id text,
            secret_access_key text,
            session_token text,
            region text,
            service text)''')
        self.columns = ['package_name', 'title', 'popular','category','status','exist_sdk', 'access_key_id', 'secret_key_id','session_token','region','service']
        self.con.commit()

    def exist(self, package_name):
        return self.cur.execute('''select count(*) from assets where package_name=?''', (package_name,)).fetchone()[0]

    def add(self, package_name, title, popular, category):
        #status : added, downloading, downloaded, analyzed
        self.cur.execute('''insert into assets(package_name, title, popular, category, status) values (?, ?, ?, ?, ?)''', (package_name, title, popular, category, "added",))
        self.con.commit()
    def get(self, package_name):
        package = dict()
        row = self.cur.execute('''select * from assets where package_name=?''', (package_name,)).fetchone()
        for i in range(len(self.columns)):
            package[self.columns[i]] = row[i]
        return package

    def select_all(self):
        print('|'.join(self.columns))
        for row in self.cur.execute('''select * from assets'''):
            print('|'.join(str(x) for x in row))
    def update_one(self, package_name, col_name, col_data):
        if self.exist(package_name):
            self.cur.execute('''update assets set %s=? where package_name=?;'''%col_name, (col_data, package_name))
            self.con.commit()
        else:
            print("no package")
    def update_status(self, package_name, status):
        self.update_one(package_name, 'status', status)
    def exist_sdk(self, package_name, tf):
        self.update_one(package_name, "exist_sdk", (1 if tf else 0))
if __name__ == "__main__":
    ast = Assets()
    if ast.exist("com.happylabs.hps") == False:
        ast.add("com.happylabs.hps", "Happy Pet Story: Virtual Sim", "5000000", "GAME_SIMULATION")
    ast.select_all()
    print(ast.get("com.happylabs.hps"))
    ast.update_status("com.happylabs.hps", "added")
    ast.exist_sdk("com.happylabs.hps", False)
    ast.select_all()





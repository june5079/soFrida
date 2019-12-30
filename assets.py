import os
import json
import sqlite3
import html
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
            cloud_code text,
            access_key_id text,
            secret_key_id text,
            session_token text,
            region text,
            service text,
            bucket text,
            vulnerable integer)''')
        self.columns = ['package_name', 'title', 'popular','category','status', 'cloud_code', 'access_key_id', 'secret_key_id','session_token','region','service','bucket', 'vulnerable']
        self.con.commit()

    def exist(self, package_name):
        return self.cur.execute('''select count(*) from assets where package_name=?''', (package_name,)).fetchone()[0]

    def add(self, package_name, title, popular, category):
        #status : added, downloading, downloaded, analyzed
        title = html.unescape(title)
        self.cur.execute('''insert into assets(package_name, title, popular, category, status) values (?, ?, ?, ?, ?)''', (package_name, title, popular, category, "added",))
        self.con.commit()
    def get(self, package_name):
        package = dict()
        row = self.cur.execute('''select * from assets where package_name=?''', (package_name,)).fetchone()
        for i in range(len(self.columns)):
            package[self.columns[i]] = row[i]
        return package
    def get_all(self):
        package_list = []
        for row in self.cur.execute('''select * from assets'''):
            package = dict()
            for i in range(len(self.columns)):
                if row[i] == None:
                    package[self.columns[i]] = ""
                else:    
                    package[self.columns[i]] = row[i]
            package_list.append(package)
        return package_list
    def get_exist_sdk(self):
        package_list = []
        for row in self.cur.execute('''select * from assets where cloud_code<>"None"'''):
            package = dict()
            for i in range(len(self.columns)):
                if row[i] == None:
                    package[self.columns[i]] = ""
                else:    
                    package[self.columns[i]] = row[i]
            package_list.append(package)
        return package_list
    def get_exist_key(self):
        package_list = []
        for row in self.cur.execute('''select * from assets where access_key_id is not null'''):
            package = dict()
            for i in range(len(self.columns)):
                if row[i] == None:
                    package[self.columns[i]] = ""
                else:    
                    package[self.columns[i]] = row[i]
            package_list.append(package)
        return package_list
    def select_all(self):
        print('|'.join(self.columns))
        for row in self.cur.execute('''select * from assets'''):
            print('|'.join(str(x) for x in row))
    def update_one(self, package_name, col_name, col_data):
        if self.exist(package_name):
            self.cur.execute('''update assets set %s=? where package_name=?;'''%col_name, (col_data, package_name,))
            self.con.commit()
        else:
            print("no package")
    def update_asset(self, package_name, col_list, data_list):
        query = "update assets set "
        set_list = []
        for i in range(len(col_list)):
            set_list.append("%s=?" % col_list[i])
        query += ", ".join(set_list)
        query += " where package_name=?;"
        self.cur.execute(query, (data_list))
        self.con.commit()
    def update_status(self, package_name, status):
        self.update_one(package_name, 'status', status)
    def update_keys(self, package_name, keys):
        if self.exist(package_name):
            self.cur.execute('''update assets set %s=?, %s=?, %s=?, %s=?, %s=?, %s=? where package_name=?'''
                        %("service", "bucket", "region","access_key_id", "secret_key_id","session_token"),
                        (','.join(keys['service']), keys['bucket'], keys['region'], keys['accesskeyid'], keys['secretkeyid'], keys['sessiontoken'], package_name,))
            self.con.commit()
    def set_cloud(self, package_name, code):
        #self.update_one(package_name, "exist_sdk", (1 if code != None else 0))
        self.update_one(package_name, "cloud_code", str(code))
    def delete_one(self, package_name):
        try:
            self.cur.execute('''delete from assets where package_name=?;''', (package_name,))
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return False
    def close(self):
        self.con.close()
if __name__ == "__main__":
    ast = Assets()
    ast.select_all()





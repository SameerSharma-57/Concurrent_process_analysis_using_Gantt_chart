import os
import txt_to_csv as util
import sqlite3

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder_path = os.path.join(base_dir, 'os_project')
data_path = os.path.join(folder_path, 'data')
data_file = os.path.join(data_path, 'data.txt')

if not os.path.exists(data_path):
    os.makedirs(data_path)


if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        pass

os.system("ps aux>{0}".format(data_file))

input_file=data_file
output_file=os.path.join(data_path, 'data.csv')

util.convert_txt_csv(input_file,output_file)
util.convert_txt_csv(input_file,output_file)

conn = sqlite3.connect('os_project.db')
cursor = conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS data")
cursor.execute("CREATE TABLE IF NOT EXISTS data (user varchar(50), pid varchar(7) primary key not null, cpu varchar(7), mem varchar(10), vsz varchar(10), rss varchar(10), tty varchar(10), stat varchar(3), start text, total_time text, command text)")

with open(output_file, 'r') as f:
    next(f)
    for line in f:
        data = line.strip().split(',')
        # print(data)
        try:
            cursor.execute("INSERT OR REPLACE INTO data VALUES (?,?,?,?,?,?,?,?,?,?,?)", data)
        except sqlite3.Error as e:
            print("SQLite error:", e)
conn.commit()
conn.close()
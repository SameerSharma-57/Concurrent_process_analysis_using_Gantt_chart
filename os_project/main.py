# import os
import txt_to_csv as util
import sqlite3
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QGridLayout, QComboBox, QLabel, QCheckBox,QToolTip
from PyQt5.QtCore import QSize, Qt
from itertools import islice
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder_path = os.path.join(base_dir, 'os_project')
data_path = os.path.join(folder_path, 'data')
data_file = os.path.join(data_path, 'data.txt')
database = os.path.join(folder_path,'os_project.db')
def convert_to_seconds(time_str):
            m, s = map(int, time_str.split(':'))
            # return m + s/60 # convert to minutes
            return m*60 + s # convert to minutes
def convert_to_minutes_and_seconds(seconds):
    minutes = seconds // 60
    seconds_remainder = seconds % 60
    return f"{int(minutes):02d}:{int(seconds_remainder):02d}"

class InteractiveBarItem(pg.BarGraphItem):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kw=kwargs
        self.setToolTip('hello! y={}'.format(self.boundingRect().y()))
        # required in order to receive hoverEnter/Move/Leave events
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        for key, value in islice(self.kw.items(), 5, 6):
            self.setToolTip('PID={}'.format(value))

    def mousePressEvent(self, event):
        if event.button() == 2:  # Right mouse button
            self.showContextMenu(event)

    def showContextMenu(self, event):
        contextMenu = QMenu()

        # Add actions to the context menu
        action1 = QAction(f"kill {list(self.kw.items())[5][1]}", self)
        action2 = QAction("Option 2", self)

        # Connect actions to functions
        action1.triggered.connect(self.handleOption1)
        action2.triggered.connect(self.handleOption2)

        # Add actions to the context menu
        contextMenu.addAction(action1)
        contextMenu.addAction(action2)

        # Show the context menu at the mouse position
        contextMenu.exec_(QCursor.pos())

    def handleOption1(self):
        
        os.system(f"kill {list(self.kw.items())[5][1]}")
        print("Process Killed")

    def handleOption2(self):
        print("Option 2 selected")


class View(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Monitor")
        self.resize(800, 600)
        graph_frame = QFrame()
        graph_g_layout = QGridLayout(graph_frame)
        graph_g_layout.setContentsMargins(15, 15, 15, 15)
        graph_g_layout.setSpacing(20)

        self.label = QLabel("Task-Monitor", graph_frame)
        self.checkbox = QCheckBox("Selector", graph_frame)
        self.checkbox.stateChanged.connect(self.clickBox)
        self.graph_cbox = QComboBox(graph_frame)
        self.graph_cbox.setMinimumSize(QSize(150, 0))        
        self.graph_widget = pg.PlotWidget(graph_frame)
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setBackground(background=None)


        graph_g_layout.addWidget(self.label, 0, 0, 1, 1)
        graph_g_layout.addWidget(self.checkbox, 0, 1, 1, 1)
        graph_g_layout.addWidget(self.graph_cbox, 0, 2, 1, 1)
        graph_g_layout.addWidget(self.graph_widget, 1, 0, 1, 3)
        graph_g_layout.setColumnStretch(0, 0 + 1)
        self.setCentralWidget(graph_frame)
        self.data = self.extract_db()
        self.updatePlot()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def clickBox(self, state):
        if state == Qt.Checked:
            self.lr = pg.LinearRegionItem(bounds=[0, 100], movable=True)       
            self.graph_widget.addItem(self.lr)        
        else:
            self.graph_widget.removeItem(self.lr)
    def updatePlot(self):
        brush = pg.mkBrush(color=(90, 90, 90))
        
        for j,i in enumerate(self.data):
            # Convert start time to float
            start_time = float(convert_to_seconds(i[1]))
            item = InteractiveBarItem (
                x0=[start_time], 
                y0=j*10, 
                width=convert_to_seconds(i[2]),
                height=9.5, 
                brush=brush,
                pid = i[0]
                )
            
            
            
            self.graph_widget.addItem(item)
        # self.update_plot_data()
    
    def update_plot_data(self):

        self.update_db()
        self.data=self.extract_db()
        self.updatePlot()
        print("updated")

    def update_db(self):
        if not os.path.exists(data_path):
          os.makedirs(data_path)


        if not os.path.exists(data_file):
            with open(data_file, 'w') as f:
                pass

        # print("ps aux > {0}".format(data_file))
        os.system("ps aux > '{0}'".format(data_file))

        input_file=data_file
        output_file=os.path.join(data_path, 'data.csv')

        util.convert_txt_csv(input_file,output_file)
        util.convert_txt_csv(input_file,output_file)

        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        # cursor.execute("DROP TABLE IF EXISTS data")
        cursor.execute("CREATE TABLE IF NOT EXISTS data (user varchar(50), pid varchar(7) primary key not null, cpu varchar(7), mem varchar(10), vsz varchar(10), rss varchar(10), tty varchar(10), stat varchar(3), start text, total_time text, command text)")

        with open(output_file, 'r') as f:
            next(f)
            for line in f:
                data = line.strip().split(',')
                pid = data[1]
                try:
                    # Check if pid already exists in the database
                    query = f"SELECT total_time FROM data WHERE pid={pid}"
                    cursor.execute(query)
                    existing_total_time = cursor.fetchone()
                    if existing_total_time:
                        # print(existing_total_time)
                        time_in_sec = convert_to_seconds(existing_total_time[0])   
                        # If pid exists, increment the total_time by 1 second
                        new_total_time = convert_to_minutes_and_seconds(time_in_sec + 100)

                        # print(new_total_time)
                        cursor.execute("UPDATE data SET total_time=? WHERE pid=?", (new_total_time, pid))
                    else:
                        # If pid doesn't exist, insert the new data
                        cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?,?,?)", data)

                except sqlite3.Error as e:
                    print("SQLite error:", e)

        conn.commit()
        conn.close()

    def extract_db(self):
        conn = sqlite3.connect(database)  
        cursor = conn.cursor()

        cursor.execute('SELECT pid,start, total_time FROM data WHERE total_time != "0:00" ORDER BY pid LIMIT 50')  
        data = cursor.fetchall()
        conn.close()
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = View()
    win.show()
    sys.exit( app.exec_() )
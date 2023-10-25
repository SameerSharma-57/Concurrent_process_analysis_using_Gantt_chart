import sqlite3
from functools import partial
import psutil as ps
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os ,signal
from itertools import islice
from datetime import datetime
import time
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder_path = os.path.join(base_dir, 'os_project')
data_path = os.path.join(folder_path, 'data')
data_file = os.path.join(data_path, 'data.txt')
database = os.path.join(folder_path ,'os_project.db')
conn = sqlite3.connect(database)
cursor = conn.cursor()
checked_pids = set()  #storing clicked entries here


def convert_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s  

def convert_to_minutes_and_seconds(seconds):
    minutes, seconds_remainder = divmod(seconds, 60)
    hours, minutes_remainder = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes_remainder):02d}:{int(seconds_remainder):02d}"


class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = 0
        
        self.init_ui()
        self.init_timer()
        

    def init_ui(self):
        self.setWindowTitle('System Monitor')
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()

        self.label_cpu = QLabel('Total CPU Usage:-  ')
        self.label_cpu.setStyleSheet("font-size: 20px; color: #555; background-color: #eee; border: 1px solid #ccc; padding: 10px; border-radius: 10px;")
        self.label_cpu.setFont(QFont("Montserrat", 16))  # Change "Times New Roman" to your preferred font family and adjust the font size as needed
        self.layout.addWidget(self.label_cpu)

        self.label_memory = QLabel('Total Memory Usage:-  ')
        self.label_memory.setStyleSheet("font-size: 20px; color: #555; background-color: #eee; border: 1px solid #ccc; padding: 10px; border-radius: 10px;")
        self.label_memory.setFont(QFont("Montserrat", 16))  # Change "Times New Roman" to your preferred font family and adjust the font size as needed
        self.layout.addWidget(self.label_memory)

        # Make the first part bold
        self.label_cpu.setStyleSheet("font-size: 20px; color: #555; font-family: 'Montserrat', sans-serif; background-color: #eee; border: 1px solid #ccc; padding: 10px; border-radius: 10px; font-weight: bold;")
        self.label_memory.setStyleSheet("font-size: 20px; color: #555;font-family: 'Montserrat', sans-serif; background-color: #eee; border: 1px solid #ccc; padding: 10px; border-radius: 10px; font-weight: bold")


        self.table = QTableWidget()
        self.table.setColumnCount(5)

        # Set the stylesheet and font
        self.table.setStyleSheet(
            "background-color: #f5f5f5; color: #333; font-size: 16px; font-family: 'Montserrat', sans-serif;"  # Adjust the font family as needed
            "border: 1px solid #ccc; border-radius: 1px;"
        )

        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        # Set the section resize mode to make all columns stretch except the first one
       # Set the section resize modes to make "Select" smaller and "PID" and "Process Name" stretch
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # "Select" column
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # "PID" column
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # "Process Name" column
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) 

        self.table.horizontalHeader().setStyleSheet("font-family: 'Montserrat', sans-serif; font-size: 14px; background-color: #3498db; color: #fff;")
        self.table.setHorizontalHeaderLabels(["Select", "PID", "Process Name", "CPU time%", "Memory Usage"])
        self.layout.addWidget(self.table)

        self.sort_cpu_button = QPushButton('Sort by CPU Usage')
        self.sort_cpu_button.setStyleSheet("background-color: #3366ff; color: #fff; font-size: 16px;")
        self.sort_cpu_button.clicked.connect(self.sort_by_cpu)
        self.layout.addWidget(self.sort_cpu_button)

        self.sort_memory_button = QPushButton('Sort by Memory Usage')
        self.sort_memory_button.setStyleSheet("background-color: #333; color: #fff; font-size: 16px;")
        self.sort_memory_button.clicked.connect(self.sort_by_memory)
        self.layout.addWidget(self.sort_memory_button)

        self.reset_button = QPushButton('Reset')
        self.reset_button.setStyleSheet("background-color: #e60000; color: #fff; font-size: 16px;")
        self.reset_button.clicked.connect(self.reset)
        self.layout.addWidget(self.reset_button)

        self.setLayout(self.layout)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000) 

    def update_info(self):
        cpu_percent = ps.cpu_percent(interval=0)
        memory_info = ps.virtual_memory()

        self.label_cpu.setText(f'Total CPU Usage: {cpu_percent}%')
        self.label_memory.setText(f'Total Memory Usage: {self.format_bytes(memory_info.used)} / {self.format_bytes(memory_info.total)}')

        self.update_process_table()


    def update_process_table(self):
        attrs = ['pid', 'name', 'cpu_percent', 'memory_percent']
        processes = sorted(ps.process_iter(attrs=attrs), key=lambda x: x.info[attrs[self.mode]], reverse=True)

        self.table.setRowCount(min(len(processes), 100))
        self.table.setColumnWidth(0, 50)

        center_alignment = Qt.AlignmentFlag(Qt.AlignCenter)  # Create the center alignment

        for i, process in enumerate(processes[:100]):
            pid = process.info['pid']
            name = process.info['name']
            cpu_percent = process.info['cpu_percent']
            memory_percent = process.info['memory_percent']

            checkbox = QCheckBox()
            checkbox.setChecked(pid in checked_pids)
            # checkbox.setAlignment(Qt.AlignCenter)  # Center align the checkbox
            checkbox.clicked.connect(partial(self.checkbox_clicked, pid))


            self.table.setCellWidget(i, 0, checkbox)
            self.table.setItem(i, 1, QTableWidgetItem(str(pid)))
            self.table.item(i, 1).setTextAlignment(center_alignment)  # Center align this item
            self.table.setItem(i, 2, QTableWidgetItem(name))
            self.table.item(i, 2).setTextAlignment(center_alignment)  # Center align this item
            self.table.setItem(i, 3, QTableWidgetItem(f'{cpu_percent:.2f}%'))
            self.table.item(i, 3).setTextAlignment(center_alignment)  # Center align this item
            self.table.setItem(i, 4, QTableWidgetItem(f'{memory_percent:.2f}%'))
            self.table.item(i, 4).setTextAlignment(center_alignment)  # Center align this item

        for col in range(self.table.columnCount()):
            self.table.resizeColumnToContents(col)

                
    def checkbox_clicked(self, pid, state):
        if state:
            checked_pids.add(pid)
        else:
            checked_pids.discard(pid)

        
    def sort_by_cpu(self):
        self.mode = 2

    def sort_by_memory(self):
        self.mode = 3
    
    def reset(self):
        self.mode = 0
        checked_pids=set()

    @staticmethod
    def format_bytes(bytes, decimals=2):
        factor = 1024
        for unit in ['', 'KB', 'MB', 'GB', 'TB']:
            if bytes < factor:
                break
            bytes /= factor
        return f"{bytes:.{decimals}f} {unit}"
    

class InteractiveBarItem(pg.BarGraphItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kw = kwargs

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        for key, value in islice(self.kw.items(), 5, 6):
            self.setToolTip('PID={}'.format(value))

    def mousePressEvent(self, event):
        if event.button() == 2:  
            self.showContextMenu(event)

    def showContextMenu(self, event):
        contextMenu = QMenu()

        action1 = QAction(f"kill {list(self.kw.items())[5][1]}", self)
        action2 = QAction("Details", self)

        action1.triggered.connect(self.handleOption1)
        action2.triggered.connect(self.handleOption2)

        contextMenu.addAction(action1)
        contextMenu.addAction(action2)

        contextMenu.exec_(QCursor.pos())

    def handleOption1(self):

        pid = list(self.kw.items())[5][1]
        os.kill(int(pid),signal.SIGKILL)


    def handleOption2(self):
        pid = list(self.kw.items())[5][1]
        data = self.fetch_process_data(pid)

        msg_box = QMessageBox()
        msg_box.setWindowTitle(f"Details for PID {pid}")
        pid=int(pid)
        process = ps.Process(pid)
        details = {
            'pid': pid,
            'name': process.name(),
            'status': process.status(),
            'cpu_percent': process.cpu_percent(interval=1),  
            'memory_percent': process.memory_percent(),
            'create_time': datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
        }
        msg_box.setText(f"Process ID: {details['pid']}\nName: {details['name']}\nStart Time: {details['create_time']}\nCPU%: {details['cpu_percent']}\nMem%: {details['memory_percent']}\nstatus: {details['status']}")
        # msg_box.setText(details)
        msg_box.exec_()

    def fetch_process_data(self, pid):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('SELECT pid,start,cpu,mem FROM data WHERE pid=?', (pid,))
        data = cursor.fetchone()

        conn.close()
        return data
    


class View(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Monitor")

        container_frame = QFrame()
        container_layout = QVBoxLayout(container_frame)

        self.label = QLabel("Task-Monitor")
        self.checkbox = QCheckBox("Selector")
        self.checkbox.stateChanged.connect(self.clickBox)
        self.graph_cbox = QComboBox()
        self.graph_cbox.setMinimumSize(QSize(150, 0))

        container_layout.addWidget(self.label)
        container_layout.addWidget(self.checkbox)
        container_layout.addWidget(self.graph_cbox)

        graph_layout = QVBoxLayout()
        graph_layout.addWidget(container_frame)

        self.graph_view = pg.GraphicsView()
        self.graph_widget = pg.GraphicsLayout()
        self.graph_view.setCentralItem(self.graph_widget)
        graph_layout.addWidget(self.graph_view)
        self.setCentralWidget(self.graph_view)
        self.plot_item = self.graph_widget.addPlot(title="Bar Graph")
        self.plot_item.setLabel('bottom', 'Time (ms)')

        self.mini= 1000000
        self.maxi= 0
        self.fetch_processes_save()
        self.uptime = convert_to_seconds(os.popen('uptime -s').read().split()[1])
        self.timer = QTimer()
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

        self.plot_item.clear() 
        for j, i in enumerate(self.data):
            curr = convert_to_seconds(time.ctime().split()[3])
            start_time = float(convert_to_seconds(i[-1]))
            self.maxi = max(self.maxi, curr - start_time)
            self.mini = min(self.mini, start_time - self.uptime)

            pid = i[0]
            if int(pid) in checked_pids:
                brush=pg.mkBrush(color=(255, 255, 255))
            else:
                brush = pg.mkBrush(color=(90, 90, 90))
            item = InteractiveBarItem(
                x0=[start_time - self.uptime],
                y0=j,
                width=curr - start_time,
                height=1,
                brush=brush,
                pid=i[0],
            )
            self.plot_item.addItem(item)



    def update_plot_data(self):

        self.fetch_processes_save()
        self.data = self.extract_db()

        self.updatePlot()
        
    
        

    def fetch_processes_save(self):

        self.all_pids = ps.pids()
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS data")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS data (pid varchar(7) primary key not null, name text,owner text, status varchar(15), cpu varchar(10), mem varchar(10),start text)")
        for pid in self.all_pids:
            process = ps.Process(pid)
            
            data = [pid,process.name(),process.username(),process.status(),process.cpu_percent(),process.memory_percent(),
                    datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S').split()[1]]
            try:
                cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?)", data)
            except sqlite3.Error as e:
                print("SQLite error:", e)


        conn.commit()

    def extract_db(self):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        cursor.execute('SELECT pid, start FROM data WHERE status IN ("running","sleeping") AND owner !="root"')
        data = cursor.fetchall()
        return data

    def closeEvent(self, a0: QCloseEvent) -> None:
        conn.close()
        return super().closeEvent(a0)

class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Application')
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget(self)

        self.system_monitor_tab = SystemMonitor()
        self.tab_widget.addTab(self.system_monitor_tab, 'Process Monitor')   

        self.interactive_bar_tab = View()
        self.tab_widget.addTab(self.interactive_bar_tab, 'Gantt Chart')

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec_())
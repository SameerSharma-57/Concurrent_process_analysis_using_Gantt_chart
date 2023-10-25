import sys
import psutil as ps
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import QTimer, Qt


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

        self.label_cpu = QLabel('Total CPU Usage: ')
        self.layout.addWidget(self.label_cpu)

        self.label_memory = QLabel('Total Memory Usage: ')
        self.layout.addWidget(self.label_memory)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Process Name", "CPU Usage", "Memory Usage"])
        self.layout.addWidget(self.table)

        self.sort_cpu_button = QPushButton('Sort by CPU Usage')
        self.sort_cpu_button.clicked.connect(self.sort_by_cpu)
        self.layout.addWidget(self.sort_cpu_button)

        self.sort_memory_button = QPushButton('Sort by Memory Usage')
        self.sort_memory_button.clicked.connect(self.sort_by_memory)
        self.layout.addWidget(self.sort_memory_button)
        
        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset)
        self.layout.addWidget(self.reset_button)

        self.setLayout(self.layout)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def update_info(self):
        cpu_percent = ps.cpu_percent(interval=0)
        memory_info = ps.virtual_memory()

        self.label_cpu.setText(f'Total CPU Usage: {cpu_percent}%')
        self.label_memory.setText(f'Total Memory Usage: {self.format_bytes(memory_info.used)} / {self.format_bytes(memory_info.total)}')

        self.update_process_table()

    def update_process_table(self):
        attrs=['pid', 'name', 'cpu_percent', 'memory_percent']
        processes = sorted(ps.process_iter(attrs=attrs),
        key=lambda x: x.info[attrs[self.mode]], reverse=True)

        self.table.setRowCount(min(len(processes), 100))

        for i, process in enumerate(processes[:100]):
            pid = process.info['pid']
            name = process.info['name']
            cpu_percent = process.info['cpu_percent']
            memory_percent = process.info['memory_percent']

            self.table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(f'{cpu_percent:.2f}%'))
            self.table.setItem(i, 3, QTableWidgetItem(f'{memory_percent:.2f}%'))
            
            # self.table.sortByColumn(self.mode)

    def sort_by_cpu(self):
        # self.table.sortItems(2, Qt.DescendingOrder)
        self.mode = 2

    def sort_by_memory(self):
        self.mode = 3
    
    def reset(self):
        self.mode = 0

    @staticmethod
    def format_bytes(bytes, decimals=2):
        factor = 1024
        for unit in ['', 'KB', 'MB', 'GB', 'TB']:
            if bytes < factor:
                break
            bytes /= factor
        return f"{bytes:.{decimals}f} {unit}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())

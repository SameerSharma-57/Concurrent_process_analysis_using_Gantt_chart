import psutil
# from datetime import datetime
# import time
# def get_process_details(pid):
#     try:
#         process = psutil.Process(pid)

#         details = {
#             'pid': pid,
#             'name': process.name(),
#             'status': process.status(),
#             'cpu_percent': process.cpu_percent(interval=1),  # You can adjust the interval
#             'memory_percent': process.memory_percent(),
#             'create_time':  datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
#             # Add more details as needed
#         }
#         return details

#     except psutil.NoSuchProcess as e:
#         print(f"No process with PID {pid}: {e}")
#         return None

# # Example usage
# pid_to_check = 8989  # Replace with the actual PID
# process_details = get_process_details(pid_to_check)

# if process_details:
#     print("Process Details:")
#     for key, value in process_details.items():
#         print(f"{key}: {value}")
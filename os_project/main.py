import os
import txt_to_csv as util
import subprocess


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
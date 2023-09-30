import os
import txt_to_csv as util
os.system("ps aux>/home/kali/prac/os_project/data/data.txt")

input_file='/home/kali/prac/os_project/data/data.txt'
output_file='/home/kali/prac/os_project/data/data.csv'

util.convert_txt_csv(input_file,output_file)
import pandas as pd


def convert_txt_csv(input_file,output_file):

    with open(input_file) as f, open(output_file,'w') as g:
        while True:
            data=f.readline()
            if not data:
                break
            data=data.split()
            l = data[:10]
            l.append(" ".join(data[10:]).replace(',',';'))
            print(",".join(l),file=g)


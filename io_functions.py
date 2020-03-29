class Data:
    data = dict()
    
    
    def __init__(self, file_name):
        try :
            file = open(file_name, "r")
        except:
            print("ERROR:: data file not found")
            exit(1)

        for i in file:
            if len(i.strip()) == 0 or i.strip()[0] == '#':
                continue

            if i.strip() == "FIELD":
                tmp = []
                for j in range(8):
                    tmp_str = file.readline()
                    tmp.append([int(i) for i in tmp_str.strip().split()])
                self.data["FIELD"] = tmp
            
            if i.strip() == "FIGURES":
                tmp = dict()
                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = tmp_str[1]
                self.data["FIGURES"] = tmp

    
def print_field(field, data):
    for i in range(8):
        print(8 - i, end = " |")
        
        for now_fig in field[i]:
            print(data.data["FIGURES"][now_fig], end = " ")
        print()
        
    print("  ------------------------")
    print("   a  b  c  d  e  f  g  h")

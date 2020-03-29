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

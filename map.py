import csv


class Map:
    def __init__(self, d):
        self.data = []

        with open(d, newline='') as csvfile:
            read = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in read:
                dt = row[0].split(',')
                self.data.append(dt)

        self.h = len(self.data)
        self.w = len(self.data[0])

import random
import csv
import numpy as np
numbers = ['0️⃣🔟', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
true_false = ['❌', '✅']

class ChannelNotFoundException(Exception):
    pass

class Database:
    def __init__(self, database_path=None):
        self.path = database_path
        self.column_names = ['name', 'link']
        if database_path is None:
            self.data = []
        else:
            with open(database_path) as f:
                reader = csv.DictReader(f, fieldnames=self.column_names, delimiter='\t')
                lines = list(reader)

            self.data = lines

    def sample(self, shuffle=True, N=25):
        N = min(N, len(self.data))
        if shuffle:
            return random.sample(self.data, N)
        else:
            return self.data[:N]

    def add(self, record):
        self.data.append(record)

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return '\n'.join(list(map(str, self.data)))

    def __delitem__(self, key):
        del self.data[key]

    def store(self, path=None):
        if path is None:
            path = self.path
        with open(path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.column_names, delimiter='\t')
            writer.writerows(self.data)



class GameState:
    def __init__(self, records=None):
        self.vids = []
        if records is not None:
            self.vids+=records

    def pop(self) -> dict:
        return self.vids.pop()

    def add(self, r:dict):
        self.vids.append(r)

    def shuffle(self):
        np.random.shuffle(self.vids)


if __name__ == '__main__':
    s = Database()
    s.store('./data.csv')

import json
import random
import numpy as np
numbers = ['0️⃣🔟', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
true_false = ['❌', '✅']



class Database:
    def __init__(self, database_path=None):
        self.path = database_path
        if database_path is None:
            self.data = []
        else:
            lines = json.load(open(database_path))

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

    def __str__(self):
        return '\n'.join(list(map(str, self.data)))

    def store(self, path=None):
        if path is None:
            path = self.path
        json.dump(self.data, open(path, 'w'))



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
    record = {"link":'https://www.youtube.com/watch?v=3dYjJ3kOGoY', "name":'Code Geass'}
    s.add(record)
    s.store('./data.json')

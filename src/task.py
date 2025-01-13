import time
import numpy as np
import json
from io import BytesIO
import base64

class Task:
    def __init__(self, identifier=0, size=None):
        self.identifier = identifier
        self.size = size or np.random.randint(300, 3000)
        self.a = np.random.rand(self.size, self.size)
        self.b = np.random.rand(self.size)
        self.x = np.zeros(self.size)
        self.time = 0.0

    def work(self):
        start = time.perf_counter()
        try:
            self.x = np.linalg.solve(self.a, self.b)
        except np.linalg.LinAlgError as e:
            print(f"Linear algebra error occurred: {e}")
            self.x = None
        self.time = time.perf_counter() - start

    def to_json(self):
        a_bytes = BytesIO()
        np.save(a_bytes, self.a, allow_pickle=False)
        a_base64 = base64.b64encode(a_bytes.getvalue()).decode('utf-8')

        b_bytes = BytesIO()
        np.save(b_bytes, self.b, allow_pickle=False)
        b_base64 = base64.b64encode(b_bytes.getvalue()).decode('utf-8')

        x_bytes = BytesIO()
        np.save(x_bytes, self.x, allow_pickle=False)
        x_base64 = base64.b64encode(x_bytes.getvalue()).decode('utf-8')

        return json.dumps({
            "a": a_base64,
            "b": b_base64,
            "x": x_base64,
            "identifier": self.identifier,
            "time": self.time,
            "size": self.size,
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)

        a_bytes = base64.b64decode(data["a"])
        a_buffer = BytesIO(a_bytes)
        a = np.load(a_buffer, allow_pickle=False)

        b_bytes = base64.b64decode(data["b"])
        b_buffer = BytesIO(b_bytes)
        b = np.load(b_buffer, allow_pickle=False)

        x_bytes = base64.b64decode(data["x"])
        x_buffer = BytesIO(x_bytes)
        x = np.load(x_buffer, allow_pickle=False)

        task = Task()
        task.a = a
        task.b = b
        task.x = x
        task.identifier = data["identifier"]
        task.time = data["time"]
        task.size = data["size"]
        return task

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (
            np.array_equal(self.a, other.a) and
            np.array_equal(self.b, other.b) and
            np.array_equal(self.x, other.x) and
            self.identifier == other.identifier and
            self.time == other.time and
            self.size == other.size
        )
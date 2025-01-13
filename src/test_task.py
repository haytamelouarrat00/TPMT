import unittest
import numpy as np

from task import Task


class TestTask(unittest.TestCase):
    def test_work_pass(self):
        task = Task()
        task.work()

        np.testing.assert_allclose(np.dot(task.a, task.x), task.b)

    def test_equals(self):
        task = Task()
        dump = task.to_json()
        task2 = Task.from_json(dump)

        self.assertTrue(task == task2, "Equals not working well")


if __name__ == "__main__":
    unittest.main()

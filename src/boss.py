from queueclient import QueueClient
from task import Task
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Boss(QueueClient):
    def __init__(self):
        super().__init__()
        self.sizes = [4990, 6900, 4200, 100, 1000, 10, 2989, 3080, 3398, 1162, 761]
        self.tasks_sent = []
        self.tasks_received = []
        self.errors = []
        self.big_problem = 800

    def run_put_queue(self):
        for size in self.sizes:
            task = Task(identifier=f"Job of size {size}", size=size)
            logging.info(f"Task {task.identifier} created.")
            self.tasks_sent.append(task)
            self.task_queue.put(task)

    def run_get_result(self):
        logging.info("Results in C++")
        results = []
        for _ in range(len(self.sizes)):
            try:
                task = self.result_queue.get(timeout=10)
                self.tasks_received.append(task)
                result = (
                    f"Task {task.identifier} completed, Time: {task.time:.5f} seconds"
                )
                results.append(result)
                logging.info(result)
            except Exception as e:
                logging.error(f"Error retrieving task result: {e}")

        self._write_results_to_file("data/result_cpp.txt", "Results in C++", results)

    def run_same_tasks_in_python(self):
        logging.info("Results in Python")
        results = []
        for i, task in enumerate(self.tasks_sent):
            task.work()
            result = (
                f"Task {task.identifier} completed, Time: {task.time:.5f} seconds"
            )
            results.append(result)
            logging.info(result)
            error = task.time - self.tasks_received[i].time
            self.errors.append(error)

        self._write_results_to_file("data/result_py.txt", "Results in Python", results)

    def _write_results_to_file(self, filename, header, results):
        try:
            with open(filename, "w") as file:
                file.write(f"{header}\n" + "\n".join(results) + "\n")
        except IOError as e:
            logging.error(f"Error writing to file {filename}: {e}")

if __name__ == "__main__":
    boss = Boss()
    boss.run_put_queue()
    boss.run_get_result()
    boss.run_same_tasks_in_python()
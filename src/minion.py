from queueclient import QueueClient
import numpy as np
import logging
import time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Minion(QueueClient):
    def __init__(self):
        super().__init__()

    def run_queue(self):
        while True:
            try:
                task = self.task_queue.get(timeout=10)
                if task is None:
                    logging.info("Minion received sentinel. Exiting.")
                    break
                logging.info(f"Minion received task: {task.identifier}")
                start_time = time.time()
                task.work()
                end_time = time.time()
                norm_ax = np.linalg.norm(task.a @ task.x)
                norm_b = np.linalg.norm(task.b)
                result_msg = (
                    f"Task {task.identifier} done successfully with norm2(ax) = {norm_ax}, norm2(b) = {norm_b}"
                )
                self.result_queue.put(result_msg)
                logging.info(f"Minion completed task: {task.identifier} in {end_time - start_time:.2f} seconds")
            except Exception as e:
                logging.error(f"Error processing task: {e}")
                error_msg = f"Task failed: {e}"
                self.result_queue.put(error_msg)

if __name__ == "__main__":
    minion = Minion()
    minion.run_queue()
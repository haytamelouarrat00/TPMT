from multiprocessing.managers import BaseManager
from multiprocessing import Queue

class QueueManager(BaseManager):
    pass

# Register queue types
QueueManager.register('TaskQueue', Queue)
QueueManager.register('ResultQueue', Queue)

if __name__ == '__main__':
    # Create queue instances
    task_queue = Queue()
    result_queue = Queue()

    # Re-register with queue instances
    QueueManager.register('get_task_queue', callable=lambda: task_queue)
    QueueManager.register('get_result_queue', callable=lambda: result_queue)

    # Start the manager server
    manager = QueueManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
    server = manager.get_server()
    server.serve_forever()
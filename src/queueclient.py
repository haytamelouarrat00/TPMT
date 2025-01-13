from multiprocessing.managers import BaseManager

class QueueClient:
    def __init__(self):
        # Register with the manager
        BaseManager.register('get_task_queue')
        BaseManager.register('get_result_queue')

        # Connect to the manager server
        self.manager = BaseManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        self.manager.connect()

        # Get the queues
        self.task_queue = self.manager.get_task_queue()
        self.result_queue = self.manager.get_result_queue()
"""
Background threading and tasks (i.e. emailing)
"""

import queue

from sum_zero import app, mail

from flask_mail import Message
from functools import wraps
from threading import Thread


class DaemonThread:
    """
    Simple daemon worker for running asynchronous tasks. Exposes a decorator
    which delays function execution until it is pulled from the task queue
    by the worker's thread. Rather than creating a new thread for each new
    task, the thread will run until the task queue is empty for `timeout`
    seconds. Whenever a new task is added, the daemon will check to see if
    the thread is active and restart it if it is not.

    Example usage:

    daemon = Daemon(timeout=60)
    @daemon.make_async
    def func(...):
        ...

    func(a, b, c) # this will add func(a, b, c) to the task queue

    """
    def __init__(self, timeout=20):
        self.inactive = True
        self._thread = None
        self._queue = queue.Queue()
        self._timeout = timeout

    def make_async(self, runnable):
        @wraps(runnable)
        def task_adder(*args, **kwargs):
            self._add_task(runnable, args, kwargs)
            if self.inactive:
                self.start()
        return task_adder

    def _add_task(self, runnable, args, kwargs):
        # Store the execution context in a dictionary and enqueue
        task = dict(job=runnable, args=args or [], kwargs=kwargs or {})
        self._queue.put(task)

    def _run(self):
        try:
            # Some tasks will require the current app's context
            # We need to recreate this since the task will be on another thread
            with app.app_context():
                while True:
                    task = self._queue.get(timeout=self._timeout)
                    task_job = task.get('job')
                    task_args, task_kwargs = task.get('args', []), task.get('kwargs', {})
                    task_job(*task_args, **task_kwargs)
        except queue.Empty as e:
            # If thread is empty for 'timeout' seconds, Empty exception is raised
            self._thread = None
            return None

    def start(self):
        self._thread = Thread(target=self._run)
        self._thread.start()

daemon = DaemonThread(timeout=60)

@daemon.make_async
def send_email(subject, text_body, html_body, recipients, sender):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    return True

@daemon.make_async
def test(sleep=10):
    import time
    time.sleep(sleep)
    print("Completed")

from multiprocessing import Process, Pipe
from functools import partial
from time import sleep
import logging


# Log information about events
logging.basicConfig(level=logging.INFO, format='%(message)s')


def event(process_name, vector):
    """
    Run an event at process with the specified name.
    Return an updated vector clock.
    """
    vector[process_name] += 1
    logging.info(f'Event happened in process {process_name}: {list(vector.values())}')
    return vector


def send_message(pipe, process_name, vector):
    """
    Send a message from process with the specified name to the specified pipe.
    Return an updated vector clock.
    """
    vector[process_name] += 1
    pipe.send(vector)
    logging.info(f'Message has been sent from process {process_name}: {list(vector.values())}')
    return vector


def recv_message(pipe, process_name, vector):
    """
    Receive a message at process with the specified name from the specified pipe.
    Return an updated vector clock.
    """
    vector[process_name] += 1
    received_vector = pipe.recv()
    for p in vector:
        vector[p] = max(vector[p], received_vector[p])
    logging.info(f'Message has been received at process {process_name}: {list(vector.values())}')
    return vector


def run_process(process_name, vector, actions):
    """
    Run a new process with the specified name, initial vector clock and list of actions.
    """
    print(f'Process {process_name} is running...')
    for action in actions:
        vector = action(vector)
        sleep(0.01)
    print(f'Process {process_name}: {list(vector.values())}')


if __name__ == '__main__':
    # Create pipes for interprocess communication
    pipe_ab, pipe_ba = Pipe()
    pipe_bc, pipe_cb = Pipe()

    # Specify actions (events) for each process_name
    process_actions = {
        'a': [
            partial(send_message, pipe_ab, 'a'),
            partial(send_message, pipe_ab, 'a'),
            partial(event, 'a'),
            partial(recv_message, pipe_ab, 'a'),
            partial(event, 'a'),
            partial(event, 'a'),
            partial(recv_message, pipe_ab, 'a'),
        ],
        'b': [
            partial(recv_message, pipe_ba, 'b'),
            partial(recv_message, pipe_ba, 'b'),
            partial(send_message, pipe_ba, 'b'),
            partial(recv_message, pipe_bc, 'b'),
            partial(event, 'b'),
            partial(send_message, pipe_ba, 'b'),
            partial(send_message, pipe_bc, 'b'),
            partial(send_message, pipe_bc, 'b'),
        ],
        'c': [
            partial(send_message, pipe_cb, 'c'),
            partial(recv_message, pipe_cb, 'c'),
            partial(event, 'c'),
            partial(recv_message, pipe_cb, 'c'),
        ],
    }

    vector = {'a': 0, 'b': 0, 'c': 0}

    # Create 3 processes
    processes = []
    for process_name, actions in process_actions.items():
        processes.append(Process(target=run_process, args=(process_name, vector, actions)))

    # Start processes
    for process in processes:
        process.start()

    # Wait until all processes finish running
    for process in processes:
        process.join()

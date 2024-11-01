from time import sleep

from zaku import TaskQ


def synchrous_rpc(request_data, *, queue):
    """
    This function is a synchronous RPC function that is used to
    send rendering requests to the rendering server and collect
    the response. This is a blocking function that waits for the
    response from the worker before returning.

    Args:
        request_data: The data to send to the worker
        queue: The queue to send the request to. This is a keyword
            argument

    :return:
    """

    from uuid import uuid4

    request_id = str(uuid4())
    temp_queue_name = f"{TaskQ.ZAKU_USER}:lucidsim:rpc-{request_id}"

    temp_queue = TaskQ(name=temp_queue_name)

    # push the request to the queue
    queue.add(
        {
            "request_id": request_id,
            "response_queue": temp_queue_name,
            **request_data,
            # "data": request_data,
        }
    )

    while True:
        with temp_queue.pop() as response:
            if response is not None:
                print("got response!")
                break

            # this blocks till the response is back
            sleep(0.001)

    temp_queue.clear_queue()
    # temp_queue.remove_queue()
    return response


TaskQ.remote_call = lambda self, data: synchrous_rpc(data, queue=self)

import threading
import queue

my_queue = queue.Queue()

def storeInQueue(f):
  def wrapper(*args):
    my_queue.put(f(*args))
  return wrapper

@storeInQueue
def get_name(full_name):
   return full_name, full_name + "he"

threading.Thread(target=get_name, args = ["foo"]).start()
threading.Thread(target=get_name, args = ["bar"]).start()

my_data = my_queue.get()
print(my_data)
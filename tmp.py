import traceback
import sys
def func():
    another_function()
def another_function():
    raise Exception('LOL')

# def lumberstack():
#     traceback.print_stack()
#     # print(repr(traceback.extract_stack()))
#     # print(repr(traceback.format_stack()))
#     print(str(traceback))

try:
    func()
except Exception as e:
    _, val, tb = sys.exc_info()
    print(traceback.print_exception(None, e, tb))
finally:
    print('DONE')
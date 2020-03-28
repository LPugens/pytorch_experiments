import string
import random
import torch
import os

def initialize_torch(args=None):
    if args is not None:
        use_cuda = not args.no_cuda and torch.cuda.is_available()
    else:
        use_cuda = torch.cuda.is_available()

    if args is not None:
        torch.manual_seed(args.seed)

    device = torch.device("cuda" if use_cuda else "cpu")
    return use_cuda, device

def random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))

def create_dir_if_not_exists(dir_name):
    try:
        # Create target Directory
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ") 
    except FileExistsError:
        print("Directory " , dir_name ,  " already exists")
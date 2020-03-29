import string
import random
import torch
import os

def initialize_torch(args=None):
    use_cuda = torch.cuda.is_available()
    if torch.cuda.is_available():
        use_cuda = True
        print('Found CUDA-able. Using CUDA!')
    else:
        print('Not found CUDA-able. Not using CUDA!')
        use_cuda = False

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
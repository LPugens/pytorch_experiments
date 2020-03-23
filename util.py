import torch

def initialize_torch(args=None):
    if args is not None:
        use_cuda = not args.no_cuda and torch.cuda.is_available()
    else:
        use_cuda = torch.cuda.is_available()

    if args is not None:
        torch.manual_seed(args.seed)

    device = torch.device("cuda" if use_cuda else "cpu")
    return use_cuda, device
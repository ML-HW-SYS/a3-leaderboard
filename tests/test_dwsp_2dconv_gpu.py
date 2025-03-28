import tvm
import torch
import pytest
import timeit
import numpy as np
import torch.nn.functional as F
from src.ops import make_dwsp_conv2d_gpu_scheduler


dev = tvm.cuda(0)


def make_func(*args):
    s, A, W, O = make_dwsp_conv2d_gpu_scheduler(*args)
    func = tvm.build(s, [A, W, O], "cuda")
    return func


def ans_torch(a_torch, w_torch):
    B, C, H, W = a_torch.size()
    O, D, K1, K2 = w_torch.size()
    assert K1 == K2
    assert D == 1
    K = K1

    torch.cuda.synchronize()
    b_torch = F.conv2d(
        a_torch, w_torch, bias=None, stride=1,
        padding=((K - 1)//2), dilation=1, groups=C)
    torch.cuda.synchronize()
    return b_torch


@pytest.mark.parametrize('B', [1, 2, 3, 4, 5, 11, 32])
@pytest.mark.parametrize('C', [1, 3, 4, 64])
@pytest.mark.parametrize('H', [1, 3, 4, 128])
@pytest.mark.parametrize('W', [1, 3, 4, 128])
@pytest.mark.parametrize('K', [1, 3, 5])
def test1_M1_N1(B, C, H, W, K):
    # Define dimension
    func = make_func(B, C, H, W, K)

    # Create random test data
    np.random.seed(seed=100)
    a_np = np.random.rand(B, C, H, W).astype(np.float32)
    w_np = np.random.rand(C, 1, K, K).astype(np.float32)

    # Torch input
    a_torch = torch.tensor(a_np).float()
    w_torch = torch.tensor(w_np).float()
    b_np = ans_torch(a_torch, w_torch).detach().numpy()

    a = tvm.nd.array(a_np, dev)
    w = tvm.nd.array(w_np, dev)
    b = tvm.nd.array(np.zeros(tuple(b_np.shape), dtype='float32'), dev)
    func(a, w, b)
    b_out = b.numpy()

    assert b_np.shape == b_out.shape, \
        "Shape mismatch: " + str(b_np.shape) + "\t" + str(b_out.shape)
    assert np.allclose(b_np, b_out), "Value mismatch: %s %s" % (b_np, b_out)
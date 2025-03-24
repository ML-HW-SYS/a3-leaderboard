# Put this in the root directory of the repo
# This code will do the following:
# 1. run all the tests, collect results
# 2. we will run the function of interest for n times with tiemout to gather
#    the wallclock time it takes to complete the function.
# TODO 1: the time only counts if the functionality test passed
#         should output inf if the functionality tests failed
# TODO 2: Should add timeout on all the functions so that early
#         time out won't killed all the rest of the grades
# TODO 3: maybe consider quantizing the results? Now right the variances
#         are very small and not sure whether it means a lots
import torch
import os
import sys
import tvm
import time
import timeit
import numpy as np
import pytest
import subprocess
from tests.test_1dconv_cpu import make_conv1d_cpu_func
from tests.test_1dconv_gpu import make_conv1d_gpu_func
from tests.test_dwsp_2dconv_gpu import make_func as make_dwsp_2dconv_gpu_func
from tests.test_dwsp_2dconv_gpu import ans_torch as dwsp_2dconv_ans
from tests.test_gemm_gpu import make_func as make_gemm_gpu_func


def run_tests(test_file):
    """Run tests and return True if all tests pass, False otherwise."""
    try:
        result = subprocess.run(['python', '-m', 'pytest', test_file, '-v'], 
                               capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def test_speed_gemm_gpu():
    # Check if tests pass first
    if not run_tests('tests/test_gemm_gpu.py'):
        return float('inf')
        
    # Define dimension
    M = 1024
    K = 1024
    N = 1024
    n_repeat = 100
    dev = tvm.cuda(0)

    # Time the optimized implementation
    func = make_gemm_gpu_func(M, K, N)
    def tvm_time():
        # Create random test data
        np.random.seed(seed=int(time.time()))
        a_np = np.random.rand(M, K).astype(np.float32)
        w_np = np.random.rand(K, N).astype(np.float32)
        a = tvm.nd.array(a_np, dev)
        w = tvm.nd.array(w_np, dev)
        b = tvm.nd.array(np.zeros((M, N), dtype='float32'), dev)
        func(a, w, b)
    return timeit.timeit(tvm_time, number=n_repeat)


def test_speed_dwsp_conv2d_gpu():
    # Check if tests pass first
    if not run_tests('tests/test_dwsp_2dconv_gpu.py'):
        return float('inf')
        
    # Define dimension
    B, C, H, W, K = 10, 5, 256, 256, 3
    n_repeat = 100
    dev = tvm.cuda(0)

    # Create random test data
    np.random.seed(seed=1024)
    a_np = np.random.rand(B, C, H, W).astype(np.float32)
    w_np = np.random.rand(C, 1, K, K).astype(np.float32)

    # Torch input
    a_torch = torch.tensor(a_np).float()
    w_torch = torch.tensor(w_np).float()
    b_torch = dwsp_2dconv_ans(a_torch, w_torch)

    # Time the optimized implementation
    func = make_dwsp_2dconv_gpu_func(B, C, H, W, K)
    def tvm_time():
        # Create random test data
        np.random.seed(seed=int(time.time()))
        a_np = np.random.rand(B, C, H, W).astype(np.float32)
        w_np = np.random.rand(C, 1, K, K).astype(np.float32)

        a = tvm.nd.array(a_np, dev)
        w = tvm.nd.array(w_np, dev)
        b = tvm.nd.array(np.zeros(tuple(b_torch.shape), dtype='float32'), dev)
        func(a, w, b)
    return timeit.timeit(tvm_time, number=n_repeat)


def test_speed_conv1d_gpu():
    # Check if tests pass first
    if not run_tests('tests/test_1dconv_gpu.py'):
        return float('inf')
        
    # Define dimension
    M = 1024
    N = 1024
    n_repeat = 100
    func = make_conv1d_gpu_func(M, N)
    dev = tvm.cuda(0)

    def tvm_time():
        # Create random test data
        np.random.seed(seed=1024)
        a_np = np.random.rand(M).astype(np.float32)
        w_np = np.random.rand(N).astype(np.float32)

        # Time the optimized implementation
        a = tvm.nd.array(a_np, dev)
        w = tvm.nd.array(w_np, dev)
        b = tvm.nd.array(np.zeros((M + N - 1), dtype='float32'), dev)
        func(a, w, b)
    time_tvm = timeit.timeit(tvm_time, number=n_repeat)
    return time_tvm


def test_speed_conv1d_cpu():
    # Check if tests pass first
    if not run_tests('tests/test_1dconv_cpu.py'):
        return float('inf')
        
    # Define dimension
    dev = tvm.device('llvm', 0)
    M = 1024
    N = 1024
    n_repeat = 100
    func = make_conv1d_cpu_func(M, N)

    def tvm_time():
        # Create random test data
        np.random.seed(seed=int(time.time()))
        a_np = np.random.rand(M).astype(np.float32)
        w_np = np.random.rand(N).astype(np.float32)

        # Time the optimized implementation
        a = tvm.nd.array(a_np, dev)
        w = tvm.nd.array(w_np, dev)
        b = tvm.nd.array(np.zeros((M + N - 1), dtype='float32'), dev)

        func(a, w, b)

    time_tvm = timeit.timeit(tvm_time, number=n_repeat)
    return time_tvm


if __name__ == "__main__":
    print("-" * 80)
    print("Profiling:")
    print(os.getcwd())

    with open("results.csv", "w") as outf:
        outf.write("op,dev,time(s)\n")
        try:
            conv1d_cpu_time = test_speed_conv1d_cpu()
            print("1DConv, CPU time: %ss" % conv1d_cpu_time )
            outf.write("conv1d,cpu,%s\n" % conv1d_cpu_time)
        except Exception as e:
            print(e)
            print("1DConv, CPU time: inf")
            outf.write("conv1d,cpu,inf\n")

        try:
            conv1d_gpu_time = test_speed_conv1d_gpu()
            print("1DConv, GPU time: %ss" % conv1d_gpu_time )
            outf.write("conv1d,gpu,%s\n" % conv1d_gpu_time)
        except Exception as e:
            print(e)
            print("1DConv, GPU time: inf")
            outf.write("conv1d,gpu,inf\n")

        try:
            dwsp_2dconv_gpu_time = test_speed_dwsp_conv2d_gpu()
            print("DWSPConv2D, GPU time: %ss" % dwsp_2dconv_gpu_time)
            outf.write("DWSPConv2D,gpu,%s\n" % dwsp_2dconv_gpu_time)
        except Exception as e:
            print(e)
            print("DWSPConv2D, GPU time: inf")
            outf.write("DWSPConv2D,gpu,inf\n")

        try:
            gemm_gpu_time = test_speed_gemm_gpu()
            print("GEMM, GPU time: %ss" % gemm_gpu_time)
            outf.write("gemm,gpu,%s\n" % gemm_gpu_time)
        except Exception as e:
            print(e)
            print("GEMM, GPU time: inf")
            outf.write("gemm,gpu,inf\n")
    print("DONE")
    print("-" * 100)

'''
A simplified 3-D Tensor (channels, height, weight) for convolutional neural networks.
'''
class Tensor(object):
    def __init__(self, c, h, w):
        self.c = c
        self.h = h
        self.w = w

    def equals(self, other):
        return self.c == other.c and self.h == other.h and self.w == other.w

'''
Calculate the single-sample inference-time params and FLOPs of a convolutional
neural network with PyTorch-like APIs.

To calculate the params and FLOPs of certain network architecture, CNNCalculator
needs to be inherited and the network needs to be defined as in PyTorch.

For convenience, some basic operators are pre-defined and other modules can be
defined in a similar way. Parameters and FLOPs in Batch Normalization and other
types of layers are also computed. If only Convolutional and Linear layers are
considered, please modify the code.

Refer to `MobileNet.py` for details.
'''
class CNNCalculator(object):
    def __init__(self, all_layer=False):
        self.params = 0
        self.flops = 0
        self.all_layer = all_layer

    def calculate(self, *inputs):
        raise NotImplementedError

    def Conv2d(self, tensor, out_c, size, stride=1, padding=0, groups=1, bias=True):
        in_c = tensor.c
        out_h = (tensor.h - size + 2 * padding) / stride + 1
        out_w = (tensor.w - size + 2 * padding) / stride + 1
        assert in_c % groups == 0 and out_c % groups == 0, 'in_c and out_c must be divisible by groups'
        self.params += out_c * in_c / groups * size * size
        self.flops += out_c * out_h * out_w * in_c / groups * size * size
        if bias:
            self.params += out_c
            self.flops += out_c * out_w * out_h
        return Tensor(out_c, out_h, out_w)

    def BatchNorm2d(self, tensor):
        out_c = tensor.c
        out_h = tensor.h
        out_w = tensor.w
        if self.all_layer:
            self.params += 4 * out_c
            self.flops += 2 * out_c * out_h * out_w
        return Tensor(out_c, out_h, out_w)

    def ReLU(self, tensor):
        out_c = tensor.c
        out_h = tensor.h
        out_w = tensor.w
        if self.all_layer:
            self.flops += out_c * out_h * out_w
        return Tensor(out_c, out_h, out_w)

    def AvgPool2d(self, tensor, size, stride=1, padding=0):
        out_c = tensor.c
        out_h = (tensor.h - size + 2 * padding) / stride + 1
        out_w = (tensor.w - size + 2 * padding) / stride + 1
        if self.all_layer:
            self.flops += out_c * out_h * out_w * size * size
        return Tensor(out_c, out_h, out_w)

    def MaxPool2d(self, tensor, size, stride=1, padding=0):
        out_c = tensor.c
        out_h = (tensor.h - size + 2 * padding) / stride + 1
        out_w = (tensor.w - size + 2 * padding) / stride + 1
        if self.all_layer:
            self.params += out_c * out_h * out_w
            self.flops += out_c * out_h * out_w * size * size
        return Tensor(out_c, out_h, out_w)

    def Linear(self, tensor, out_c):
        in_c = tensor.c
        out_h = tensor.h
        out_w = tensor.w
        assert out_h == 1 and out_w == 1, 'out_h or out_w is greater than 1 in Linear layer.'
        self.params += in_c * out_c
        self.flops += in_c * out_c
        return Tensor(out_c, out_h, out_w)

    def Concat(self, *tensors):
        out_c = 0
        out_h = tensors[0].h
        out_w = tensors[0].w
        for tensor in tensors:
            assert tensor.h == out_h and tensor.w == out_w, 'tensor dimensions mismatch in Concat layer.'
            out_c += tensor.c
        return Tensor(out_c, out_h, out_w)

    def MultiAdd(self, tensor, other):
        assert tensor.equals(other), 'tensor dimensions mismatch in Add layer.'
        out_c = tensor.c
        out_h = tensor.h
        out_w = tensor.w
        if self.all_layer:
            self.flops += out_c * out_h * out_w
        return Tensor(out_c, out_h, out_w)

    def Add(self, tensor, other):
        return self.MultiAdd(tensor, other)

    def Multi(self, tensor, other):
        return self.MultiAdd(tensor, other)
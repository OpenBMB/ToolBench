"""Offline compression regressions; real tensor tests need an installed CPU Torch.

Run with: python -m unittest discover -s tests -p 'test_compression.py' -v
No model, Transformers installation, network access or GPU is needed.
"""
import importlib.util
import itertools
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

try:
    import torch
except ImportError:
    torch = None

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'toolbench/model/compression.py'
MODULE_IDS = itertools.count()


def load_compression(torch_module):
    transformers = types.ModuleType('transformers')
    for name in ['AutoTokenizer', 'AutoModelForCausalLM', 'AutoConfig']:
        setattr(transformers, name, object())
    replacements = {'transformers': transformers, 'torch': torch_module}
    if torch_module is not torch:
        replacements.update({
            'torch.nn': torch_module.nn,
            'torch.nn.functional': torch_module.nn.functional,
        })
    name = f'_toolbench_compression_test_{next(MODULE_IDS)}'
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with patch.dict(sys.modules, replacements):
        spec.loader.exec_module(module)
    return module


class FakeTensor:
    def __init__(self, dtype='float32', device='cpu'):
        self.dtype = dtype
        self.device = device
        self.moves = []
        self.detaches = 0

    def detach(self):
        self.detaches += 1
        return self

    def to(self, *args, **kwargs):
        self.moves.append((args, kwargs))
        return self


class FakeModule:
    def named_children(self):
        return []


class FakeContainer(FakeModule):
    def __init__(self, **children):
        self.__dict__.update(children)

    def named_children(self):
        return [(name, child) for name, child in self.__dict__.items()
                if isinstance(child, FakeModule)]


class FakeLinear(FakeModule):
    def __init__(self):
        self.weight = FakeTensor()
        self.bias = FakeTensor()


class DependencyFreeCompressionTests(unittest.TestCase):
    def setUp(self):
        fake_torch = types.ModuleType('torch')
        fake_torch.Tensor = FakeTensor
        fake_torch.cat = Mock()
        fake_torch.nn = types.ModuleType('torch.nn')
        fake_torch.nn.Module = FakeModule
        fake_torch.nn.Linear = FakeLinear
        fake_torch.nn.functional = types.ModuleType('torch.nn.functional')
        fake_torch.nn.functional.linear = Mock(return_value='output')
        self.module = load_compression(fake_torch)
        self.quantize = self.module.compress
        self.module.compress = Mock(return_value=('quantized', 'scale', (2, 4)))

    def model(self):
        return FakeContainer(block=FakeContainer(projection=FakeLinear()),
                             output=FakeLinear())

    def test_discovery_descends_containers_without_corrupting_prefixes(self):
        self.assertEqual(self.module.get_compressed_list(self.model()),
                         ['block.projection.weight', 'output.weight'])

    def test_conversion_reaches_nested_layers_and_is_idempotent(self):
        model = self.model()
        original_bias = model.block.projection.bias
        self.module.compress_module(model, 'cpu')
        converted = model.block.projection
        self.assertIsInstance(converted, self.module.CLinear)
        self.assertIs(converted.bias, original_bias)
        self.assertEqual(self.module.compress.call_count, 2)
        self.module.compress_module(model, 'cpu')
        self.assertIs(model.block.projection, converted)
        self.assertEqual(self.module.compress.call_count, 2)

    def test_apply_preserves_packed_weights_and_is_idempotent(self):
        model = self.model()
        packed = {'block.projection.weight': ('block',),
                  'output.weight': ('output',)}
        self.module.apply_compressed_weight(model, packed, 'cpu')
        converted = model.block.projection
        self.assertIs(converted.weight, packed['block.projection.weight'])
        self.assertIs(model.output.weight, packed['output.weight'])
        self.module.compress.assert_not_called()
        self.module.apply_compressed_weight(model, packed, 'cpu')
        self.assertIs(model.block.projection, converted)

    def test_forward_decompresses_before_dtype_and_bias_dispatch(self):
        packed = ('quantized', 'scale', (2, 4))
        bias = FakeTensor(dtype='float64')
        layer = self.module.CLinear(packed, bias, 'cpu')
        weight = FakeTensor(dtype='float32')
        self.module.decompress = Mock(return_value=weight)
        inputs = FakeTensor(dtype='float64')
        self.assertEqual(layer.forward(inputs), 'output')
        self.module.decompress.assert_called_once_with(
            packed, self.module.default_compression_config)
        self.assertEqual(inputs.moves, [(('float32',), {})])
        self.assertEqual(bias.moves, [((), {'device': 'cpu', 'dtype': 'float32'})])
        self.module.torch.nn.functional.linear.assert_called_once_with(
            inputs, weight, bias)

    def test_exact_group_multiple_does_not_add_padding(self):
        class ReachedQuantization(Exception):
            pass

        tensor = FakeTensor()
        tensor.shape = (2, 4)
        tensor.view = Mock(side_effect=ReachedQuantization)
        self.module.torch.zeros = Mock(
            side_effect=AssertionError('Group-aligned weights must not be padded'))
        config = self.module.CompressionConfig(8, 4, 1, True)
        with self.assertRaises(ReachedQuantization):
            self.quantize(tensor, config)
        tensor.view.assert_called_once_with((2, 1, 4))
        self.module.torch.zeros.assert_not_called()


@unittest.skipUnless(torch is not None, 'CPU Torch is not installed')
class RealCpuCompressionTests(unittest.TestCase):
    def setUp(self):
        self.module = load_compression(torch)

    def test_round_trip_exact_and_partial_groups(self):
        for symmetric in [True, False]:
            config = self.module.CompressionConfig(8, 4, 1, symmetric)
            for width in [4, 5]:
                with self.subTest(symmetric=symmetric, width=width):
                    weight = torch.linspace(-0.8, 0.9, 2 * width).reshape(2, width)
                    packed = self.module.compress(weight, config)
                    restored = self.module.decompress(packed, config)
                    self.assertEqual(restored.shape, weight.shape)
                    self.assertEqual(restored.dtype, weight.dtype)
                    torch.testing.assert_close(restored, weight, rtol=0.01, atol=0.015)

    def test_packed_forward_bias_dtype_and_tolerance(self):
        weight = torch.tensor([[1., -.5, .25, 0.], [-.2, .6, -1., .8]])
        bias = torch.tensor([.1, -.2], dtype=torch.float64)
        inputs = torch.tensor([[.1, .2, .3, .4], [1., -.5, .3, -.1]],
                              dtype=torch.float64)
        packed = self.module.compress(weight, self.module.default_compression_config)
        layer = self.module.CLinear(packed, bias, 'cpu')
        actual = layer(inputs)
        expected = torch.nn.functional.linear(inputs.float(), weight, bias.float())
        self.assertIs(layer.weight, packed)
        self.assertIs(layer.bias, bias)
        self.assertEqual(actual.dtype, torch.float32)
        self.assertEqual(actual.device.type, 'cpu')
        torch.testing.assert_close(actual, expected, rtol=0.01, atol=0.01)

    def test_raw_parameter_without_bias_is_compressed_once(self):
        weight = torch.nn.Parameter(torch.tensor([[1., -.5, .25, 0.]]))
        layer = self.module.CLinear(weight, device='cpu')
        self.assertIsInstance(layer.weight, tuple)
        inputs = torch.tensor([[.1, .2, .3, .4]])
        expected = torch.nn.functional.linear(inputs, weight)
        torch.testing.assert_close(layer(inputs), expected, rtol=0.01, atol=0.01)

    def test_nested_model_conversion_and_application_are_idempotent(self):
        model = torch.nn.Sequential(
            torch.nn.Sequential(torch.nn.Linear(4, 3)), torch.nn.Linear(3, 2))
        with torch.no_grad():
            for parameter in model.parameters():
                parameter.copy_(torch.linspace(-.5, .5, parameter.numel()).reshape_as(parameter))
        inputs = torch.tensor([[.1, .2, .3, .4], [.4, .3, .2, .1]])
        expected = model(inputs).detach()
        self.assertEqual(self.module.get_compressed_list(model),
                         ['0.0.weight', '1.weight'])
        self.module.compress_module(model, 'cpu')
        converted = model[0][0]
        self.module.compress_module(model, 'cpu')
        self.assertIs(model[0][0], converted)
        self.module.apply_compressed_weight(model, {}, 'cpu')
        self.assertIs(model[0][0], converted)
        torch.testing.assert_close(model(inputs), expected, rtol=0.02, atol=0.015)


if __name__ == '__main__':
    unittest.main(verbosity=2)

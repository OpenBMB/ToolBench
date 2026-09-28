import sys
import types
import unittest


def _module(name):
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


if "pydantic" not in sys.modules:
    pydantic = _module("pydantic")

    class BaseModel:
        pass

    pydantic.BaseModel = BaseModel

if "transformers" not in sys.modules:
    transformers = _module("transformers")
    models = _module("transformers.models")
    llama = _module("transformers.models.llama")
    modeling = _module("transformers.models.llama.modeling_llama")
    transformers.models = models
    models.llama = llama
    llama.modeling_llama = modeling

if "toolbench.utils" not in sys.modules:
    utils = _module("toolbench.utils")
    utils.standardize = lambda name: name
    utils.change_name = lambda name: name

from toolbench.inference.server import process_error


TIMEOUT = (
    "The request to the API has timed out. Please try again later, "
    "or if the issue persists"
)


class ProcessErrorTest(unittest.TestCase):
    def test_a_timeout_is_not_cached(self):
        result, save_cache, switch = process_error(TIMEOUT)
        self.assertEqual(result["error"], "API temporarily not working error...")
        self.assertFalse(save_cache)
        self.assertFalse(switch)

    def test_an_unauthorized_reply_is_still_cached(self):
        result, save_cache, switch = process_error("Unauthorized")
        self.assertEqual(result["error"], "Unauthorized error...")
        self.assertTrue(save_cache)
        self.assertFalse(switch)

    def test_a_normal_payload_is_still_cached(self):
        result, save_cache, switch = process_error({"result": 1})
        self.assertEqual(result["error"], "")
        self.assertTrue(save_cache)
        self.assertFalse(switch)

    def test_a_gateway_failure_is_still_reported(self):
        gateway = "Your Client (working) ---> Gateway (working) ---> API (not working)"
        result, save_cache, switch = process_error(gateway)
        self.assertEqual(result["error"], "API not working error...")
        self.assertFalse(save_cache)
        self.assertFalse(switch)


if __name__ == "__main__":
    unittest.main()

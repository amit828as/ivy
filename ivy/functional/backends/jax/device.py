"""
Collection of Jax device functions, wrapped to fit Ivy syntax and signature.
"""

# global
import os
import jax
import ivy

# local
from ivy.functional.ivy.device import Profiler as BaseProfiler


# Helpers #
# --------#

def _to_array(x):
    if isinstance(x, jax.interpreters.ad.JVPTracer):
        return _to_array(x.primal)
    elif isinstance(x, jax.interpreters.partial_eval.DynamicJaxprTracer):
        return _to_array(x.aval)
    return x


# API #
# ----#

def dev(x, as_str=False):
    if isinstance(x, jax.interpreters.partial_eval.DynamicJaxprTracer):
        return None
    dv = _to_array(x).device_buffer.device
    try:
        dv = dv()
    except:
        pass
    if as_str:
        return dev_to_str(dv)
    return dv


_callable_dev = dev


def to_dev(x, dev=None, out=None):
    if dev is not None:
        cur_dev = dev_to_str(_callable_dev(x))
        if cur_dev != dev:
            x = jax.device_put(x, dev_from_str(dev))
    if ivy.exists(out):
        return ivy.inplace_update(out, x)
    return x


def dev_to_str(dev):
    if isinstance(dev, str):
        return dev
    if dev is None:
        return None
    p, dev_id = (dev.platform, dev.id)
    if p == 'cpu':
        return p
    return p + ':' + str(dev_id)


def dev_from_str(dev):
    if not isinstance(dev, str):
        return dev
    dev_split = dev.split(':')
    dev = dev_split[0]
    if len(dev_split) > 1:
        idx = int(dev_split[1])
    else:
        idx = 0
    return jax.devices(dev)[idx]


clear_mem_on_dev = lambda dev: None


def _dev_is_available(base_dev):
    try:
        jax.devices(base_dev)
        return True
    except RuntimeError:
        return False


def gpu_is_available() -> bool:
    return _dev_is_available('gpu')


def num_gpus():
    try:
        return len(jax.devices('gpu'))
    except RuntimeError:
        return 0


tpu_is_available = lambda: _dev_is_available('tpu')


# noinspection PyMethodMayBeStatic
class Profiler(BaseProfiler):

    def __init__(self, save_dir):
        super(Profiler, self).__init__(save_dir)
        self._save_dir = os.path.join(self._save_dir, 'profile')

    def start(self):
        jax.profiler.start_trace(self._save_dir)

    def stop(self):
        jax.profiler.stop_trace()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

#Global
import mxnet as mx
from typing import Optional, Union

#Local
from ivy.functional.backends.mxnet import _handle_flat_arrays_in_out

def argmax(
    x:mx.ndarray.ndarray.NDArray,
    axis:Optional[int] = None, 
    out : Optional[mx.ndarray.ndarray.NDArray] = None,
    keepdims: bool = False
    ) -> mx.ndarray.ndarray.NDArray:
    return mx.nd.argmax(x,axis=axis,out=out, keepdims=keepdims)


def argmin(
        x: mx.ndarray.ndarray.NDArray,
        axis: Optional[int] = None,
        out: Optional[mx.ndarray.ndarray.NDArray] = None,
        keepdims: bool = False
) -> mx.ndarray.ndarray.NDArray:
    ret = mx.nd.argmin(x, axis=axis, out=out, keepdims=keepdims)
    return ret


@_handle_flat_arrays_in_out
def where(condition, x1, x2):
    x_shape = list(x1.shape)
    condition_shape = list(condition.shape)
    if x_shape == condition_shape:
        res = mx.nd.where(condition, x1, x2)
        return res
    tile_reps = [int(x / c) for x, c in zip(x_shape, condition_shape)]
    tiled_condition = mx.nd.tile(condition, tile_reps)
    return mx.nd.where(tiled_condition, x1, x2)

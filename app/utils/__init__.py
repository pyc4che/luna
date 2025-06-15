import functools

from starlette.requests import Request
from starlette.responses import Response

from typing import Callable, Any, Optional, Tuple, Dict

from fastapi_cache.key_builder import default_key_builder


def unwrap_func(func: Callable[..., Any]) -> Callable[..., Any]:
    while isinstance(func, functools.partial):
        func = func.func
    return func


def safe_key_builder(
    func: Callable[..., Any],
    namespace: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    request: Optional[Request] = None,
    response: Optional[Response] = None,
) -> str:
    base_func = unwrap_func(func)
    return default_key_builder(
        func=base_func,
        namespace=namespace,
        args=args,
        kwargs=kwargs,
        request=request,
        response=response,
    )

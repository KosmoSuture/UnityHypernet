"""Redirect shim — canonical source is hypernet_swarm."""
import sys as _sys
import importlib as _il
_mod = _il.import_module(f"hypernet_swarm.{__name__.rsplit('.', 1)[-1]}")
_sys.modules[__name__] = _mod

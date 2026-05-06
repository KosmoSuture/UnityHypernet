"""Redirect shim - canonical source is hypernet_swarm."""
import importlib as _il

_mod = _il.import_module(f"hypernet_swarm.{__name__.rsplit('.', 1)[-1]}")
globals().update(_mod.__dict__)

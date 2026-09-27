"""Helpers to locate SUMO and build command lines."""

from __future__ import annotations

import os
import shutil
import sys


def sumo_binary(gui: bool = False) -> str:
    name = "sumo-gui" if gui else "sumo"
    try:  # pip package "eclipse-sumo"
        import sumo  # type: ignore
        os.environ.setdefault("SUMO_HOME", sumo.SUMO_HOME)
        path = os.path.join(sumo.SUMO_HOME, "bin", name)
        if os.path.exists(path):
            return path
    except ImportError:
        pass
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ["SUMO_HOME"], "tools")
        if tools not in sys.path:
            sys.path.append(tools)
        path = os.path.join(os.environ["SUMO_HOME"], "bin", name)
        if os.path.exists(path):
            return path
    found = shutil.which(name)
    if found:
        return found
    sys.exit("SUMO not found: install it (pip install eclipse-sumo) or set SUMO_HOME")

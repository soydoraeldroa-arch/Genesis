"""Scope loading and enforcement.

Every network call the agent makes to a target host must go through
is_in_scope() first. load_scope() refuses to return a usable config
unless the file has been hand-edited to set confirmed: true.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import yaml


class ScopeError(Exception):
    pass


@dataclass
class ScopeConfig:
    program_name: str
    platform: str
    authorized_by: str
    in_scope: list = field(default_factory=list)
    out_of_scope: list = field(default_factory=list)
    program_notes: str = ""


REQUIRED_FIELDS = ["program_name", "platform", "authorized_by", "in_scope", "confirmed"]


def load_scope(path: str) -> ScopeConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}

    missing = [k for k in REQUIRED_FIELDS if k not in data]
    if missing:
        raise ScopeError(f"Scope file is missing required field(s): {', '.join(missing)}")

    if data.get("confirmed") is not True:
        raise ScopeError(
            "Scope file has confirmed: false (or unset). Set it to 'confirmed: true' only "
            "after you have personally checked the in_scope list against the program's "
            "current published scope and verified you are an authorized participant. "
            "Refusing to run against any target until then."
        )

    if any("REPLACE_ME" in str(v) for v in (data.get("program_name"), data.get("authorized_by"))):
        raise ScopeError(
            "Scope file still contains placeholder 'REPLACE_ME' values. Fill it in with your "
            "actual program name and platform handle before running."
        )

    return ScopeConfig(
        program_name=data["program_name"],
        platform=data["platform"],
        authorized_by=data["authorized_by"],
        in_scope=data.get("in_scope") or [],
        out_of_scope=data.get("out_of_scope") or [],
        program_notes=data.get("program_notes", ""),
    )


def _match(host: str, pattern: str) -> bool:
    regex = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
    return re.match(regex, host, re.IGNORECASE) is not None


def is_in_scope(host: str, scope: ScopeConfig) -> bool:
    host = host.strip().lower().rstrip(".")
    for pattern in scope.out_of_scope:
        if _match(host, pattern):
            return False
    for pattern in scope.in_scope:
        if _match(host, pattern):
            return True
    return False

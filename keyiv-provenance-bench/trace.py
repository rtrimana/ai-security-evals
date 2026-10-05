"""Deterministic backward tracer for AES key / IV provenance.

Starting from the encryption call (the sink), follow assignments, helper-function
returns and class attributes back to the expression where the key and the IV/nonce
originate, then classify that expression. It never looks at variable names or
comments, only at the code structure.

It plays two roles in this benchmark:
  1. a deterministic baseline to compare models against;
  2. the source of the structured trace that is optionally shown to a model
     (the chain and origin expression, but NOT the classification).

NOTE: the tracer and the case generator were written by the same author for the
same code patterns, so its accuracy on these cases is a consistency check, not
evidence that it generalizes to real-world code.

Usage:
    python trace.py --check          # run the tracer over cases.jsonl and report agreement
    python trace.py cases/c001.py    # print the trace for one file
"""
import argparse
import ast
import json
import sys
from pathlib import Path

from common import verdict_from

CSPRNG_CALLS = {"os.urandom", "secrets.token_bytes", "AESGCM.generate_key"}


class Tracer:
    def __init__(self, source):
        self.tree = ast.parse(source)
        self.parents = {}
        for parent in ast.walk(self.tree):
            for child in ast.iter_child_nodes(parent):
                self.parents[child] = parent

        self.module_assigns = {}   # name -> (value node, line)
        self.functions = {}        # name -> FunctionDef
        self.class_attrs = {}      # class name -> {attr: (value node, line)}
        for node in self.tree.body:
            if self._simple_assign(node):
                self.module_assigns[node.targets[0].id] = (node.value, node.lineno)
            elif isinstance(node, ast.FunctionDef):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                attrs = {}
                for member in node.body:
                    if isinstance(member, ast.FunctionDef) and member.name == "__init__":
                        for stmt in member.body:
                            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                                    and isinstance(stmt.targets[0], ast.Attribute)
                                    and isinstance(stmt.targets[0].value, ast.Name)
                                    and stmt.targets[0].value.id == "self"):
                                attrs[stmt.targets[0].attr] = (stmt.value, stmt.lineno)
                self.class_attrs[node.name] = attrs

    # ---- helpers -----------------------------------------------------------
    @staticmethod
    def _simple_assign(node):
        return (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name))

    def _dotted(self, node):
        """'os.urandom', 'hashlib.sha256().digest', ... or None."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._dotted(node.value)
            return f"{base}.{node.attr}" if base else None
        if isinstance(node, ast.Call):
            base = self._dotted(node.func)
            return f"{base}()" if base else None
        return None

    def _is_const(self, node):
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.BinOp):
            return self._is_const(node.left) and self._is_const(node.right)
        if isinstance(node, ast.UnaryOp):
            return self._is_const(node.operand)
        if isinstance(node, ast.Call):
            if self._dotted(node.func) in {"bytes", "bytes.fromhex", "bytearray"}:
                return all(self._is_const(a) for a in node.args)
        return False

    def _enclosing_function(self, node):
        while node in self.parents:
            node = self.parents[node]
            if isinstance(node, ast.FunctionDef):
                return node
        return None

    def _scope_for(self, func, before_line):
        params = {a.arg for a in func.args.args if a.arg != "self"}
        local_vars = {}
        for stmt in func.body:
            if self._simple_assign(stmt) and stmt.lineno < before_line:
                local_vars[stmt.targets[0].id] = (stmt.value, stmt.lineno)
        owner = self.parents.get(func)
        attrs = self.class_attrs.get(owner.name, {}) if isinstance(owner, ast.ClassDef) else {}
        return {"params": params, "locals": local_vars, "attrs": attrs}

    EMPTY_SCOPE = {"params": set(), "locals": {}, "attrs": {}}

    # ---- classification ------------------------------------------------------
    def _classify_expr(self, node):
        names, env = set(), False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                dotted = self._dotted(sub.func)
                if dotted:
                    names.add(dotted)
            if isinstance(sub, ast.Attribute) and self._dotted(sub) == "os.environ":
                env = True
        text = ast.unparse(node)
        if any(n.startswith("random.") or n == "time.time" for n in names):
            return "predictable", text
        if any(n.startswith("hashlib.") for n in names):
            return "weak_derivation", text
        if names & CSPRNG_CALLS:
            return "csprng", text
        if env or names & {"open", "os.getenv", "input"}:
            return "external", text
        if self._is_const(node):
            return "hardcoded", text
        return "unresolved", text

    def classify(self, node, scope, chain, depth=0):
        """Return (source class, origin expression); append each hop to chain."""
        if depth > 10:
            return "unresolved", ast.unparse(node)

        if isinstance(node, ast.Name):
            name = node.id
            if name in scope["locals"]:
                value, line = scope["locals"][name]
                chain.append(f"line {line}: {name} = {ast.unparse(value)}")
                return self.classify(value, scope, chain, depth + 1)
            if name in scope["params"]:
                chain.append(f"{name} is a parameter of the enclosing function (supplied by the caller)")
                return "external", f"parameter {name}"
            if name in self.module_assigns:
                value, line = self.module_assigns[name]
                chain.append(f"line {line}: {name} = {ast.unparse(value)} (module level)")
                return self.classify(value, self.EMPTY_SCOPE, chain, depth + 1)
            return "unresolved", name

        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "self"):
            if node.attr in scope["attrs"]:
                value, line = scope["attrs"][node.attr]
                chain.append(f"line {line}: self.{node.attr} = {ast.unparse(value)} (in __init__)")
                return self.classify(value, self.EMPTY_SCOPE, chain, depth + 1)
            return "unresolved", ast.unparse(node)

        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in self.functions):
            func = self.functions[node.func.id]
            returns = [s for s in ast.walk(func) if isinstance(s, ast.Return) and s.value is not None]
            if not returns:
                return "unresolved", ast.unparse(node)
            ret = returns[0]
            chain.append(f"line {ret.lineno}: {func.name}() returns {ast.unparse(ret.value)}")
            return self.classify(ret.value, self._scope_for(func, ret.lineno), chain, depth + 1)

        return self._classify_expr(node)

    # ---- sink ------------------------------------------------------------------
    def find_sink(self):
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            dotted = self._dotted(node.func)
            if dotted == "Cipher" and len(node.args) >= 2:
                aes_call, mode_call = node.args[0], node.args[1]
                return aes_call.args[0], mode_call.args[0], mode_call.func.attr, node
            if dotted == "AES.new":
                key = node.args[0]
                mode = (self._dotted(node.args[1]) or "").split("MODE_")[-1]
                iv = None
                for kw in node.keywords:
                    if kw.arg in ("iv", "nonce"):
                        iv = kw.value
                if iv is None and len(node.args) > 2:
                    iv = node.args[2]
                return key, iv, mode, node
            if (isinstance(node.func, ast.Attribute) and node.func.attr == "encrypt"
                    and isinstance(node.func.value, ast.Call)
                    and self._dotted(node.func.value.func) == "AESGCM"):
                return node.func.value.args[0], node.args[0], "GCM", node
        return None

    def trace(self):
        found = self.find_sink()
        if not found:
            return None
        key_node, iv_node, mode, sink = found
        func = self._enclosing_function(sink)
        scope = self._scope_for(func, sink.lineno)
        out = {"mode": mode, "sink": ast.unparse(sink), "sink_line": sink.lineno}
        for label, node in (("key", key_node), ("iv", iv_node)):
            chain = []
            source, origin = self.classify(node, scope, chain)
            out[label] = {"chain": chain, "origin": origin, "source": source}
        unresolved = "unresolved" in (out["key"]["source"], out["iv"]["source"])
        out["verdict"] = ("cannot_determine" if unresolved
                          else verdict_from(out["key"]["source"], out["iv"]["source"]))
        return out


def trace_source(source):
    return Tracer(source).trace()


def render_trace(trace):
    """Text shown to a model in the 'trace' condition. Deliberately omits the
    classification (csprng / hardcoded / ...); the model still has to judge."""
    lines = [f"Encryption call (line {trace['sink_line']}, mode {trace['mode']}): {trace['sink']}"]
    for label, title in (("key", "Key"), ("iv", "IV / nonce")):
        item = trace[label]
        lines.append(f"{title}:")
        for hop in item["chain"]:
            lines.append(f"  - {hop}")
        lines.append(f"  - originates from: {item['origin']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--check", action="store_true", help="compare against cases.jsonl")
    args = ap.parse_args()

    if args.check:
        rows = [json.loads(line) for line in open("cases.jsonl")]
        bad = 0
        for row in rows:
            t = trace_source(Path(row["file"]).read_text())
            got = (t["key"]["source"], t["iv"]["source"], t["verdict"]) if t else None
            want = (row["key_source"], row["iv_source"], row["verdict"])
            if got != want:
                bad += 1
                print(f"MISMATCH {row['id']}: tracer={got} label={want}")
        print(f"{len(rows) - bad}/{len(rows)} cases agree with the labels")
        sys.exit(1 if bad else 0)

    for f in args.files:
        t = trace_source(Path(f).read_text())
        print(json.dumps(t, indent=2))
        print()
        print(render_trace(t))


if __name__ == "__main__":
    main()

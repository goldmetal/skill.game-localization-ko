#!/usr/bin/env python3
"""Check normalized flat JSON catalogs; requires Python 3.9+, no packages."""
import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(path):
    def reject_constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def read_catalog(path):
    data = read_json(path)
    if not isinstance(data, dict) or not data:
        raise ValueError("A catalog must be a non-empty flat JSON object")
    for key, value in data.items():
        if not key or not isinstance(value, str):
            raise ValueError("Catalog IDs must be non-empty and values must be strings")
        key.encode("utf-8", errors="strict")
        value.encode("utf-8", errors="strict")
    return data


def read_exceptions(path):
    data = read_json(path) if path else {}
    if not isinstance(data, dict):
        raise ValueError("Exceptions must be a JSON object")
    for key, entry in data.items():
        fields = {"reason", "source_tokens", "target_tokens"}
        if not key or not isinstance(entry, dict) or set(entry) != fields:
            raise ValueError(f"Invalid exception schema for {key!r}")
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise ValueError(f"An exception requires a reason: {key!r}")
        for name in ("source_tokens", "target_tokens"):
            if not isinstance(entry[name], list) or any(not isinstance(t, str) or not t for t in entry[name]):
                raise ValueError(f"Invalid expected token list for {key!r}")
    return data


def token_spans(value, patterns):
    spans = set()
    for pattern in patterns:
        for match in pattern.finditer(value):
            if match.start() == match.end():
                raise ValueError("Token patterns must not match an empty string")
            spans.add(match.span())
    ordered = sorted(spans)
    for previous, current in zip(ordered, ordered[1:]):
        if current[0] < previous[1]:
            raise ValueError("Token patterns produce overlapping matches; refine the patterns")
    return ordered


def inspect_catalogs(source, target, expressions=(), exceptions=None):
    patterns = [re.compile(p) for p in expressions]
    for pattern in patterns:
        if pattern.search("") is not None:
            raise ValueError("Token patterns must not match an empty string")
    exceptions = exceptions or {}
    if exceptions and not patterns:
        raise ValueError("Token exceptions require at least one token pattern")

    errors = []
    accepted = []
    missing = sorted(source.keys() - target.keys())
    extra = sorted(target.keys() - source.keys())
    if missing:
        errors.append({"type": "missing_ids", "ids": missing})
    if extra:
        errors.append({"type": "extra_ids", "ids": extra})
    for key in sorted(exceptions.keys() - (source.keys() & target.keys())):
        errors.append({"type": "stale_exception", "id": key})

    if patterns:
        for key in sorted(source.keys() & target.keys()):
            left = [source[key][a:b] for a, b in token_spans(source[key], patterns)]
            right = [target[key][a:b] for a, b in token_spans(target[key], patterns)]
            exception = exceptions.get(key)
            if exception:
                if left == right or left != exception["source_tokens"] or right != exception["target_tokens"]:
                    errors.append({"type": "stale_exception", "id": key})
                else:
                    accepted.append({"id": key, "reason": exception["reason"]})
            elif left != right:
                errors.append({"type": "token_mismatch", "id": key,
                               "source_tokens": left, "target_tokens": right})

    characters = set()
    non_nfc = []
    replacement = []
    for key, value in target.items():
        if unicodedata.normalize("NFC", value) != value:
            non_nfc.append(key)
        if "\ufffd" in value:
            replacement.append(key)
        cursor = 0
        for start, end in token_spans(value, patterns):
            characters.update(value[cursor:start])
            cursor = end
        characters.update(value[cursor:])

    def is_hangul(cp):
        return any(a <= cp <= b for a, b in ((0x1100, 0x11FF), (0x3130, 0x318F),
                                            (0xA960, 0xA97F), (0xAC00, 0xD7A3),
                                            (0xD7B0, 0xD7FF)))

    codepoints = sorted(map(ord, characters))
    return {
        "status": "failed" if errors else "passed",
        "source_entries": len(source), "target_entries": len(target),
        "token_check": "ordered_regex_matches" if patterns else "not_checked",
        "errors": errors, "accepted_token_exceptions": accepted,
        "warnings": {"non_nfc_ids": sorted(non_nfc), "replacement_character_ids": sorted(replacement)},
        "display_codepoints": [f"U+{cp:04X}" for cp in codepoints],
        "hangul_codepoints": sum(is_hangul(cp) for cp in codepoints),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--token-pattern", action="append", default=[])
    parser.add_argument("--exceptions", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve() in {
            p.resolve() for p in (args.source, args.target, args.exceptions) if p is not None
        }:
            raise ValueError("The report must not overwrite an input file")
        report = inspect_catalogs(read_catalog(args.source), read_catalog(args.target),
                                  args.token_pattern, read_exceptions(args.exceptions))
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 1 if report["errors"] else 0
    except (OSError, ValueError, re.error) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())

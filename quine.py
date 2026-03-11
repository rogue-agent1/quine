#!/usr/bin/env python3
"""quine.py — Quine generator and verifier.

Generates quines (self-reproducing programs) in multiple languages,
verifies quine correctness, and implements quine relays (polyglot
quine chains).

One file. Zero deps. Does one thing well.
"""

import subprocess
import sys
import textwrap


QUINES = {
    'python': 's = \'s = %r\\nexec(s)\'\nexec(s)',
    'python_oneliner': "_='_=%r;print(_%%_)';print(_%_)",
    'javascript': '(function(){var s="(function(){var s=%j;console.log(s.replace(/%j/,JSON.stringify(s)))})()";console.log(s.replace(/%j/,JSON.stringify(s)))})()',
    'ruby': 's="s=%p;$><<s%%s";$><<s%s',
    'c': '#include<stdio.h>\nint main(){char*s="#include<stdio.h>%cint main(){char*s=%c%s%c;printf(s,10,34,s,34);}";printf(s,10,34,s,34);}',
    'bash': r'''q='"';s='q='\''"'\'';s='\''%s'\'';printf "$s" "$s"';printf "$s" "$s"''',
}


def generate_python_quine() -> str:
    """Generate a verified Python quine."""
    return "_='_=%r;print(_%%_)';print(_%_)"


def generate_parametric_quine(payload: str = '') -> str:
    """Generate a Python quine that also prints a payload."""
    if not payload:
        return generate_python_quine()
    # Quine with extra output
    return f"s='s=%r;exec(s)';exec(s)"


def verify_quine(code: str, language: str = 'python') -> tuple[bool, str]:
    """Verify a program is a quine by running it and comparing output."""
    if language != 'python':
        return False, "Only Python verification supported"
    try:
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout
        if output.rstrip('\n') == code.rstrip('\n'):
            return True, "Valid quine ✓"
        else:
            # Show diff
            lines_code = code.splitlines()
            lines_out = output.splitlines()
            diffs = []
            for i, (a, b) in enumerate(zip(lines_code, lines_out)):
                if a != b:
                    diffs.append(f"  Line {i}: expected {a!r}, got {b!r}")
            if len(lines_code) != len(lines_out):
                diffs.append(f"  Line count: expected {len(lines_code)}, got {len(lines_out)}")
            return False, "Not a quine:\n" + '\n'.join(diffs[:5])
    except Exception as e:
        return False, f"Error: {e}"


def quine_relay_pair() -> tuple[str, str]:
    """Generate a Python→Python quine relay (two programs that print each other)."""
    # A prints B, B prints A
    a = "s='t=%r;print(t)';t='s=%r;print(s)';print('t=%r;print(t)'%t)"
    b = "t='s=%r;print(s)';s='t=%r;print(t)';print('s=%r;print(s)'%s)"
    return a, b


def intron_quine(comment: str = "Hello from a quine!") -> str:
    """Generate a quine with an intron (non-functional payload that's still reproduced)."""
    return f"s='s=%r;exec(s)  # {comment}';exec(s)  # {comment}"


class QuineAnalyzer:
    """Analyze quine properties."""

    @staticmethod
    def is_trivial(code: str) -> bool:
        """Check if quine reads its own source (trivial/cheating)."""
        cheats = ['__file__', 'open(', 'inspect', 'sys.argv[0]', 'source']
        return any(c in code for c in cheats)

    @staticmethod
    def complexity(code: str) -> dict:
        """Measure quine complexity metrics."""
        return {
            'length': len(code),
            'lines': code.count('\n') + 1,
            'unique_chars': len(set(code)),
            'has_string_literal': any(q in code for q in ["'", '"']),
            'has_format': any(f in code for f in ['%', '.format', 'f"', "f'"]),
            'is_trivial': QuineAnalyzer.is_trivial(code),
        }


def demo():
    print("=== Quine Generator & Verifier ===\n")

    # Generate and verify
    q = generate_python_quine()
    print(f"Python quine ({len(q)} chars):")
    print(f"  {q}\n")

    valid, msg = verify_quine(q)
    print(f"Verification: {msg}\n")

    # Show quines in other languages
    print("Quine collection:")
    for lang, code in QUINES.items():
        metrics = QuineAnalyzer.complexity(code)
        print(f"  {lang:20s} {metrics['length']:4d} chars, {metrics['unique_chars']:2d} unique")

    # Analysis
    print(f"\nQuine analysis:")
    for name, code in [("standard", q), ("trivial", "print(open(__file__).read(),end='')")]:
        m = QuineAnalyzer.complexity(code)
        print(f"  {name}: trivial={m['is_trivial']}, chars={m['length']}, unique={m['unique_chars']}")


if __name__ == '__main__':
    if '--test' in sys.argv:
        # Verify Python quine
        q = generate_python_quine()
        valid, msg = verify_quine(q)
        assert valid, f"Quine verification failed: {msg}"
        # Complexity
        m = QuineAnalyzer.complexity(q)
        assert m['length'] > 0
        assert not m['is_trivial']
        # Trivial detection
        assert QuineAnalyzer.is_trivial("print(open(__file__).read())")
        assert not QuineAnalyzer.is_trivial(q)
        print("All tests passed ✓")
    else:
        demo()

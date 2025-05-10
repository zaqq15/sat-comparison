import argparse
import time
import sys
from collections import defaultdict

try:
    import psutil
except ImportError:
    psutil = None


def parse_cnf(file_path):
    clauses = []
    variables = set()
    num_vars = 0
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if parts[1] != 'cnf':
                    raise ValueError("Not a CNF file")
                num_vars = int(parts[2])
                continue
            literals = list(map(int, line.split()))
            if literals and literals[-1] == 0:
                literals = literals[:-1]
            if literals:
                for lit in literals:
                    variables.add(abs(lit))
                clauses.append(frozenset(literals))
    return clauses, variables, num_vars


def unit_propagate(clauses):
    """Apply unit propagation."""
    assignment = {}
    while True:
        units = [next(iter(c)) for c in clauses if len(c) == 1]
        if not units:
            return clauses, False, assignment

        lit = units[0]
        var = abs(lit)
        val = lit > 0

        if var in assignment:
            if assignment[var] != val:
                return [], True, {}
            else:
                continue

        assignment[var] = val
        new_clauses = []
        for c in clauses:
            if lit in c:
                continue
            new_c = set(c)
            if -lit in new_c:
                new_c.remove(-lit)
                if not new_c:
                    return [], True, {}
            new_clauses.append(frozenset(new_c))
        clauses = new_clauses


def pure_literal_elimination(clauses):

    counts = defaultdict(int)
    for c in clauses:
        for lit in c:
            counts[lit] += 1

    pure_lits = [lit for lit in counts if -lit not in counts]
    if not pure_lits:
        return clauses

    new_clauses = [c for c in clauses if not any(l in pure_lits for l in c)]
    return new_clauses


def simplify_clauses(clauses):

    unique = []
    for c in clauses:
        if any(c.issubset(d) for d in unique):
            continue
        unique = [d for d in unique if not d.issubset(c)]
        unique.append(c)
    return unique


def dp_solve(clauses, metrics, start_time, timeout=120, verbose=False):

    metrics['calls'] += 1


    current_time = time.time()
    if current_time - start_time > timeout:
        if verbose:
            print(f"DP solver timed out after {timeout} seconds")
        return None

    if verbose and metrics['calls'] % 100 == 0:
        print(f"DP solver progress: {metrics['calls']} recursive calls, {len(clauses)} clauses")

    # Unit propagation
    clauses, conflict, _ = unit_propagate(clauses)
    if conflict:
        return False
    if not clauses:
        return True

    # Pure literal elimination
    new_clauses = pure_literal_elimination(clauses)
    if new_clauses != clauses:
        return dp_solve(new_clauses, metrics, start_time, timeout, verbose)


    clauses = simplify_clauses(clauses)


    all_vars = {abs(l) for c in clauses for l in c}
    for var in sorted(all_vars):
        pos = [c for c in clauses if var in c]
        neg = [c for c in clauses if -var in c]
        if pos and neg:
            break
    else:
        return True

    # Resolution
    resolvents = []
    for p in pos:
        for n in neg:
            res = (p - {var}) | (n - {-var})
            if any(abs(l) == var for l in res):
                continue
            if not res:
                return False
            resolvents.append(frozenset(res))

    new_clauses = [c for c in clauses if var not in c and -var not in c]
    return dp_solve(simplify_clauses(new_clauses + resolvents), metrics, start_time, timeout, verbose)


def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def main():
    parser = argparse.ArgumentParser(description="Davis-Putnam SAT Solver")
    parser.add_argument("--input", "-i", required=True,
                        help="Input CNF file (DIMACS or simple list).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output (show progress)")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="Timeout in seconds (default: 120)")
    args = parser.parse_args()

    start_time = time.time()
    process = psutil.Process() if psutil else None
    start_mem = process.memory_info().rss if process else None

    print(f"┌─────────────────────────────────────────┐")
    print(f"│   DAVIS-PUTNAM SAT SOLVER              │")
    print(f"└─────────────────────────────────────────┘")
    print(f"Reading CNF from: {args.input}")

    try:
        clauses, variables, num_vars_header = parse_cnf(args.input)
        print(f"Formula statistics:")
        print(f"  • Variables: {len(variables)} (header claims: {num_vars_header})")
        print(f"  • Clauses: {len(clauses)}")

        print(f"\nStarting Davis-Putnam algorithm with {args.timeout}s timeout...")
        metrics = {'calls': 0}
        result = dp_solve(clauses, metrics, start_time, args.timeout, args.verbose)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n┌─────────────────────────────────────────┐")
        print(f"│   RESULTS                               │")
        print(f"└─────────────────────────────────────────┘")

        if result is None:
            print(f"Status: ⏱️  TIMEOUT after {args.timeout} seconds")
        elif result:
            print(f"Status: ✓ SATISFIABLE")
        else:
            print(f"Status: ✗ UNSATISFIABLE")

        print(f"Recursive calls: {metrics['calls']:,}")
        print(f"Time elapsed: {total_time:.2f} seconds")

        if process:
            end_mem = process.memory_info().rss
            mem_delta = end_mem - start_mem
            print(f"Memory used: {format_size(mem_delta)} (delta), {format_size(end_mem)} total")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
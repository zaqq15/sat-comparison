import argparse
import time
import sys

try:
    import psutil
except ImportError:
    psutil = None


def parse_cnf(file_path):

    clauses = []
    variables = set()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('%'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'cnf':
                    continue
                else:
                    raise ValueError("Invalid DIMACS format")
            parts = line.split()
            if parts and parts[-1] == '0':
                parts = parts[:-1]
            clause = set()
            for lit in parts:
                if lit == '0' or lit == '':
                    continue
                lit_val = int(lit)
                clause.add(lit_val)
                variables.add(abs(lit_val))
            if clause:
                clauses.append(clause)
    return clauses, variables


def unit_propagate(clauses):

    assignment = {}
    changed = True
    while changed:
        changed = False
        units = [next(iter(c)) for c in clauses if len(c) == 1]
        for lit in units:
            var = abs(lit);
            val = (lit > 0)
            if var in assignment:
                if assignment[var] != val:
                    return clauses, True
            else:
                assignment[var] = val
            changed = True
            new_clauses = []
            for c in clauses:
                if lit in c:
                    continue
                if -lit in c:
                    new_c = set(c)
                    new_c.remove(-lit)
                    if len(new_c) == 0:
                        return new_clauses + [new_c], True
                    new_clauses.append(new_c)
                else:
                    new_clauses.append(set(c))
            clauses = new_clauses
            break
    return clauses, False


def pure_literal_elimination(clauses):

    counts = {}
    for c in clauses:
        for lit in c:
            counts[lit] = counts.get(lit, 0) + 1
    pure_lits = []
    for lit in list(counts.keys()):
        if -lit not in counts:
            pure_lits.append(lit)
    if not pure_lits:
        return clauses, False
    new_clauses = []
    for c in clauses:
        if any(l in c for l in pure_lits):
            continue
        new_clauses.append(set(c))
    return new_clauses, True


def simplify(clauses, lit):
    """Simplify clauses by assigning lit=True: drop satisfied clauses and remove -lit."""
    new_clauses = []
    for c in clauses:
        if lit in c:
            continue
        if -lit in c:
            new_c = set(c)
            new_c.remove(-lit)
            new_clauses.append(new_c)
        else:
            new_clauses.append(set(c))
    return new_clauses


def dpll_solve(clauses, metrics, start_time, timeout=120, verbose=False):

    metrics['calls'] += 1


    current_time = time.time()
    if current_time - start_time > timeout:
        if verbose:
            print(f"DPLL solver timed out after {timeout} seconds")
        return None


    if verbose and metrics['calls'] % 1000 == 0:
        print(f"DPLL progress: {metrics['calls']:,} recursive calls, {len(clauses)} clauses")

    # Unit propagation
    clauses, conflict = unit_propagate(clauses)
    if conflict:
        return False

    # Pure literal elimination
    clauses, changed = pure_literal_elimination(clauses)
    if changed:
        return dpll_solve(clauses, metrics, start_time, timeout, verbose)


    if not clauses:
        return True
    if any(len(c) == 0 for c in clauses):
        return False

    lit = next(iter(clauses[0]))

    result = dpll_solve(simplify(clauses, lit), metrics, start_time, timeout, verbose)
    if result is None:  # Timeout
        return None
    if result:
        return True


    result = dpll_solve(simplify(clauses, -lit), metrics, start_time, timeout, verbose)
    return result


def format_size(bytes):

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def main():
    parser = argparse.ArgumentParser(description="DPLL SAT solver.")
    parser.add_argument("--input", "-i", required=True,
                        help="Input CNF file (DIMACS).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output (show progress).")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="Timeout in seconds (default: 120)")
    args = parser.parse_args()

    start_time = time.time()
    process = psutil.Process() if psutil else None
    start_mem = process.memory_info().rss if process else None

    print(f"┌─────────────────────────────────────────┐")
    print(f"│   DPLL SAT SOLVER                      │")
    print(f"└─────────────────────────────────────────┘")
    print(f"Reading CNF from: {args.input}")

    try:
        clauses, variables = parse_cnf(args.input)
        print(f"Formula statistics:")
        print(f"  • Variables: {len(variables)}")
        print(f"  • Clauses: {len(clauses)}")

        print(f"\nStarting DPLL algorithm with {args.timeout}s timeout...")
        metrics = {'calls': 0}
        result = dpll_solve(clauses, metrics, start_time, args.timeout, args.verbose)

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
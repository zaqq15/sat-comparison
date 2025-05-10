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
                continue

            parts = line.split()
            if parts and parts[-1] == '0':
                parts = parts[:-1]

            clause = []
            for lit in parts:
                if lit == '' or lit == '0':
                    continue
                try:
                    lit_int = int(lit)
                    clause.append(lit_int)
                    variables.add(abs(lit_int))
                except ValueError:
                    continue

            if clause:
                clauses.append(frozenset(clause))

    return set(clauses), variables


def can_resolve(c1, c2):

    for lit in c1:
        if -lit in c2:
            return lit
    return None


def resolve(c1, c2, lit):

    return frozenset((c1 - {lit}) | (c2 - {-lit}))


def is_tautology(clause):

    for lit in clause:
        if -lit in clause:
            return True
    return False


def pure_resolution(clauses, verbose=False, timeout=120):

    all_clauses = set(clauses)
    if frozenset() in all_clauses:
        return False, 0, "COMPLETED"

    start_time = time.time()
    resolvents_count = 0
    status = "COMPLETED"

    while True:
        if verbose:
            print(f"Current clauses: {len(all_clauses)}")


        if time.time() - start_time > timeout:
            status = "TIMEOUT"
            if verbose:
                print(f"Timeout after {timeout} seconds")
            return None, resolvents_count, status


        new_clauses = set()

        clause_list = list(all_clauses)
        n = len(clause_list)

        for i in range(n):
            for j in range(i + 1, n):
                c1 = clause_list[i]
                c2 = clause_list[j]

                lit = can_resolve(c1, c2)
                if lit is not None:
                    resolvent = resolve(c1, c2, lit)

                    if is_tautology(resolvent):
                        continue

                    if len(resolvent) == 0:
                        if verbose:
                            print("Derived empty clause - UNSAT")
                        return False, resolvents_count + 1, status

                    if resolvent not in all_clauses and resolvent not in new_clauses:
                        new_clauses.add(resolvent)
                        resolvents_count += 1

                        if verbose and resolvents_count % 1000 == 0:
                            print(f"Generated {resolvents_count} resolvents")


        if not new_clauses:
            if verbose:
                print("No more resolvents can be generated - SAT")
            return True, resolvents_count, status


        if verbose:
            print(f"Adding {len(new_clauses)} new clauses")
        all_clauses.update(new_clauses)


def format_size(bytes):

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def main():
    parser = argparse.ArgumentParser(description="Pure Resolution-based SAT solver (CNF).")
    parser.add_argument("--input", "-i", required=True,
                        help="Input CNF file (DIMACS or simple list).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output.")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="Timeout in seconds (default: 120)")
    args = parser.parse_args()

    start_time = time.time()
    process = psutil.Process() if psutil else None
    start_mem = process.memory_info().rss if process else None

    print(f"┌─────────────────────────────────────────┐")
    print(f"│   PURE RESOLUTION SAT SOLVER            │")
    print(f"└─────────────────────────────────────────┘")
    print(f"Reading CNF from: {args.input}")

    try:
        clauses, variables = parse_cnf(args.input)
        print(f"Formula statistics:")
        print(f"  • Variables: {len(variables)}")
        print(f"  • Clauses: {len(clauses)}")

        print(f"\nStarting resolution with {args.timeout}s timeout...")
        satisfiable, steps, status = pure_resolution(clauses, verbose=args.verbose, timeout=args.timeout)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n┌─────────────────────────────────────────┐")
        print(f"│   RESULTS                               │")
        print(f"└─────────────────────────────────────────┘")

        if status == "TIMEOUT":
            print(f"Status: ⏱️  TIMEOUT after {args.timeout} seconds")
        elif satisfiable:
            print(f"Status: ✓ SATISFIABLE")
        else:
            print(f"Status: ✗ UNSATISFIABLE")

        print(f"Resolution steps: {steps:,}")
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
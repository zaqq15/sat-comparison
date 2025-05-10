
from pysat.formula import CNF
import time
import traceback
import argparse
import sys


def benchmark_solver(solver_name, cnf):

    try:

        if solver_name == 'g3':
            from pysat.solvers import Glucose3 as SolverClass
        elif solver_name == 'g4':
            from pysat.solvers import Glucose4 as SolverClass
        elif solver_name == 'cd':
            try:
                from pysat.solvers import Cadical as SolverClass
            except ImportError:
                print(f"Solver {solver_name} (Cadical) not available in your PySAT installation")
                return None, 0
        elif solver_name == 'm22':
            from pysat.solvers import Maplesat as SolverClass
        else:
            print(f"Unknown solver: {solver_name}")
            return None, 0

        print(f"  - Initializing {solver_name} solver...")
        with SolverClass(bootstrap_with=cnf) as solver:
            print(f"  - Solver initialized, starting solve...")
            start_time = time.time()
            result = solver.solve()
            solve_time = time.time() - start_time
            print(f"  - Solve complete: {'SAT' if result else 'UNSAT'} in {solve_time:.4f}s")

            return result, solve_time

    except ImportError as e:
        print(f"Solver {solver_name} not available: {str(e)}")
        return None, 0
    except Exception as e:
        print(f"Error with solver {solver_name}: {str(e)}")
        print(f"Detailed error information:")
        traceback.print_exc()
        return None, 0


def main():

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Benchmark SAT solvers on a CNF formula')
    parser.add_argument("--input", "-i", dest='input_file', required=True, help='Input CNF file in DIMACS format')
    parser.add_argument('--solvers', dest='solvers', default='g3,g4,cd,m22',
                        help='Comma-separated list of solvers to use (default: g3,g4,cd,m22)')
    parser.add_argument('--minimal', action='store_true', help='Run a minimal test with a hardcoded formula')

    args = parser.parse_args()


    if args.minimal:
        run_minimal_test()
        return


    try:
        cnf = CNF(from_file=args.input_file)
        print(f"Successfully loaded CNF with {len(cnf.clauses)} clauses and {cnf.nv} variables")

        if any(len(clause) == 0 for clause in cnf.clauses):
            print("WARNING: CNF contains empty clauses which may cause solver issues")
    except Exception as e:
        print(f"Error loading CNF file: {str(e)}")
        return

    solvers = args.solvers.split(',')

    results = {}

    # Run benchmarks
    for solver_name in solvers:
        print(f"Testing solver: {solver_name}...")
        result, time_taken = benchmark_solver(solver_name, cnf)

        if result is not None:
            results[solver_name] = {
                'result': 'SAT' if result else 'UNSAT',
                'time': time_taken
            }
            print(f"  - Added result for {solver_name}: {results[solver_name]}")

    print("\nResults Summary:")
    if results:
        print(f"{'Algorithm':<15} {'Result':<8} {'Time (s)':<10}")
        print("-" * 40)
        for name, data in results.items():
            print(f"{name:<15} {data['result']:<8} {data['time']:<10.4f}")
    else:
        print("No successful solver runs to report.")


def run_minimal_test():

    print("Running minimal test with hardcoded CNF formula")


    simple_cnf = CNF()
    simple_cnf.append([1, 2])
    simple_cnf.append([-1, 3])

    print(f"Simple CNF created with {len(simple_cnf.clauses)} clauses and {simple_cnf.nv} variables")

    try:
        from pysat.solvers import Glucose3
        print("Testing with Glucose3...")
        with Glucose3(bootstrap_with=simple_cnf) as solver:
            result = solver.solve()
            print(f"Result: {'SAT' if result else 'UNSAT'}")
            if result:
                model = solver.get_model()
                print(f"Model found: {model}")
    except ImportError:
        print("Glucose3 solver not available")
    except Exception as e:
        print(f"Error with Glucose3: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
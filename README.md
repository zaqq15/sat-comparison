# SAT Solver Implementations



This repository contains several SAT (Boolean Satisfiability Problem) solver implementations using different algorithms. Each implementation is designed to evaluate and compare the performance of various SAT solving techniques on CNF (Conjunctive Normal Form) formulas.

## Algorithms Included

| Algorithm | File | Description |
|-----------|------|-------------|
| Pure Resolution | `pure_resolution.py` | Classic resolution-based approach that systematically resolves clauses until reaching a contradiction or fixed point |
| Davis-Putnam | `davis_putnam.py` | Combines variable elimination by resolution with simplification techniques |
| DPLL | `dpll.py` | Davis-Putnam-Logemann-Loveland algorithm with backtracking, unit propagation, and pure literal elimination |
| PySAT Benchmark | `pysat_benchmark.py` | Benchmarking tool for modern SAT solvers via PySAT (Glucose3, Glucose4, CaDiCaL, MapleSAT) |

## Features

- **Uniform Interface**: All solvers share a similar command-line interface
- **Detailed Statistics**: Runtime, memory usage, and search space statistics
- **Timeout Control**: Set maximum runtime to handle complex formulas
- **Pretty Output**: Clear console display of results with Unicode symbols
- **DIMACS Support**: Process standard DIMACS CNF format used by SAT competitions

## Installation

```bash
# Clone the repository
git clone https://github.com/zaqq15/sat-comparison.git
cd sat-solvers

# Install dependencies
pip install psutil

# For PySAT benchmark tool
pip install python-sat
```

## Usage

### Pure Resolution Solver

```bash
python resolution_solver.py --input path/to/cnf_file.cnf [--timeout 120] [--verbose]
```

### Davis-Putnam Solver

```bash
python dp_solver.py --input path/to/cnf_file.cnf [--timeout 120] [--verbose]
```

### DPLL Solver

```bash
python dpll_solver.py --input path/to/cnf_file.cnf [--timeout 120] [--verbose]
```

### PySAT Benchmarking Tool

```bash
python cdcl_solver.py --input path/to/cnf_file.cnf [--solvers g3,g4,cd,m22] [--minimal]
```

## Algorithm Comparison

| Algorithm | Time Complexity | Space Complexity | Strengths | Weaknesses |
|-----------|-----------------|------------------|-----------|------------|
| Pure Resolution | Exponential | Exponential | Complete, theoretically elegant | Inefficient for large formulas |
| Davis-Putnam | Exponential | Exponential | Better than pure resolution | Still impractical for large inputs |
| DPLL | Exponential | Linear | Practical for moderately sized problems | Still exponential in worst case |
| Modern SAT Solvers | Exponential | Linear | Highly optimized for real-world problems | Complex implementations |

## Example Output

```
┌─────────────────────────────────────────┐
│   DPLL SAT SOLVER                      │
└─────────────────────────────────────────┘
Reading CNF from: example.cnf
Formula statistics:
  • Variables: 50
  • Clauses: 218

Starting DPLL algorithm with 120s timeout...

┌─────────────────────────────────────────┐
│   RESULTS                               │
└─────────────────────────────────────────┘
Status: ✓ SATISFIABLE
Recursive calls: 1,342
Time elapsed: 0.89 seconds
Memory used: 4.32 MB (delta), 28.76 MB total
```

## Performance Considerations

- **Pure Resolution**: Only practical for very small instances (typically < 20 variables)
- **Davis-Putnam**: Improved but still limited to small instances (typically < 30 variables)
- **DPLL**: Can handle moderate-sized instances (typically < 100 variables, depending on structure)
- **Modern Solvers**: Can solve instances with thousands of variables, depending on structure



## Acknowledgments

- These implementations are for educational purposes
- Modern SAT solving techniques go far beyond these classical approaches with conflict-driven clause learning (CDCL), sophisticated heuristics, and many optimizations

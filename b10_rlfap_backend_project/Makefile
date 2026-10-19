PY ?= python3

all: generate run analyze plot check

generate:
	$(PY) src/gen_instances.py --count 10 --seed 2026
	$(PY) src/summarize_instances.py

run:
	$(PY) src/run.py --time-limit 30

analyze:
	$(PY) src/analyze_results.py

plot:
	$(PY) src/plot.py

check:
	$(PY) src/check_solutions.py

validate-celar:
	$(PY) src/validate_celar.py --solver Gecode --time-limit 30

clean:
	rm -rf data/dzn results/results.csv results/verification.csv results/raw results/plots results/instance_statistics.csv
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

.PHONY: all generate run analyze plot check validate-celar clean

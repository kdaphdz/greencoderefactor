#!/bin/bash

BASE_DIR="$HOME/greencoderefactor/llm-based"
RESULTS_DIR="$BASE_DIR/results_llmbased"

# Comando de tests
TEST_CMD="python3 -m pytest"

mkdir -p "$RESULTS_DIR"

for i in $(seq 1 30); do
    REPO_DIR="$BASE_DIR/iteration$i/repo"
    ITER_RESULTS="$RESULTS_DIR/iteration$i"

    mkdir -p "$ITER_RESULTS"

    echo "========================================"
    echo "Iteration $i"
    echo "========================================"

    if [ ! -d "$REPO_DIR" ]; then
        echo "ERROR: $REPO_DIR no existe"
        continue
    fi

    cd "$REPO_DIR" || exit 1

    for run in $(seq 1 30); do
        OUTPUT="$ITER_RESULTS/run${run}.txt"

        echo "Iteration $i - Run $run/30"

        perf stat \
            -e power/energy-pkg/ \
            -o "$OUTPUT" \
            $TEST_CMD

        if [ $? -ne 0 ]; then
            echo "WARNING: tests failed in iteration $i, run $run"
        fi
    done
done

echo ""
echo "========================================"
echo "Experimento terminado"
echo "Resultados: $RESULTS_DIR"
echo "========================================"

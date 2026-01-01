# Repository Usage Guide

## Core Development Principles

### 1. Research Integrity First - Fail Fast Philosophy
- **This is a research repo**: Hidden invisible fallbacks are *criminal* to research integrity
- **Failing is fine**: NEVER make code do something secretly without being obvious
- **Stay explicit**: Implicit behavior corrupts experiments and wastes time
- **No silent failures**: Crash immediately on missing configs or invalid states
- **No fallbacks**: Required parameters must be explicitly provided
- **Loud failures**: Better to crash in 1 second than run for 10 hours with wrong behavior
- **Why**: Silent failures waste compute hours and corrupt research results

### 2. Implementation vs Orchestration
- **Implementation (HOW)**: Lives in `src/` modules - reusable functions and core logic
- **Orchestration (WHAT/WHEN)**: Lives in `src/scripts/` - experiment flow and coordination at Python level
- **Bash scripts in `/scripts/`**: Minimal wrappers that just call Python scripts, e.g., `uv run python src/scripts/train.py configs/train/default.yaml`

### 3. Abstraction Guidelines
- **Just the right amount**: Do not over-abstract, aim for clarity over cleverness
- **Consult before major changes**: When introducing new structures/abstractions, ask first
- **Watch for spaghetti**: If code is getting tangled, stop and discuss restructuring

### 4. Script Legibility
- Scripts should read like a story - each line is a meaningful step
- Everything happens in `main()` function
- Clear, sequential flow from config loading to execution

## Script Organization

### Required Config Structure
- All configs **MUST** have `output_dir` field - this is non-negotiable
- All scripts should *only* modify the `output_dir` specified in config (except system-level cache/temp files)

### Recommended Script Interface
```bash
python src/scripts/<script_name>.py configs/<config_file>.yaml --overwrite --debug
```
- **Only two runtime flags are recommended:**
  - `--overwrite`: Whether to overwrite existing `output_dir`
  - `--debug`: Debug mode for temporary testing
- Everything else should be in the config file

### Bash Scripts
- All .sh scripts must be in `scripts/`
- **It is advised to organize with subfolders** based on your project's needs
- Example subfolders (these are just examples - use what makes sense for your project):
  - `scripts/data_generation/`
  - `scripts/training/`
  - `scripts/evaluation/`
- All .sh scripts should be as minimal as possible, mostly they simply keep track of what .py scripts should be ran to recreate the experiment
- **IMPORTANT: Always pass through arguments using `"$@"`** to allow flags like `--overwrite` and `--debug` to be passed from bash to Python
- Example:
  ```bash
  #!/bin/bash
  uv run python src/scripts/train.py configs/train/default.yaml "$@"
  ```
  This allows you to run: `bash scripts/train.sh --overwrite --debug`

### Config Files
- All configs must be in `configs/`
- **It is advised to organize with subfolders** based on your project's needs
- Example subfolders (these are just examples - use what makes sense for your project):
  - `configs/data/`
  - `configs/experiments/`
  - `configs/models/`
- This organization makes it easy to find and manage different types of configs

### Python Scripts
- Orchestration scripts (entry points) live in `src/scripts/`
- Implementation modules live in `src/` (but not in `src/scripts/`)
- All orchestration scripts *must* read in *exactly* a `config_path` argument (required)
- Optional flags: `--overwrite` (default False) and `--debug` (default False)
- All orchestration scripts *must* write *all* results to the `output_dir` mentioned by config (error out if this is not given by the config)
- All orchestration scripts should validate the output directory and handle overwrite logic appropriately
- **All scripts should copy the config YAML file to the output directory immediately after creating it** (recommended to save as `config.yaml` for consistency) - this ensures reproducibility and keeps a record of exact parameters used for each run

## Practical Guidelines

### Config Validation
```python
# Always validate upfront - fail fast!
def validate_config(config):
    # Check for required output_dir FIRST
    if 'output_dir' not in config:
        raise ValueError("FATAL: 'output_dir' is required in config")
    
    # Check other required fields
    required_fields = ['experiment', 'model']  # Add your requirements
    for field in required_fields:
        if field not in config:
            raise ValueError(f"FATAL: '{field}' is required in config")
    
    # Validate nested fields explicitly
    if 'learning_rate' not in config.get('training', {}):
        raise ValueError("FATAL: 'training.learning_rate' is required")
```

### Error Handling
```python
# ❌ BAD: Silent fallback
if config is None:
    print("Warning: config missing")
    return default_value

# ✅ GOOD: Immediate failure
if config is None:
    raise ValueError("FATAL: config is required")

# ✅ GOOD: Exit immediately on critical failures
import sys
if not Path(data_path).exists():
    print(f"Error: Data path {data_path} does not exist!")
    sys.exit(1)
```

### Output Directory Management
```python
# Use the safe init_directory utility from src/utils.py
# IMPORTANT: Scripts in src/scripts/ need to add project root to path first
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils import init_directory

# In your orchestration script
output_dir = init_directory(config['output_dir'], overwrite=args.overwrite)

# Create standard subdirectories
(output_dir / 'figures').mkdir(parents=True, exist_ok=True)
(output_dir / 'results').mkdir(parents=True, exist_ok=True)
(output_dir / 'logs').mkdir(parents=True, exist_ok=True)
```

### Code Organization
- **Reusable utilities**: Put in `src/utils.py` - stateless functions used repetitively
- **Orchestration scripts**: Put in `src/scripts/` - entry points that coordinate experiments
- **Implementation modules**: Put in `src/` - domain-specific logic and classes
- Don't over-modularize - functions that do one complete operation are fine
- Trust framework features (e.g., use HuggingFace's TrainingArguments instead of custom schedulers)

### Resources Directory Usage
The `resources/` folder is for reference materials that inform your research:

- **Git repositories**: Clone external repos you're studying or referencing
- **Papers**: Store PDFs of papers relevant to the research
- **Documentation**: Keep external docs, specifications, or references
- **Examples**: Reference implementations or code samples

```bash
# Example structure
resources/
├── repos/
│   └── some-reference-repo/
├── papers/
│   ├── attention-is-all-you-need.pdf
│   └── scaling-laws.pdf
└── docs/
    └── api-spec.md
```

This folder is gitignored - it's for local reference only, not committed to the repo.

### Scratch Directory Usage
**CRITICAL: NEVER place files directly in `scratch/`!**

- **Always create a subfolder** within `scratch/` for your temporary work: `scratch/{subfolder_name}/`
- **Why this matters**: Direct files in scratch/ create clutter and make it impossible to track what belongs to what task
- **Examples of proper usage:**
  - `scratch/test_visualization/` - for testing plotting code
  - `scratch/debug_model/` - for debugging model behavior
  - `scratch/quick_analysis/` - for one-off data checks
- **Everything in these subfolders is gitignored** (except .gitkeep in scratch/ itself)
- **Clean up subfolders when done** - delete entire subdirectories when the temporary work is complete

```bash
# ✅ CORRECT: Create subfolder for temporary work
mkdir scratch/my_test
touch scratch/my_test/temp_script.py
# ... do your work ...
rm -rf scratch/my_test  # Clean up when done

# ❌ WRONG: Never do this!
touch scratch/temp_script.py  # DO NOT put files directly in scratch/
```

### Running Scripts
Always execute from project root:
```bash
# Standard execution
uv run python src/scripts/train.py configs/experiment.yaml

# With overwrite flag
uv run python src/scripts/train.py configs/experiment.yaml --overwrite

# From activated environment
python src/scripts/evaluate.py configs/eval_config.yaml
```

## Quick Decision Guide
- "Could another experiment reuse this?" → Utility module in `src/`
- "Is this specific to THIS experiment?" → Orchestration script in `src/scripts/`
- "Is this HOW to do something?" → Implementation in `src/` modules
- "Is this WHEN/WHETHER to do something?" → Orchestration in `src/scripts/`

## Standard Script Template
```python
import argparse
import yaml
from pathlib import Path
from src.utils import init_directory

def main(config_path, overwrite=False, debug=False):
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate config - fail fast!
    if 'output_dir' not in config:
        raise ValueError("FATAL: 'output_dir' required in config")
    
    # Initialize output directory with safety checks
    output_dir = init_directory(config['output_dir'], overwrite=overwrite)
    
    # Create standard subdirectories
    (output_dir / 'figures').mkdir(parents=True, exist_ok=True)
    (output_dir / 'results').mkdir(parents=True, exist_ok=True)
    (output_dir / 'logs').mkdir(parents=True, exist_ok=True)
    
    # Debug mode handling
    if debug:
        print(f"DEBUG MODE: Output will be written to {output_dir}")
        # Add any debug-specific behavior
    
    # Your experiment code here
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', type=str, help='Path to config file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite output directory')
    parser.add_argument('--debug', action='store_true', help='Debug mode for testing')
    args = parser.parse_args()
    
    main(args.config_path, args.overwrite, args.debug)
```

## Analysis Scripts Pattern

### Typical Analysis Workflow
Analysis scripts follow a different pattern from experiment scripts. They read existing experiment results and create analysis outputs **within** the experiment directory, without modifying the original experiment data.

**Config Structure for Analysis:**
```yaml
exp_dir: "data/my_experiment/run_001"  # Points to existing experiment
output_dir: "data/my_experiment/run_001/analysis/my_analysis"  # Subdirectory within exp_dir
```

**Key Principles:**
- `exp_dir`: Points to the **experiment directory** containing results to analyze
- `output_dir`: Points to where **analysis outputs** should be saved (typically `exp_dir/analysis/<analysis_name>/`)
- Analysis scripts **never modify** the original experiment data
- `--overwrite` flag only affects the analysis subdirectory, not the experiment itself

**Example Analysis Script:**
```python
def main(config_path, overwrite=False):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if 'exp_dir' not in config:
        raise ValueError("FATAL: 'exp_dir' required for analysis")
    if 'output_dir' not in config:
        raise ValueError("FATAL: 'output_dir' required")

    exp_dir = Path(config['exp_dir'])
    output_dir = Path(config['output_dir'])

    # Check experiment results exist
    results_path = exp_dir / 'results' / 'research_results.json'
    if not results_path.exists():
        raise FileNotFoundError(f"Results not found at {results_path}")

    # Create analysis output directory (only overwrites analysis, not experiment!)
    if output_dir.exists() and not overwrite:
        raise ValueError(f"Analysis output {output_dir} exists. Use --overwrite to replace.")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and analyze results
    with open(results_path, 'r') as f:
        data = json.load(f)

    # ... perform analysis ...

    # Save analysis outputs to output_dir
    plt.savefig(output_dir / 'plot.png')
    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(summary, f)
```

**Example Directory Structure After Analysis:**
```
data/my_experiment/run_001/
├── config.yaml              # Original experiment config (untouched)
├── results/
│   └── research_results.json  # Original results (untouched)
├── logs/                    # Original logs (untouched)
└── analysis/                # Analysis outputs (can be overwritten)
    ├── basic_analysis/
    │   ├── plot.png
    │   └── summary.json
    └── detailed_analysis/
        └── ...
```

**Why This Pattern:**
- Preserves experiment integrity - original data is never modified
- Multiple analyses can be run on the same experiment
- Analysis can be re-run with `--overwrite` without re-running expensive experiments
- Clear separation between experiment data and derived analysis

## Key Takeaways
- **Implementation is HOW. Orchestration is WHAT/WHEN/WHETHER.**
- **Research integrity demands explicit behavior** - no hidden magic
- **Better to crash loudly than fail silently**
- **When in doubt, be explicit and ask before abstracting**

## IMPORTANT
- NEVER create file variations like _v2, _new, _final, _updated. Use git for versioning.
- Always follow the existing project structure as defined in CLAUDE.md
- Config files must specify `output_dir` - this is non-negotiable
- All data outputs go to the path specified in `output_dir` in the config
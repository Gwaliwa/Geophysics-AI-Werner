# Selected reproducibility scripts

These scripts are intended to support transparency for the manuscript without releasing the full operational workflow.

## Files

- `plot_feature_importance.py`  
  Generates a feature-importance figure from the processed feature-importance CSV.

- `summarize_drillhole_validation.py`  
  Summarizes drillhole validation results from either a point-level drillhole CSV or an already summarized validation table.

- `plot_werner_solutions.py`  
  Plots Werner source-solution locations and estimated depths from the processed Werner solutions table.

## Suggested folder placement in GitHub

```text
Geophysics-AI-Werner/
├── data/
├── scripts/
│   ├── plot_feature_importance.py
│   ├── summarize_drillhole_validation.py
│   └── plot_werner_solutions.py
├── figures/
├── outputs/
└── requirements.txt
```

## Example commands

```bash
python scripts/plot_feature_importance.py
python scripts/summarize_drillhole_validation.py
python scripts/plot_werner_solutions.py
```

These scripts use processed outputs only. They do not include the full proprietary preprocessing, inversion, feature-engineering, or modeling workflow.

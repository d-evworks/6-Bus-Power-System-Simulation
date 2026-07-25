# Traditional Workflow Output (raw results)

## Baseline
- Converged: True
- Min voltage (pu): 1.0165
- Max voltage (pu): 1.0229
- Weak buses (outside 0.95-1.05 pu): []
- Max line loading (%): 69.5
- Overloaded lines (>100%): []
- Total active losses (MW): 0.00943

## Load +20%
- Converged: True
- Min voltage (pu): 1.015
- Max voltage (pu): 1.0218
- Weak buses (outside 0.95-1.05 pu): []
- Max line loading (%): 85.2
- Overloaded lines (>100%): []
- Total active losses (MW): 0.01259

## Impedance +30%
- Converged: True
- Min voltage (pu): 1.0154
- Max voltage (pu): 1.0237
- Weak buses (outside 0.95-1.05 pu): []
- Max line loading (%): 69.5
- Overloaded lines (>100%): []
- Total active losses (MW): 0.01226

## PV Removal
- Converged: True
- Min voltage (pu): 1.0139
- Max voltage (pu): 1.02
- Weak buses (outside 0.95-1.05 pu): []
- Max line loading (%): 91.0
- Overloaded lines (>100%): []
- Total active losses (MW): 0.01666

## Combined Stress
- Converged: True
- Min voltage (pu): 1.0092
- Max voltage (pu): 1.02
- Weak buses (outside 0.95-1.05 pu): []
- Max line loading (%): 107.5
- Overloaded lines (>100%): [('Line 0-1', 101.8), ('Line 5-0', 107.5)]
- Total active losses (MW): 0.02959


*(An engineer must manually read every scenario above, cross-reference thresholds themselves, and decide what's actionable. No prioritization or recommendations are provided by this workflow.)*
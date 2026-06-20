## Capacity planning
# Determine if current budget can support production targets
planner = IndustrialSectorBuilder.create_manufacturing_sector()
results = planner.optimize_production(target_output_value=200_000_000)

if not results['success']:
    # Similar to: "Cannot meet SLA with current infrastructure"
    print("Need to increase budget or reduce targets")

# Bottleneck Analysis
# Identify which industry limits growth (like finding system bottleneck)
results = planner.optimize_production(target_output_value=150_000_000)
df = results['results']

# Find industries at capacity (like CPU at 100%)
bottlenecks = df[df['Capacity Utilization'] > 90]
print(f"Bottlenecks: {bottlenecks['Industry'].tolist()}")

## Scaling activity
# Test various growth scenarios (like capacity planning for growth)
sensitivity = planner.sensitivity_analysis(
    base_target=150_000_000,
    variations=[-0.2, 0, 0.2, 0.5, 1.0]  # -20% to +100% demand
)

# Find breaking point (like finding max sustainable load)
max_feasible = sensitivity[sensitivity['Feasible']].iloc[-1]
print(f"Maximum sustainable output: ${max_feasible['Output Target']:,.0f}")

## Resources optimization
# Calculate labor efficiency (like calculating ops cost per request)
print(f"Value per worker: ${results['total_value'] / results['total_labor']:,.2f}")
print(f"Cost per unit output: ${results['total_cost'] / results['total_value']:.4f}")

### Deep dive: Complexe components
## The Constraint Matrix

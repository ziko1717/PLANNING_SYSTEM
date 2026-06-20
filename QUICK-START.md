from industrial_planner import IndustrialPlanner, Industry

# 1. Initialize planner with budget (like setting total cloud budget)
planner = IndustrialPlanner(government_budget=100_000_000)  # $100M

# 2. Define industries (like defining microservices)
planner.add_industry(Industry(
    name="Steel Production",
    fixed_cost=10_000_000,      # CAPEX: plant setup
    variable_cost=500,          # OPEX: per unit cost
    selling_price=800,          # Revenue per unit
    labor_per_unit=0.001,       # Workers per unit
    max_capacity=50_000,        # Throughput limit
    min_production=5_000        # Minimum viable scale
))

# 3. Run optimization (like capacity planning simulation)
results = planner.optimize_production(
    target_output_value=150_000_000,  # GDP target
    export_demand={"Steel Production": 10_000}  # Minimum exports
)

# 4. Analyze results (like reviewing resource allocation)
if results['success']:
    print(f"Total workers needed: {results['total_labor']}")
    print(results['results'])

### Using Pre-built Sectors

from industrial_planner import IndustrialSectorBuilder

# Choose a sector template (like choosing infrastructure templates)
manufacturing = IndustrialSectorBuilder.create_manufacturing_sector()
agricultural = IndustrialSectorBuilder.create_agricultural_sector()    
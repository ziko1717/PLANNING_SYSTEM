"""
Industrial Production Planning System
====================================
A linear programming application for planning an entire productive industry
given government budget constraints and labor requirements.

Author: Planning System v1.0
"""

import numpy as np
from scipy.optimize import linprog
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Industry:
    """
    Data class representing a sub-industry within the productive sector.
    
    Think of this as a production line in a factory - it has:
    - Fixed costs (like machinery, building maintenance)
    - Variable costs (raw materials, energy per unit)
    - Production capacity (throughput limits)
    - Labor requirements (operators needed)
    """
    name: str
    fixed_cost: float  # Government investment needed (like infrastructure setup)
    variable_cost: float  # Cost per unit produced (operational expenses)
    selling_price: float  # Revenue per unit
    labor_per_unit: float  # Workers needed per unit of production
    max_capacity: float  # Maximum production capacity (like plant throughput)
    min_production: float  # Minimum viable production (breakeven point)
    
    def total_cost(self, quantity: float) -> float:
        """Calculate total cost for producing a given quantity"""
        if quantity > 0:
            return self.fixed_cost + (self.variable_cost * quantity)
        return 0.0
    
    def total_revenue(self, quantity: float) -> float:
        """Calculate total revenue from selling quantity"""
        return self.selling_price * quantity
    
    def total_labor(self, quantity: float) -> float:
        """Calculate total labor required"""
        return self.labor_per_unit * quantity


class IndustrialPlanner:
    """
    Main planning engine that optimizes industrial production.
    
    This works like infrastructure capacity planning:
    - We have limited resources (budget = compute resources)
    - We need to meet demand (output = service level)
    - We optimize for efficiency (cost minimization = resource optimization)
    """
    
    def __init__(self, government_budget: float):
        """
        Initialize planner with government budget constraint.
        
        Args:
            government_budget: Total capital available for industrial investment
                              (like total CAPEX + OPEX budget in infrastructure)
        """
        self.budget = government_budget
        self.industries: Dict[str, Industry] = {}
        self.results: Optional[pd.DataFrame] = None
        
    def add_industry(self, industry: Industry) -> None:
        """Register an industry in the planning system"""
        self.industries[industry.name] = industry
    
    def optimize_production(self, target_output_value: float, 
                          export_demand: Optional[Dict[str, float]] = None) -> Dict:
        """
        Optimize production across all industries to meet output targets.
        
        This is the core planning algorithm - think of it like:
        1. Calculate required production quantities
        2. Allocate budget across industries
        3. Determine labor requirements
        
        Args:
            target_output_value: Total value of goods needed (GDP target)
            export_demand: Optional minimum production for specific industries
        
        Returns:
            Dictionary with optimization results
        """
        
        n_industries = len(self.industries)
        if n_industries == 0:
            raise ValueError("No industries defined")
        
        industry_list = list(self.industries.values())
        
        """
        LINEAR PROGRAMMING SETUP
        ========================
        We're solving:
        MINIMIZE: total cost
        SUBJECT TO:
        1. Total cost <= budget
        2. Total production value >= target_output_value
        3. Production >= minimum for each industry
        4. Production <= maximum capacity for each industry
        5. (Optional) Export demands met
        
        This is similar to:
        - Load balancing in distributed systems (minimize cost)
        - Resource allocation with constraints (budget, capacity)
        - Service level agreement (meeting output targets)
        """
        
        # Objective function coefficients (minimize costs)
        # We minimize total cost: fixed_costs + variable_costs * quantity
        c = np.array([ind.variable_cost for ind in industry_list])
        
        # Inequality constraints matrix
        # Format: A_ub * x <= b_ub
        
        # Constraint 1: Total cost <= budget
        # sum(variable_cost_i * x_i + fixed_cost_i) <= budget
        A_ub = [np.array([ind.variable_cost for ind in industry_list])]
        b_ub = [self.budget - sum(ind.fixed_cost for ind in industry_list)]
        
        # Constraint 2: Total production value >= target
        # -sum(selling_price_i * x_i) <= -target
        A_ub.append(-np.array([ind.selling_price for ind in industry_list]))
        b_ub.append(-target_output_value)
        
        # Constraint 3 & 4: Production bounds
        # These are handled as bounds, but we add capacity constraints here
        for i, ind in enumerate(industry_list):
            # Maximum capacity constraint: x_i <= max_capacity
            constraint = np.zeros(n_industries)
            constraint[i] = 1.0
            A_ub.append(constraint)
            b_ub.append(ind.max_capacity)
            
            # Minimum production constraint: -x_i <= -min_production
            constraint = np.zeros(n_industries)
            constraint[i] = -1.0
            A_ub.append(constraint)
            b_ub.append(-ind.min_production)
        
        # Handle export demands (minimum production for specific industries)
        if export_demand:
            for ind_name, min_demand in export_demand.items():
                if ind_name in self.industries:
                    i = industry_list.index(self.industries[ind_name])
                    constraint = np.zeros(n_industries)
                    constraint[i] = -1.0
                    A_ub.append(constraint)
                    b_ub.append(-min_demand)
        
        # Convert to numpy arrays
        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)
        
        # Production quantities must be non-negative
        bounds = [(0, None) for _ in range(n_industries)]
        
        """
        SOLVE OPTIMIZATION PROBLEM
        =========================
        Using Simplex method - similar to solving network flow optimization
        but for industrial production quantities.
        """
        result = linprog(
            c, 
            A_ub=A_ub, 
            b_ub=b_ub,
            bounds=bounds,
            method='highs',  # Modern solver, like using optimized routing algorithm
            options={'disp': False}
        )
        
        if not result.success:
            return {
                'success': False,
                'message': f"Optimization failed: {result.message}\n"
                          f"This means constraints cannot be met - similar to "
                          f"when infrastructure capacity can't meet demand",
                'status': result.status
            }
        
        # Extract results
        quantities = result.x
        self.results = self._compile_results(industry_list, quantities)
        
        return {
            'success': True,
            'total_production': sum(quantities),
            'total_value': sum(ind.selling_price * qty 
                              for ind, qty in zip(industry_list, quantities)),
            'total_cost': sum(ind.total_cost(qty) 
                            for ind, qty in zip(industry_list, quantities)),
            'total_labor': sum(ind.total_labor(qty) 
                             for ind, qty in zip(industry_list, quantities)),
            'budget_utilization': (sum(ind.total_cost(qty) 
                                      for ind, qty in zip(industry_list, quantities)) 
                                 / self.budget * 100),
            'results': self.results
        }
    
    def _compile_results(self, industry_list: List[Industry], 
                        quantities: np.ndarray) -> pd.DataFrame:
        """Compile optimization results into a structured format"""
        data = []
        for ind, qty in zip(industry_list, quantities):
            data.append({
                'Industry': ind.name,
                'Quantity': round(qty, 2),
                'Total Cost': round(ind.total_cost(qty), 2),
                'Revenue': round(ind.total_revenue(qty), 2),
                'Profit': round(ind.total_revenue(qty) - ind.total_cost(qty), 2),
                'Labor Required': round(ind.total_labor(qty), 1),
                'Capacity Utilization': round(qty / ind.max_capacity * 100, 1) 
                                       if ind.max_capacity > 0 else 0
            })
        return pd.DataFrame(data)
    
    def sensitivity_analysis(self, base_target: float, 
                           variations: List[float]) -> pd.DataFrame:
        """
        Perform sensitivity analysis on target output.
        
        Similar to infrastructure load testing:
        - What happens if demand increases by 10%, 20%, etc.?
        - When does the system become infeasible?
        """
        results = []
        for variation in variations:
            target = base_target * (1 + variation)
            result = self.optimize_production(target)
            results.append({
                'Output Target': target,
                'Variation %': variation * 100,
                'Feasible': result['success'],
                'Total Cost': result.get('total_cost', 0),
                'Labor Required': result.get('total_labor', 0),
                'Budget Utilization %': result.get('budget_utilization', 0)
            })
        return pd.DataFrame(results)


class IndustrialSectorBuilder:
    """
    Builder class for creating realistic industrial sectors.
    
    Think of this as defining your infrastructure topology:
    - Each industry is like a service component
    - They have different resource requirements
    - Some are interdependent (through supply chains)
    """
    
    @staticmethod
    def create_manufacturing_sector() -> IndustrialPlanner:
        """Create a sample manufacturing-focused economy"""
        planner = IndustrialPlanner(government_budget=100_000_000)  # $100M budget
        
        # Steel industry - base materials
        planner.add_industry(Industry(
            name="Steel Production",
            fixed_cost=10_000_000,    # Furnace, plant setup
            variable_cost=500,        # Raw materials, energy per ton
            selling_price=800,        # Market price per ton
            labor_per_unit=0.001,     # 1 worker per 1000 tons
            max_capacity=50_000,      # Annual capacity in tons
            min_production=5_000      # Minimum to keep furnace running
        ))
        
        # Automotive - high value manufacturing
        planner.add_industry(Industry(
            name="Automotive Assembly",
            fixed_cost=25_000_000,     # Assembly line setup
            variable_cost=15_000,      # Parts, materials per vehicle
            selling_price=25_000,      # Sale price per vehicle
            labor_per_unit=0.05,       # 20 workers per vehicle (annual)
            max_capacity=10_000,       # Vehicles per year
            min_production=1_000       # Minimum to maintain supply chain
        ))
        
        # Electronics - technology sector
        planner.add_industry(Industry(
            name="Electronics Manufacturing",
            fixed_cost=15_000_000,     # Clean room, equipment
            variable_cost=200,         # Components per unit
            selling_price=500,         # Consumer price
            labor_per_unit=0.002,      # 500 workers per 1000 units
            max_capacity=200_000,      # Units per year
            min_production=20_000      # Minimum to maintain expertise
        ))
        
        return planner
    
    @staticmethod
    def create_agricultural_sector() -> IndustrialPlanner:
        """Create an agriculture-focused economy"""
        planner = IndustrialPlanner(government_budget=50_000_000)
        
        planner.add_industry(Industry(
            name="Grain Production",
            fixed_cost=5_000_000,       # Land preparation, irrigation
            variable_cost=200,          # Seeds, fertilizer per ton
            selling_price=350,          # Market price per ton
            labor_per_unit=0.0005,      # 1 worker per 2000 tons (mechanized)
            max_capacity=100_000,       # Tons annually
            min_production=10_000       # Minimum for food security
        ))
        
        planner.add_industry(Industry(
            name="Livestock Farming",
            fixed_cost=8_000_000,       # Barns, veterinary
            variable_cost=2000,         # Feed, healthcare per animal
            selling_price=3500,         # Sale price per animal
            labor_per_unit=0.02,        # 50 workers per 1000 animals
            max_capacity=20_000,        # Animals per year
            min_production=2_000        # Minimum herd size
        ))
        
        return planner


# ============================================================================
# MAIN EXECUTION EXAMPLE
# ============================================================================

def main():
    """
    Demonstrate the industrial planning system.
    
    This is like running a capacity planning simulation:
    1. Define the system (industries, constraints)
    2. Set performance targets
    3. Run optimization
    4. Analyze results
    """
    
    print("=" * 80)
    print("INDUSTRIAL PRODUCTION PLANNING SYSTEM")
    print("=" * 80)
    
    # Create a manufacturing economy
    print("\n1. Setting up industrial sector...")
    planner = IndustrialSectorBuilder.create_manufacturing_sector()
    
    # Set planning objectives
    target_gdp = 150_000_000  # $150M GDP target
    export_requirements = {
        "Steel Production": 10_000  # Must export at least 10,000 tons of steel
    }
    
    print(f"\n2. Running optimization with:")
    print(f"   - Government budget: ${planner.budget:,.0f}")
    print(f"   - GDP target: ${target_gdp:,.0f}")
    print(f"   - Export requirements: {export_requirements}")
    
    # Perform optimization
    results = planner.optimize_production(target_gdp, export_requirements)
    
    print("\n3. OPTIMIZATION RESULTS:")
    print("-" * 80)
    
    if results['success']:
        print(f"✓ PLAN FEASIBLE")
        print(f"\nSummary Metrics:")
        print(f"  • Total Production Value: ${results['total_value']:,.2f}")
        print(f"  • Total Cost: ${results['total_cost']:,.2f}")
        print(f"  • Budget Utilization: {results['budget_utilization']:.1f}%")
        print(f"  • Total Workers Required: {results['total_labor']:,.0f}")
        print(f"  • Profit (Revenue - Cost): ${results['total_value'] - results['total_cost']:,.2f}")
        
        print(f"\nDetailed Production Plan:")
        print(results['results'].to_string(index=False))
        
        # Sensitivity Analysis
        print(f"\n4. SENSITIVITY ANALYSIS:")
        print("-" * 80)
        print("Testing system response to demand variations...")
        
        sensitivity = planner.sensitivity_analysis(
            target_gdp,
            variations=[-0.2, -0.1, 0, 0.1, 0.2, 0.5, 1.0]
        )
        print(sensitivity.to_string(index=False))
        
        # Identify capacity bottlenecks
        print(f"\n5. CAPACITY ANALYSIS:")
        print("-" * 80)
        for _, row in results['results'].iterrows():
            if row['Capacity Utilization'] > 90:
                print(f"⚠ BOTTLENECK: {row['Industry']} at {row['Capacity Utilization']}% capacity")
            elif row['Capacity Utilization'] < 30:
                print(f"⚠ UNDERUTILIZED: {row['Industry']} at {row['Capacity Utilization']}% capacity")
            else:
                print(f"✓ OPTIMAL: {row['Industry']} at {row['Capacity Utilization']}% capacity")
                
    else:
        print(f"✗ PLAN INFEASIBLE")
        print(f"Error: {results['message']}")
        print("\nSuggestions:")
        print("  1. Increase government budget")
        print("  2. Lower GDP targets")
        print("  3. Improve industry efficiency (reduce variable costs)")
        print("  4. Remove minimum production constraints")
    
    print("\n" + "=" * 80)
    print("PLANNING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
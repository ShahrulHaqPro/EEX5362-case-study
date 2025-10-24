from src.simpy_farm import EggFarmSimulation
from src.visualization import generate_all_plots
import json
import os

def main():
    print("----- Starting Egg Farm Simulation -----")

    # Make a folder for reports if it does not exist
    if not os.path.exists("reports"):
        os.makedirs("reports")
        print("Created folder: reports")
    # else:
    #     print("Folder already exists: reports")

    # scenarios 
    scenarios = {
        "Scenario_A_Slow": 80,
        "Scenario_B_Medium": 120,
        "Scenario_C_Fast": 160
    }

    # results
    results = {}
    queue_histories = {}
    utilization_histories = {}

    # Run each scenario one by one
    for scenario_name in scenarios:
        belt_capacity = scenarios[scenario_name]
        print("\nRunning scenario:", scenario_name)
        print("Belt capacity (eggs/min):", belt_capacity)

        # Create the simulation object
        farm = EggFarmSimulation(
            belt_capacity=belt_capacity,
            hen_count=10000,
            simulation_time=720  # 12 hours (minutes)
        )

        # run the simulation
        try:
            farm.run()
        except Exception as e:
            print("Error while running simulation for", scenario_name)
            print("Error message:", e)
            # skip storing results for this scenario
            continue

        # Getting and storing metrics and histories
        metrics = farm.get_metrics()
        results[scenario_name] = metrics
        queue_histories[scenario_name] = farm.queue_history
        utilization_histories[scenario_name] = farm.utilization_history

        # Print metrics
        eggs_laid = metrics.get("eggs_laid", "N/A")
        eggs_collected = metrics.get("eggs_collected", "N/A")
        eggs_broken = metrics.get("eggs_broken", "N/A")
        breakage_rate = metrics.get("breakage_rate", "N/A")

        print("  * Eggs laid:", eggs_laid)
        print("  * Eggs collected:", eggs_collected)
        print("  * Eggs broken:", eggs_broken)
        if isinstance(breakage_rate, (int, float)):
            print("  * Breakage rate: {:.2%}".format(breakage_rate))
        else:
            print("  * Breakage rate:", breakage_rate)

    # Save results to JSON file
    out_path = "reports/simulation_results.json"
    try:
        json_results = {}
        for scenario in results:
            json_results[scenario] = {}
            metrics = results[scenario]
            for key in metrics:
                value = metrics[key]
                try:
                    json_results[scenario][key] = float(value)
                except Exception:
                    json_results[scenario][key] = value

        with open(out_path, "w") as f:
            json.dump(json_results, f, indent=4)
        print("\nSaved results to:", out_path)
    except Exception as e:
        print("Failed to save results:", e)

    # Generate graphs
    try:
        print("\nGenerating graphs")
        generate_all_plots(results, queue_histories, utilization_histories)
        print("Graphs generated.")
    except Exception as e:
        print("graphs not generated. Error:", e)

    print("\n----- Simulation completed -----")


if __name__ == "__main__":
    main()

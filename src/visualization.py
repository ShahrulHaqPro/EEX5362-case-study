import matplotlib.pyplot as plt


# queue lengths over time 
def plot_queue_analysis(queue_histories):
    plt.figure(figsize=(12, 6))

    colors = {
        'Scenario_A_Slow': 'red',
        'Scenario_B_Medium': 'blue',
        'Scenario_C_Fast': 'green'
    }

    for scenario, history in queue_histories.items():
        # x values in hours
        time_hours = []
        for i in range(len(history)):
            time_hours.append(i / 60.0)

        # Plot the line
        plt.plot(time_hours, history, label=scenario,
                 color=colors.get(scenario, 'black'), alpha=0.8)

    plt.xlabel('Time (hours)')
    plt.ylabel('Queue length (eggs)')
    plt.title('Queue Length Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save
    try:
        plt.savefig('reports/queue_analysis.png', dpi=300, bbox_inches='tight')
    except Exception as e:
        print("Could not save queue_analysis.png:", e)
    plt.close()


# comparison of breakage rate and utilization
def plot_performance_metrics(results):
    scenarios = list(results.keys())
    # x-axis
    scenario_labels = []
    for s in scenarios:
        cap = results.get(s, {}).get('belt_capacity', 'N/A')
        if cap != 'N/A':
            scenario_labels.append('{} ({}/min)'.format(s.split('_')[1] if '_' in s else s, cap))
        else:
            scenario_labels.append(s)

    breakage_rates = []
    utilizations = []
    for s in scenarios:
        br = results.get(s, {}).get('breakage_rate', 0)
        ut = results.get(s, {}).get('utilization', 0)
        breakage_rates.append(br * 100)
        utilizations.append(ut * 100)

    x = list(range(len(scenarios)))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # left axis
    bars = ax1.bar([xi - width/2 for xi in x], breakage_rates, width,
                   label='Breakage Rate (%)', color='tomato', alpha=0.7)
    ax1.set_ylabel('Breakage Rate (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenario_labels, rotation=20, ha='right')

    # right axis
    ax2 = ax1.twinx()
    ax2.plot(x, utilizations, 'o-', linewidth=2, markersize=7, label='Utilization (%)')
    ax2.set_ylabel('Utilization (%)')

    plt.title('Breakage Rate and Utilization by Scenario')

    # value labels  
    for i, val in enumerate(breakage_rates):
        ax1.text(i - width/2, val + 0.2, '{:.1f}%'.format(val), ha='center', fontsize=8)
    for i, val in enumerate(utilizations):
        ax2.text(i, val + 0.8, '{:.1f}%'.format(val), ha='center', fontsize=8)

    fig.tight_layout()
    try:
        plt.savefig('reports/performance_metrics.png', dpi=300, bbox_inches='tight')
    except Exception as e:
        print("Could not save performance_metrics.png:", e)
    plt.close()


# cost chart 
def plot_cost_analysis(results):
    EGG_VALUE = 20  # per egg
    ENERGY_COST_PER_CAPACITY_PER_MIN = 0.3  # Rs per capacity-unit per minute
    SIM_MINUTES = 720  # simulation length in minutes

    scenarios = list(results.keys())
    scenario_labels = []
    for s in scenarios:
        cap = results.get(s, {}).get('belt_capacity', 'N/A')
        if cap != 'N/A':
            scenario_labels.append('{} ({})'.format(s, cap))
        else:
            scenario_labels.append(s)

    breakage_costs = []
    energy_costs = []
    total_costs = []

    for s in scenarios:
        broken = results.get(s, {}).get('eggs_broken', 0)
        capacity = results.get(s, {}).get('belt_capacity', 0)

        break_cost = broken * EGG_VALUE
        energy_cost = capacity * ENERGY_COST_PER_CAPACITY_PER_MIN * SIM_MINUTES
        total = break_cost + energy_cost

        breakage_costs.append(break_cost)
        energy_costs.append(energy_cost)
        total_costs.append(total)

    x = list(range(len(scenarios)))
    width = 0.6

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(x, breakage_costs, width, label='Breakage Cost', color='lightcoral', alpha=0.8)
    ax.bar(x, energy_costs, width, bottom=breakage_costs, label='Energy Cost',
           color='lightsteelblue', alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(scenario_labels, rotation=20, ha='right')
    ax.set_ylabel('Cost (LKR)')
    ax.set_title('Operational Cost by Scenario')
    ax.legend()

    # Add total cost labels
    for i, total in enumerate(total_costs):
        ax.text(i, total + 1, 'RS.{:.1f}'.format(total), ha='center', fontweight='bold', fontsize=9)

    fig.tight_layout()
    try:
        plt.savefig('reports/cost_analysis.png', dpi=300, bbox_inches='tight')
    except Exception as e:
        print("Could not save cost_analysis.png:", e)
    plt.close()


# Call all functions
def generate_all_plots(results, queue_histories, utilization_histories):
    print("Generating queue analysis...")
    plot_queue_analysis(queue_histories)

    print("Generating performance metrics...")
    plot_performance_metrics(results)

    print("Generating cost analysis...")
    plot_cost_analysis(results)

    print("All graphs generated.")

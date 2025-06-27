from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random

app = Flask(__name__)


driver_names = ["Akash", "Bianca", "Carlos", "Deepa", "Elijah", "Fatima", "Gustavo", "Haruki", "Isabella", "Jasper",
 "Kavya", "Liam", "Mei", "Noah", "Olga", "Pablo", "Qiara", "Ravi", "Sofia", "Tariq"]


@app.route('/')
def index():
    return render_template('index.html')

def smart_bus_assignment(num_buses, demand_values):
    num_stops = len(demand_values)
    total_demand = sum(demand_values)
    max_capacity = (total_demand // num_buses) + 10

    assignment = [-1] * num_stops
    bus_loads = [0] * num_buses

    steps = []

    def is_valid(stop_idx, bus_idx):
        return bus_loads[bus_idx] + demand_values[stop_idx] <= max_capacity

    def backtrack(stop_idx):
        if stop_idx == num_stops:
            return True
        for bus_idx in range(num_buses):
            step = {
                "step": f"Trying stop {stop_idx} -> Bus {bus_idx}",
                "load": bus_loads[bus_idx],
                "demand": demand_values[stop_idx],
                "bus": bus_idx,
                "valid": is_valid(stop_idx, bus_idx)
            }
            steps.append(step)

            if is_valid(stop_idx, bus_idx):
                assignment[stop_idx] = bus_idx
                bus_loads[bus_idx] += demand_values[stop_idx]
                if backtrack(stop_idx + 1):
                    return True
                assignment[stop_idx] = -1
                bus_loads[bus_idx] -= demand_values[stop_idx]
        return False

    success = backtrack(0)

    if not success:
        return [], "Couldn't find a valid assignment.", steps, []

    bus_routes = [[] for _ in range(num_buses)]
    for stop_idx, bus_idx in enumerate(assignment):
        bus_routes[bus_idx].append(stop_idx)

    results = []
    visualization_data = []
    for bus_id, route in enumerate(bus_routes):
        total = sum(demand_values[i] for i in route)
        results.append((f"Bus {chr(65 + bus_id)}", str(route), driver_names[bus_id % len(driver_names)], total))
        visualization_data.append({
            "bus": f"Bus {chr(65 + bus_id)}",
            "stops": route,
            "total_demand": total
        })

    return results, "Success", steps, visualization_data

@app.route('/run_scheduler', methods=['POST'])
def run_scheduler():
    try:
        num_buses = int(request.form['num_buses'])
        demand_values = list(map(int, request.form['demand_values'].split(',')))
        result, status, steps, visualization_data = smart_bus_assignment(num_buses, demand_values)
        session['steps'] = steps
        session['visualization_data'] = visualization_data
        session['demand_values'] = demand_values
        session['result'] = result
        session['status'] = status
        return render_template('scheduler_result.html', result=result, status=status)
    except ValueError:
        return "Error: Invalid input"

@app.route('/results')
def results():
    result = session.get('result', [])
    status = session.get('status', 'No results available')
    return render_template('scheduler_result.html', result=result, status=status)

@app.route('/visualize')
def visualize():
    steps = session.get('steps', [])
    visualization_data = session.get('visualization_data', [])
    demand_values = session.get('demand_values', [])
    return render_template('visualize.html', steps=steps, visualization_data=visualization_data, demand_values=demand_values)

if __name__ == "__main__":
    app.run(debug=True)
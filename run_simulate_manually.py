from app.main import simulate, SimulationRequest

req = SimulationRequest(choices=["D", "A", "B", "A", "A"])
res = simulate(req)
print("Ending returned:", res["ending"])
print("Final stats:", res["core_stats"])

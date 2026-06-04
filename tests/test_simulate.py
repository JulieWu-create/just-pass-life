from fastapi.testclient import TestClient
from app.main import app, new_state, apply_delta, resolve_ending

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_initial_state():
    state = new_state()
    assert state["resource"] == 10
    assert state["learning"] == 5
    assert state["stress"] == 5
    assert state["info"] == 3
    assert state["satisfaction"] == 0
    assert state["stability"] == 0

def test_apply_delta():
    state = {"resource": 10, "stress": 5}
    apply_delta(state, {"resource": -3, "stress": 2, "learning": 1})
    assert state["resource"] == 7
    assert state["stress"] == 7
    assert state["learning"] == 1

def test_simulate_validation():
    # Not 5 choices
    response = client.post("/simulate", json={"choices": ["A", "B", "C"]})
    assert response.status_code == 400
    
    # Invalid choice
    response = client.post("/simulate", json={"choices": ["A", "E", "C", "D", "A"]})
    assert response.status_code == 400

def test_simulate_trace_length():
    response = client.post("/simulate", json={"choices": ["A", "B", "C", "D", "A"]})
    assert response.status_code == 200
    res = response.json()
    assert len(res["trace"]) == 5
    assert "ending" in res
    assert "core_stats" in res
    assert "aux_stats" in res

def test_stage_2_conditional_modifier():
    # C in stage 1, D in stage 2. Base D stress is 1. Under C->D, stress should be modified by -1, making delta stress = 0.
    # Initial stress = 5.
    # C in stage 1 stress delta: +1. Stress becomes 6.
    # D in stage 2 stress delta: 1 (base) - 1 (modifier) = 0. Stress remains 6.
    response = client.post("/simulate", json={"choices": ["C", "D", "B", "B", "B"]})
    assert response.status_code == 200
    res = response.json()
    # Let's inspect the trace for stage 2
    stage_2_trace = res["trace"][1]
    assert stage_2_trace["delta"]["stress"] == 0
    assert stage_2_trace["after"]["stress"] == 6

    # D in stage 1, D in stage 2. Under D->D, stress modifier is +1, making delta stress = 2.
    # Initial stress = 5.
    # D in stage 1 stress delta: +2. Stress becomes 7.
    # D in stage 2 stress delta: 1 (base) + 1 (modifier) = 2. Stress becomes 9.
    response = client.post("/simulate", json={"choices": ["D", "D", "B", "B", "B"]})
    assert response.status_code == 200
    res = response.json()
    stage_2_trace = res["trace"][1]
    assert stage_2_trace["delta"]["stress"] == 2
    assert stage_2_trace["after"]["stress"] == 9

def test_ending_priorities():
    # 1. Forced Compromise (被迫妥協型): learning <= 3, stress >= 10, info <= 2
    # choices: D (learning-1=4, stress+2=7, info-1=2), A (learning-3=1, stress+3=10, info+0=2), D (learning+1=2, stress-1=9, info-1=1), A (learning+0=2, stress+2=11, info+0=1), A (stress+3=14)
    response = client.post("/simulate", json={"choices": ["D", "A", "D", "A", "A"]})
    assert response.status_code == 200
    assert response.json()["ending"]["name"] == "被迫妥協型"
    assert response.json()["ending"]["priority"] == 1

    # 2. High Stress (高壓達標型): learning >= 7, stress >= 10
    # Choices: A (learning+2=7, stress+3=8), A (learning-3=4, stress+3=11), C (learning+0=4, stress+0=11), C (learning+2=6, stress+2=13), A (stress+3=16)
    # Let's adjust choices to hit learning >= 7 and stress >= 10:
    # Stage 1: A (learn=7, stress=8)
    # Stage 2: C (learn=9, stress=10)
    # Stage 3: D (learn=10, stress=9)
    # Stage 4: C (learn=12, stress=11)
    # Stage 5: A (learn=12, stress=14)
    response = client.post("/simulate", json={"choices": ["A", "C", "D", "C", "A"]})
    assert response.status_code == 200
    assert response.json()["ending"]["name"] == "高壓達標型"
    assert response.json()["ending"]["priority"] == 2

    # 3. Stable Exploration (穩定探索型): learning >= 7, info >= 6, stress <= 9, satisfaction >= 1
    # Choices: B, D, C, B, D
    # Initial: learn=5, info=3, stress=5, resource=10, sat=0, stab=0
    # S1: B -> learn=6, stress=6, res=9, info=3
    # S2: D -> learn=6, stress=7, res=11, info=5
    # S3: C -> learn=6, stress=7, res=11, info=7, social=1
    # S4: B -> learn=7, stress=8, res=10, info=7
    # S5: D -> learn=7, stress=9, res=10, info=9, sat=1, stab=2, social=2, uncertainty=-1
    # Check if stats: learn=7 >= 7, info=9 >= 6, stress=9 <= 9, sat=1 >= 1. Correct!
    response = client.post("/simulate", json={"choices": ["B", "D", "C", "B", "D"]})
    assert response.status_code == 200
    assert response.json()["ending"]["name"] == "穩定探索型"
    assert response.json()["ending"]["priority"] == 3

    # 4. Delayed Exploration (延後探索型): stability >= 2, satisfaction <= 0, info <= 4
    # Choices: A (learn=7, stress=8, info=4), A (learn=4, stress=11, info=4), D (learn=5, stress=10, info=3), A (learn=5, stress=12, info=3), B (sat=0, stab=3, stress=13) -> hits High Stress first!
    # Wait, let's keep stress <= 9 and learning 4-6 to avoid higher priority endings.
    # We want: learn <= 6 or stress <= 9 (to avoid High Stress and Just Pass).
    # Let's target: learn=5, stress=7, info=3, stability=3, satisfaction=0
    # Stage 1: C (learn=6, stress=6, info=4)
    # Stage 2: C (learn=8, stress=8, info=4) -> Let's avoid C. Let's do B (learn=5, stress=8, info=4)
    # Stage 3: B (learn=5, stress=9, info=5)
    # Let's test standard inputs to find one matching priority 4.
    response = client.post("/simulate", json={"choices": ["A", "A", "D", "A", "B"]})
    # This choice:
    # S1 A -> learn=7, stress=8, info=4
    # S2 A -> learn=4, stress=11, info=4
    # S3 D -> learn=5, stress=10, info=3
    # S4 A -> learn=5, stress=12, info=3
    # S5 B -> sat=0, stab=3, stress=13, learn=5, info=3
    # Fits Priority 1? learn=5 (no, needs <=3)
    # Fits Priority 2? learn=5 (no, needs >=7)
    # Fits Priority 3? learn=5 (no)
    # Fits Priority 4? stability=3 >= 2, sat=0 <= 0, info=3 <= 4 -> YES!
    assert response.json()["ending"]["name"] == "延後探索型"
    assert response.json()["ending"]["priority"] == 4

    # 5. Just Pass / Resource Constrained (剛好及格型／資源受限型): 4 <= learning <= 6, stress >= 8
    # Choices: A, A, A, B, A
    response = client.post("/simulate", json={"choices": ["A", "A", "A", "B", "A"]})
    assert response.status_code == 200
    assert response.json()["ending"]["name"] == "剛好及格型／資源受限型"
    assert response.json()["ending"]["priority"] == 5

    # 6. Average Progress (普通前進型) - fallback
    # Choices: B, B, D, B, D
    # Initial: learn=5, stress=5, info=3
    # S1: B -> learn=6, stress=6, info=3
    # S2: B -> learn=5, stress=8, info=3
    # S3: D -> learn=6, stress=7, info=2
    # S4: B -> learn=7, stress=8, info=2 -> wait, learn=7, stress=8.
    # S5: D -> learn=7, stress=9, info=4, sat=1, stab=2.
    # Fits Priority 3? learn=7, info=4 (no, needs >=6)
    # Fits Priority 4? stability=2, sat=1 (no, needs sat<=0)
    # Fits Priority 5? learn=7 (no, needs 4-6)
    # Hits Average Progress!
    response = client.post("/simulate", json={"choices": ["B", "B", "D", "B", "D"]})
    assert response.status_code == 200
    assert response.json()["ending"]["name"] == "普通前進型"
    assert response.json()["ending"]["priority"] == 6

from copy import deepcopy
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Just Pass Life Rules API",
    version="1.0.0",
    description="《剛好及格的人生》第一版規則引擎 API",
)

CORE_STATS = [
    "resource",
    "learning",
    "stress",
    "info",
    "satisfaction",
    "stability",
]

AUX_STATS = [
    "social_connection",
    "future_uncertainty",
]

INITIAL_STATE = {
    "resource": 10,
    "learning": 5,
    "stress": 5,
    "info": 3,
    "satisfaction": 0,
    "stability": 0,
}

STAGES = {
    "stage_1": {
        "title": "高一段考失利",
        "options": {
            "A": {"label": "報名大型補習班", "delta": {"resource": -4, "learning": 2, "stress": 3, "info": 1}},
            "B": {"label": "買參考書自己讀", "delta": {"resource": -1, "learning": 1, "stress": 1, "info": 0}},
            "C": {"label": "留校問老師", "delta": {"resource": 0, "learning": 1, "stress": 1, "info": 1}},
            "D": {"label": "不補習，維持原本方式", "delta": {"resource": 0, "learning": -1, "stress": 2, "info": -1}},
        },
    },
    "stage_2": {
        "title": "高二上，是否打工",
        "options": {
            "A": {"label": "平日打工三天", "delta": {"resource": 3, "learning": -3, "stress": 3, "info": 0}},
            "B": {"label": "只做假日班", "delta": {"resource": 1, "learning": -1, "stress": 2, "info": 0}},
            "C": {"label": "不打工，專心讀書", "delta": {"resource": -2, "learning": 2, "stress": 2, "info": 0}},
            "D": {"label": "申請校內獎助學金或補助", "delta": {"resource": 2, "learning": 0, "stress": 1, "info": 2}},
        },
    },
    "stage_3": {
        "title": "高二下，大學營隊",
        "options": {
            "A": {"label": "咬牙參加營隊", "delta": {"resource": -4, "learning": -1, "stress": 3, "info": 2, "social_connection": 1}},
            "B": {"label": "只上網查資料", "delta": {"resource": 0, "learning": 0, "stress": 1, "info": 1}},
            "C": {"label": "請老師協助牽線", "delta": {"resource": 0, "learning": 0, "stress": 0, "info": 2, "social_connection": 1}},
            "D": {"label": "這次先不參加，把時間拿去準備考試", "delta": {"resource": 0, "learning": 1, "stress": -1, "info": -1, "future_uncertainty": 1}},
        },
    },
    "stage_4": {
        "title": "高三考前一個月",
        "options": {
            "A": {"label": "在家讀書，盡量硬撐", "delta": {"resource": 0, "learning": 0, "stress": 2, "info": 0}},
            "B": {"label": "去圖書館讀書", "delta": {"resource": -1, "learning": 1, "stress": 1, "info": 0}},
            "C": {"label": "去付費自習室或補習班自修", "delta": {"resource": -3, "learning": 2, "stress": 2, "info": 1}},
            "D": {"label": "用 AI 工具協助整理重點", "delta": {"resource": 0, "learning": 1, "stress": 1, "info": 1}},
        },
    },
    "stage_5": {
        "title": "高三填志願",
        "options": {
            "A": {"label": "照興趣填第一志願", "delta": {"satisfaction": 2, "stability": 0, "stress": 3, "info": 0, "future_uncertainty": 2}},
            "B": {"label": "選較穩定的科系", "delta": {"satisfaction": 0, "stability": 3, "stress": 1, "info": 0, "future_uncertainty": -1}},
            "C": {"label": "聽從親友建議排志願", "delta": {"satisfaction": -1, "stability": 2, "stress": 1, "info": 0, "future_uncertainty": 1}},
            "D": {"label": "查資料並訪談學長姐後折衷排序", "delta": {"satisfaction": 1, "stability": 2, "stress": 1, "info": 2, "future_uncertainty": -1, "social_connection": 1}},
        },
    },
}

class SimulationRequest(BaseModel):
    choices: list[str] = Field(
        ...,
        description="依序填入五關選項，例如 ['B', 'D', 'C', 'B', 'D']",
    )

def new_state() -> dict:
    state = deepcopy(INITIAL_STATE)
    state["social_connection"] = 0
    state["future_uncertainty"] = 0
    return state

def apply_delta(state: dict, delta: dict) -> None:
    for key, value in delta.items():
        state[key] = state.get(key, 0) + value

def resolve_ending(state: dict) -> dict:
    # 順位 1：被迫妥協型
    if state["learning"] <= 3 and state["stress"] >= 10 and state["info"] <= 2:
        return {"name": "被迫妥協型", "priority": 1}
        
    # 順位 2：高壓達標型
    if state["learning"] >= 7 and state["stress"] >= 10:
        return {"name": "高壓達標型", "priority": 2}
        
    # 順位 3：穩定探索型
    if (
        state["learning"] >= 7
        and state["info"] >= 6
        and state["stress"] <= 9
        and state["satisfaction"] >= 1
    ):
        return {"name": "穩定探索型", "priority": 3}
        
    # 順位 4：延後探索型
    if state["stability"] >= 2 and state["satisfaction"] <= 0 and state["info"] <= 4:
        return {"name": "延後探索型", "priority": 4}
        
    # 順位 5：剛好及格型／資源受限型
    if 4 <= state["learning"] <= 6 and state["stress"] >= 8:
        return {"name": "剛好及格型／資源受限型", "priority": 5}
        
    # 順位 6：普通前進型
    return {"name": "普通前進型", "priority": 6}

@app.post("/simulate")
def simulate(payload: SimulationRequest) -> dict:
    if len(payload.choices) != 5:
        raise HTTPException(status_code=400, detail="choices 必須剛好包含五個選項。")
        
    state = new_state()
    trace = []
    previous_choice = None
    
    for stage_index, option_id in enumerate(payload.choices, start=1):
        stage_key = f"stage_{stage_index}"
        stage = STAGES[stage_key]
        
        if option_id not in stage["options"]:
            raise HTTPException(
                status_code=400,
                detail=f"{stage_key} 不接受選項 {option_id}，僅接受 A/B/C/D。",
            )
            
        before = deepcopy(state)
        delta = deepcopy(stage["options"][option_id]["delta"])
        
        # Second stage conditional stress adjustment
        if stage_key == "stage_2" and option_id == "D":
            if previous_choice == "C":
                delta["stress"] = delta.get("stress", 0) - 1
            elif previous_choice == "D":
                delta["stress"] = delta.get("stress", 0) + 1
                
        apply_delta(state, delta)
        
        trace.append({
            "stage": stage_key,
            "title": stage["title"],
            "choice": option_id,
            "choice_label": stage["options"][option_id]["label"],
            "delta": delta,
            "before": before,
            "after": deepcopy(state),
        })
        
        previous_choice = option_id
        
    ending = resolve_ending(state)
    
    return {
        "spec_version": "script-lock-2026-06-03",
        "core_stats": {key: state[key] for key in CORE_STATS},
        "aux_stats": {key: state[key] for key in AUX_STATS},
        "ending": ending,
        "trace": trace,
    }

@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

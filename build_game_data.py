import re
import json
import os

def normalize_text(text):
    text = text.replace("她", "他")
    replacements = {
        # CJK Radicals Supplement
        "\u2e9f": "母", # ⺟
        "\u2ec4": "西", # ⻄
        "\u2ed1": "長", # ⻑
        # Kangxi Radicals
        "\u2f00": "一", # ⼀
        "\u2f06": "二", # ⼆
        "\u2f08": "人", # ⼈
        "\u2f0a": "入", # ⼊
        "\u2f12": "力", # ⼒
        "\u2f17": "十", # ⼗
        "\u2f1c": "又", # ⼜
        "\u2f1d": "口", # ⼝
        "\u2f26": "子", # ⼦
        "\u2f29": "小", # ⼩
        "\u2f30": "己", # ⼰
        "\u2f32": "干", # ⼲
        "\u2f3c": "心", # ⼼
        "\u2f3f": "手", # ⼿
        "\u2f40": "支", # ⽀
        "\u2f42": "文", # ⽂
        "\u2f45": "方", # ⽅
        "\u2f47": "日", # ⽇
        "\u2f50": "比", # ⽐
        "\u2f54": "水", # ⽔
        "\u2f5a": "片", # ⽚
        "\u2f63": "生", # ⽣
        "\u2f64": "用", # ⽤
        "\u2f69": "白", # ⽩
        "\u2f6c": "目", # ⽬
        "\u2f70": "示", # ⽰
        "\u2f72": "禾", # ⽲
        "\u2f74": "立", # ⽴
        "\u2f7c": "老", # ⽼
        "\u2f7d": "而", # ⽽
        "\u2f7f": "耳", # ⽿
        "\u2f83": "自", # ⾃
        "\u2f84": "至", # ⾄
        "\u2f8a": "色", # ⾊
        "\u2f8f": "行", # ⾏
        "\u2f92": "見", # ⾒
        "\u2f93": "角", # ⾓
        "\u2f9c": "足", # ⾜
        "\u2f9d": "身", # ⾝
        "\u2f9e": "車", # ⾞
        "\u2f9f": "辛", # ⾟
        "\u2fa6": "金", # ⾦
        "\u2fa8": "門", # ⾨
        "\u2fae": "非", # ⾮
        "\u2faf": "面", # ⾯
        "\u2fb3": "音", # ⾳
        "\u2fb4": "頁", # ⾴
        "\u2fb5": "風", # ⾵
        "\u2fbc": "高", # ⾼
        "\u2fc8": "黃", # ⿈
        "\u2fca": "黑", # ⿊
        "\u2fce": "鼓", # ⿎
        "\u2fcf": "鼠", # ⿏
        "\u2fd1": "齊", # ⿑
        "\u2fd3": "龍", # ⿓
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def clean_paragraphs(lines):
    # Chinese sentence-ending punctuation marks
    ending_punctuation = re.compile(r'[。！？」』…”）\.\!\?]$')
    
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            cleaned_lines.append("")
            continue
        if "Page " in l and "===" in line:
            continue
        if l == "============================================================":
            continue
        if re.match(r'^(?:Page|Table)\s*\d+', l, re.IGNORECASE):
            continue
        cleaned_lines.append(l)
        
    result = []
    current_para = []
    for line in cleaned_lines:
        if not line:
            if current_para and ending_punctuation.search(current_para[-1]):
                result.append("".join(current_para))
                current_para = []
        else:
            # Dialogue/narrator prefix triggers a new paragraph to prevent run-on issues
            if current_para and (line.startswith("「") or 
                                 line.endswith("：") or 
                                 line.endswith(":") or
                                 re.match(r"^(?:同學|老師|店長|媽媽|林予安|陳佳禾|黃以真|主角)[\:\：]", line) or
                                 re.match(r"^[A-D]\.", line) or 
                                 re.match(r"^選項\s*[A-D]", line)):
                result.append("".join(current_para))
                current_para = []
            current_para.append(line)
            
    if current_para:
        result.append("".join(current_para))
        
    return "\n\n".join(result)

def clean_conclusion(text):
    text = re.sub(r'系統文字\s*[\:\：]?', '', text)
    text = re.sub(r'--- Table \d+ on Page \d+ ---', '', text, flags=re.IGNORECASE)
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            cleaned_lines.append("")
            continue
        if '\t' in l or '|' in l:
            continue
        if l.startswith(('選項', '角色', '張宇翔｜', '林予安｜', '陳佳禾｜', '黃以真｜')):
            continue
        if re.match(r'^[A-D]\s*[\.．\s]', l):
            continue
        if l.startswith(('最後進入下一關', '最後進入下一關：', '最後進入結局畫面')):
            continue
        if 'Table' in l and 'Page' in l:
            continue
        cleaned_lines.append(l)
        
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()

def deep_clean_text(text):
    if not text or not isinstance(text, str):
        return text
    
    text = re.sub(r'---\s*Table\s+\d+\s+on\s+Page\s+\d+\s*---', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Table\s+\d+\s+on\s+Page\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:^|\n)Page\s*\d+(?:\n|$)', '\n', text)
    text = re.sub(r'Page\s*\d+', '', text)
    text = re.sub(r'={10,}', '', text)
    text = re.sub(r'\n?狀態[\t\s]+變化[\s\S]*?(?=\n[^\t]|$)', '', text)
    text = re.sub(r'\n+(?:主角結果)?\s*狀態\s+變化[\s\S]*$', '', text)
    text = re.sub(r'\n?(?:資源|學習力|壓力|資訊感|滿意度|穩定度)\s{2,}[\+\-]?\d+', '', text)
    text = re.sub(r'\s*影子角色\s*$', '', text)
    text = re.sub(r'系統文字\s*[\:\：]?', '', text)
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def deep_clean_all(obj, key=None):
    if isinstance(obj, str):
        if key == "delta":
            # For delta, we only want to strip it, not run deep_clean_text which removes stats!
            return obj.strip()
        return deep_clean_text(obj)
    elif isinstance(obj, dict):
        return {k: deep_clean_all(v, k) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean_all(item, key) for item in obj]
    return obj

def extract_section(text, start_pattern, end_patterns):
    start_match = re.search(start_pattern, text)
    if not start_match:
        return "", -1
    
    start_idx = start_match.end()
    
    earliest_end_idx = len(text)
    for ep in end_patterns:
        end_match = re.search(ep, text[start_idx:])
        if end_match:
            end_idx = start_idx + end_match.start()
            if end_idx < earliest_end_idx:
                earliest_end_idx = end_idx
                
    return text[start_idx:earliest_end_idx].strip(), start_idx

def clean_shadows_text(text):
    text = re.sub(r'---\s*Table\s*\d+\s*on\s*Page\s*\d+\s*---[\s\S]*?(?:={10,}\s*Page\s*\d+\s*={10,}|\Z)', '', text)
    text = re.sub(r'={10,}\s*Page\s*\d+\s*={10,}', '', text)
    return text

def split_by_3spaces(line):
    parts = []
    idx_cursor = 0
    while idx_cursor < len(line):
        while idx_cursor < len(line) and line[idx_cursor].isspace():
            idx_cursor += 1
        if idx_cursor >= len(line):
            break
        start_pos = idx_cursor
        match_spaces = re.search(r'\s{3,}', line[start_pos:])
        if match_spaces:
            end_pos = start_pos + match_spaces.start()
            idx_cursor = start_pos + match_spaces.end()
        else:
            end_pos = len(line)
            idx_cursor = len(line)
        part_text = line[start_pos:end_pos].strip()
        if part_text:
            parts.append((part_text, start_pos))
    return parts

def split_by_2spaces(line):
    parts = []
    idx_cursor = 0
    while idx_cursor < len(line):
        while idx_cursor < len(line) and line[idx_cursor].isspace():
            idx_cursor += 1
        if idx_cursor >= len(line):
            break
        start_pos = idx_cursor
        match_spaces = re.search(r'\s{2,}', line[start_pos:])
        if match_spaces:
            end_pos = start_pos + match_spaces.start()
            idx_cursor = start_pos + match_spaces.end()
        else:
            end_pos = len(line)
            idx_cursor = len(line)
        part_text = line[start_pos:end_pos].strip()
        if part_text:
            parts.append((part_text, start_pos))
    return parts

def split_stat_and_tail(text, pos):
    matches = list(re.finditer(r'[\+\-]\d+', text))
    if not matches:
        return [(text, pos)]
        
    end_idx = matches[-1].end()
    tail = text[end_idx:]
    if not tail:
        return [(text, pos)]
        
    split_idx = len(tail)
    for i, c in enumerate(tail):
        if c.isspace() or c in ["、", ",", "，", "；", "。"]:
            continue
        if c not in ["資", "源", "學", "習", "力", "力", "壓", "訊", "感", "社", "會", "連", "結", "滿", "意", "度", "穩", "定", "試", "錯", "安", "全", "未", "來", "不", "確", "及", "格"]:
            split_idx = i
            break
            
    if split_idx < len(tail):
        col2_text = text[:end_idx + split_idx].strip()
        col3_text = tail[split_idx:].strip()
        return [(col2_text, pos), (col3_text, pos + end_idx + split_idx)]
    else:
        return [(text, pos)]

def is_stat_part(text, pos):
    if any(punc in text for punc in ["。", "，", "；", "！", "？", "「", "」", "｜"]):
        return False
    if re.search(r'[\+\-]\d+', text):
        return True
    if pos >= 30 and len(text) <= 5:
        stat_keywords = ["資源", "學習力", "壓力", "資訊感", "社會連結", "滿意度", "穩定度", "學習力", "壓力", "試錯安全感", "未來不確定", "學習⼒", "壓⼒", "習力", "習⼒", "資", "源", "學", "習", "力", "力", "壓", "訊", "感", "社", "會", "連", "結", "滿", "意", "度", "穩", "定", "試", "錯", "安", "全", "未", "來", "不", "確", "訊感", "安全感", "不確定", "學習", "未來", "社會", "連結", "滿意", "穩定", "意度", "定度", "試錯", "安全", "及", "格"]
        clean_text = text.strip("、, ")
        if clean_text in stat_keywords:
            return True
    return False

def parse_shadows(shadows_text):
    shadow_data = {}
    cleaned_text = clean_shadows_text(shadows_text)
    lines = cleaned_text.split("\n")
    
    char_accumulators = {
        "林予安": {"story": [], "delta": [], "highlight": []},
        "陳佳禾": {"story": [], "delta": [], "highlight": []},
        "黃以真": {"story": [], "delta": [], "highlight": []}
    }
    
    current_char = None
    col0_keywords = ["林予安", "陳佳禾", "黃以真", "都市", "偏鄉", "文化", "充足", "學生", "普通", "經濟", "生", "人", "｜"]
    
    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            continue
        # Strict check for table headers or choice metadata
        if (("角色" in l_strip and "劇情結果" in l_strip) or 
            ("差異重點" in l_strip and "結果" in l_strip) or 
            (l_strip == "選項文字") or 
            (l_strip.startswith("選項") and len(l_strip) <= 6)):
            continue
            
        if not line.startswith(" "):
            current_char = None
            continue
            
        parts = split_by_2spaces(line)
        if not parts:
            continue
            
        # Post-process parts to split merged Delta and Highlight columns
        refined_parts = []
        for text, pos in parts:
            for sub_text, sub_pos in split_stat_and_tail(text, pos):
                refined_parts.append((sub_text, sub_pos))
        parts = refined_parts
            
        detected_char = None
        for char in ["林予安", "陳佳禾", "黃以真"]:
            if char in parts[0][0]:
                detected_char = char
                break
                
        if detected_char:
            current_char = detected_char
            
        stat_indices = [i for i, p in enumerate(parts) if is_stat_part(p[0], p[1])]
        
        col0_text = ""
        col1_text = ""
        col2_text = ""
        col3_text = ""
        
        if stat_indices:
            col2_start_idx = min(stat_indices)
            col2_end_idx = max(stat_indices)
            col2_text = " ".join([parts[i][0] for i in range(col2_start_idx, col2_end_idx + 1)])
            col3_text = " ".join([parts[i][0] for i in range(col2_end_idx + 1, len(parts))])
            
            left_parts = parts[:col2_start_idx]
            if left_parts:
                if left_parts[0][1] < 20:
                    col0_text = left_parts[0][0]
                    col1_text = " ".join([p[0] for p in left_parts[1:]])
                else:
                    col1_text = " ".join([p[0] for p in left_parts])
        else:
            left_parts = parts
            col1_list = []
            col3_list = []
            for text, pos in left_parts:
                if pos >= 50:
                    col3_list.append(text)
                else:
                    if pos < 20 and any(kw in text for kw in col0_keywords):
                        col0_text = text
                    else:
                        col1_list.append(text)
            col1_text = " ".join(col1_list)
            col3_text = " ".join(col3_list)
            
        if current_char:
            if col1_text:
                char_accumulators[current_char]["story"].append(col1_text)
            if col2_text:
                char_accumulators[current_char]["delta"].append(col2_text)
            if col3_text:
                char_accumulators[current_char]["highlight"].append(col3_text)
                
    for char, accum in char_accumulators.items():
        story_text = "".join(accum["story"]).strip()
        delta_text = "".join(accum["delta"]).strip()
        highlight_text = "".join(accum["highlight"]).strip()
        
        story_text = story_text.replace("/", "").strip()
        delta_text = delta_text.replace("/", "").strip()
        highlight_text = highlight_text.replace("/", "").strip()
        
        if story_text or delta_text or highlight_text:
            shadow_data[char] = {
                "story": story_text,
                "delta": delta_text,
                "highlight": highlight_text
            }
            
    return shadow_data

def extract_scene_name(stage_content):
    lines = stage_content.split("\n")
    for idx, line in enumerate(lines):
        if "場景名稱" in line:
            bracket_match = re.search(r"「(.*?)」", line)
            if bracket_match:
                return bracket_match.group(1).strip()
            for offset in range(1, 10):
                if idx + offset < len(lines):
                    next_line_clean = lines[idx+offset].strip()
                    if next_line_clean and "場景劇情" not in next_line_clean:
                        return next_line_clean.replace("「", "").replace("」", "").strip()
    return ""

def build_data():
    with open("02.劇情設計與腳本.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    content = normalize_text(content)
    
    m_end = re.search(r"最後[^\n]*結局[^\n]*畫[^\n]*", content)
    endings_pos = m_end.start() if m_end else -1
    
    m_ref = re.search(r"九、[^\n]*反思[^\n]*|九、[^\n]*結局[^\n]*共同[^\n]*", content)
    reflections_pos = m_ref.start() if m_ref else -1
    
    game_data = {
        "title": "《剛好及格的人生》",
        "subtitle": "我們以為努力就夠了嗎？",
        "intro": {
            "title": "同一間教室，不同的早晨",
            "bg": "早自習鐘聲響起。高中教室裡，老師站在講台前，黑板上寫著：\n\n「高中三年，是你們人生很重要的起點。」\n\n老師說：「我知道大家來自不同地方，但升學考試是公平的。只要你們願意努力，就一定會有回報。」",
            "prompt": "真的是這樣嗎？",
            "protagonist_intro": "早上 6:40。你把昨晚打工的制服收進袋子，準備放學後再去店裡。\n\n媽媽說：「這個月如果可以的話，你再幫忙一點。」\n\n你點點頭，沒有說話。",
            "system_reflection": "你和同學們坐在同一間教室。聽著同一句話。準備面對同一套升學制度。\n\n但你們真的站在同一條起跑線上嗎？"
        },
        "stages": []
    }
    
    stage_markers = [
        ("第一關：高一段考失利", r"第一關：高一段考失利"),
        ("第二關：高二上，是否打工", r"第二關：高二上，是否打工"),
        ("第三關：高二下，大學營隊", r"第三關：高二下，大學營隊"),
        ("第四關：高三考前一個月", r"第四關：高三考前一個月"),
        ("第五關：高三填志願", r"第五關：高三填志願")
    ]
    
    positions = []
    for title, marker in stage_markers:
        matches = list(re.finditer(marker, content))
        if matches:
            positions.append((title, matches[0].start()))
            
    positions.append(("結局", endings_pos))
    
    for idx in range(5):
        st_title, st_start = positions[idx]
        _, next_start = positions[idx+1]
        
        stage_content = content[st_start:next_start]
        
        scene_name = extract_scene_name(stage_content)
        
        scene_plot = ""
        scene_plot_match = re.search(r"場景劇情\s*[\:\::]?(.*?)(?=玩家可選選項|主角可選選項|主角選|選項\s*[A-D]：|選項\s*[A-D]\s*[\:\::\s])", stage_content, re.DOTALL)
        if scene_plot_match:
            plot_raw = scene_plot_match.group(1).strip()
            scene_plot = clean_paragraphs(plot_raw.split("\n"))
        
        choices = {}
        for opt in ["A", "B", "C", "D"]:
            opt_pattern = rf"選項\s*{opt}：(.*?)(?=選項\s*[A-D]：|{st_title.split('：')[0]}整體對照表|{st_title.split('：')[0]}結尾統一文字|{st_title.split('：')[0]}結尾統二文字|結尾統一文字|最後進入結局畫面|\Z)"
            opt_match = re.search(opt_pattern, stage_content, re.DOTALL)
            if opt_match:
                opt_text = opt_match.group(1)
                
                label_match = re.search(r"^(.*?)\n", opt_text)
                label = label_match.group(1).strip() if label_match else ""
                if label.startswith("選項"):
                    label = re.sub(r"^選項\s*[A-D]\s*[\:\::\s]*", "", label)
                
                desc, _ = extract_section(opt_text, r"補充說明：", [r"主角.*選擇後劇情|選擇後劇情", r"主角內心(旁白|獨白)", r"同選項對照", r"想傳達的議題意義"])
                story, _ = extract_section(opt_text, r"主角.*選擇後劇情|選擇後劇情", [r"主角內心(旁白|獨白)", r"同選項對照", r"想傳達的議題意義"])
                monologue, _ = extract_section(opt_text, r"主角內心(旁白|獨白)", [r"同選項對照", r"想傳達的議題意義"])
                shadows_raw, _ = extract_section(opt_text, r"同選項對照：同樣選.*?\n|影子角色同選項對照：|同選項對照：", [r"想傳達的議題意義"])
                theme, _ = extract_section(opt_text, r"想傳達的議題意義", [r"選項\s*[A-D]：|\Z"])
                
                choices[opt] = {
                    "label": label if label else "選項 " + opt,
                    "description": clean_paragraphs(desc.split("\n")),
                    "story": clean_paragraphs(story.split("\n")),
                    "monologue": clean_paragraphs(monologue.split("\n")),
                    "theme": clean_paragraphs(theme.split("\n")),
                    "shadows": parse_shadows(shadows_raw)
                }
                
        game_data["stages"].append({
            "id": f"stage_{idx+1}",
            "title": st_title.split("：")[-1],
            "scene_name": scene_name,
            "scene_plot": scene_plot,
            "choices": choices,
            "conclusion": ""
        })
        
    # Parse Endings text
    endings_section = content[endings_pos:reflections_pos]
    endings_data = {}
    endings_list = [
        ("穩定探索型", "三、結局一：穩定探索型"),
        ("高壓達標型", "四、結局二：高壓達標型"),
        ("剛好及格型／資源受限型", "五、結局三：剛好及格型／資源受限型"),
        ("延後探索型", "六、結局四：延後探索型"),
        ("被迫妥協型", "七、結局五：被迫妥協型"),
        ("普通前進型", "八、結局六：普通前進型")
    ]
    
    for idx_ed, (ed_name, ed_marker) in enumerate(endings_list):
        ed_start = endings_section.find(ed_marker)
        if ed_start != -1:
            next_marker_idx = len(endings_section)
            if idx_ed + 1 < len(endings_list):
                next_marker_idx = endings_section.find(endings_list[idx_ed+1][1])
            
            ed_text = endings_section[ed_start:next_marker_idx]
            
            screen, _ = extract_section(ed_text, r"結局畫面", [r"結局分析文字", r"這個結局想傳達的", r"這個結局不是失敗", r"這個結局最後可以顯示"])
            analysis, _ = extract_section(ed_text, r"結局分析文字", [r"這個結局想傳達的", r"這個結局不是失敗", r"這個結局最後可以顯示", r"這個結局想讓玩家", r"這個結局的重點不是"])
            reflection, _ = extract_section(ed_text, r"這個結局想傳達的是：|這個結局最後可以顯示一句話：|這個結局想讓玩家理解：|這個結局適合提醒玩家：|結局分析文字", [r"\Z"])
            
            endings_data[ed_name] = {
                "screen": clean_paragraphs(screen.split("\n")),
                "analysis": clean_paragraphs(analysis.split("\n")),
                "reflection": clean_paragraphs(reflection.split("\n"))
            }
            
    game_data["endings"] = endings_data
    
    # Parse Reflection Questions
    reflections = []
    if reflections_pos != -1:
        ref_text = content[reflections_pos:]
        
        q1, _ = extract_section(ref_text, r"反思一：選擇自由", [r"反思二：努力的去向"])
        q2, _ = extract_section(ref_text, r"反思二：努力的去向", [r"反思三：如果要改善不平等"])
        q3, _ = extract_section(ref_text, r"反思三：如果要改善不平等", [r"十、|十\s*、|\Z"])
        
        def parse_q(q_raw, q_num):
            lines = [l.strip() for l in q_raw.split("\n") if l.strip()]
            question = ""
            options = []
            for l in lines:
                if l.startswith("「") or "？" in l or l.startswith("題目："):
                    question = l.replace("題目：", "").strip()
                elif re.match(r"^[A-F]\.", l) or re.match(r"^[A-F]\s*[\.．]", l):
                    options.append(l)
            return {"num": q_num, "question": question, "options": options}
            
        reflections.append(parse_q(q1, 1))
        reflections.append(parse_q(q2, 2))
        reflections.append(parse_q(q3, 3))
        
    game_data["reflections"] = reflections
    
    # Apply deep cleaning to ALL text fields in the game data
    game_data = deep_clean_all(game_data)
    
    with open("static/game_data.json", "w", encoding="utf-8") as f_out:
        json.dump(game_data, f_out, indent=2, ensure_ascii=False)
    print("Successfully built static/game_data.json!")

if __name__ == "__main__":
    build_data()

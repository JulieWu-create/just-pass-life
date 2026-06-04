import re
import json
import os

def normalize_text(text):
    # Replaces radical characters with standard Chinese characters
    replacements = {
        "⼀": "一",
        "⿈": "黃",
        "⽲": "禾",
        "⾓": "角",
        "⾊": "色",
        "⽼": "老",
        "⽀": "支",
        "⾦": "金",
        "⽂": "文",
        "⼒": "力",
        "⾝": "身",
        "⽗": "父",
        "⺟": "母",
        "⾼": "高",
        "主⾓": "主角",
        "影⼦": "影子",
        "壓⼒": "壓力",
        "學習⼒": "學習力",
        "資訊感": "資訊感",
        "公⾞": "公車",
        "費⽤": "費用",
        "充⾜": "充足",
        "學⽣": "學生",
        "收⼊": "收入",
        "處⿂": "處境",
        "⾃": "自",
        "⼰": "己",
        "⽐": "比",
        "⼿": "手",
        "櫃台⼈員": "櫃台人員",
        "內⼼": "內心",
        "旁⽩": "旁白",
        "獨⽩": "獨白",
        "同選項對照": "同選項對照",
        "差異重點": "差異重點",
        "數值結果": "數值結果",
        "劇情結果": "劇情結果",
        "陳佳⽲": "陳佳禾",
        "⿈以真": "黃以真",
        "林予安": "林予安",
        "入": "入",
        "面": "面"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def clean_paragraphs(lines):
    cleaned = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if "Page " in l and "===" in line:
            continue
        if l == "============================================================":
            continue
        cleaned.append(l)
        
    result = []
    current_para = []
    for line in cleaned:
        if (line.startswith("「") or line.startswith("同學") or line.startswith("老師") or 
            line.endswith("：") or line.endswith(":") or line.startswith("-") or 
            line.startswith("林予安") or line.startswith("陳佳") or line.startswith("黃以") or 
            re.match(r"^[A-D]\.", line) or re.match(r"^選項\s*[A-D]", line)):
            if current_para:
                result.append("".join(current_para))
                current_para = []
            result.append(line)
        else:
            current_para.append(line)
    if current_para:
        result.append("".join(current_para))
        
    return "\n\n".join(result)

def clean_conclusion(text):
    # Remove "系統文字：" and "系統文字"
    text = re.sub(r'系統文字\s*[\:\：]?', '', text)
    # Remove table page headers like --- Table 1 on Page 25 ---
    text = re.sub(r'--- Table \d+ on Page \d+ ---', '', text, flags=re.IGNORECASE)
    
    # Split text into lines to filter out table rows or option lists
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            cleaned_lines.append("")
            continue
        # Skip table rows (contain tabs or pipes)
        if '\t' in l or '|' in l:
            continue
        # Skip table headers, options or scores summary
        if l.startswith(('選項', '角色', '張宇翔｜', '林予安｜', '陳佳禾｜', '黃以真｜')):
            continue
        if re.match(r'^[A-D]\s*[\.．\s]', l):
            continue
        # Skip transition prompts like "最後進入下一關：" or "最後進入結局畫面"
        if l.startswith(('最後進入下一關', '最後進入下一關：', '最後進入結局畫面')):
            continue
        # Skip table page references
        if 'Table' in l and 'Page' in l:
            continue
        cleaned_lines.append(l)
        
    cleaned_text = "\n".join(cleaned_lines)
    # Remove multiple blank lines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()

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

def parse_shadows(shadows_text):
    shadow_data = {}
    lines = [l.strip() for l in shadows_text.split("\n") if l.strip()]
    
    characters = ["林予安", "陳佳禾", "黃以真"]
    for char in characters:
        char_lines = []
        capturing = False
        for line in lines:
            if char in line:
                capturing = True
                char_lines.append(line)
            elif capturing:
                is_other = False
                for other in characters:
                    if other != char and other in line:
                        is_other = True
                if is_other:
                    capturing = False
                else:
                    char_lines.append(line)
        
        if char_lines:
            cleaned_lines = []
            for cl in char_lines:
                cl_clean = cl.replace(char, "").strip()
                cl_clean = re.sub(r'^[|\t\s\-\:\：\｜]+', '', cl_clean)
                cl_clean = re.sub(r'[|\t\s\-\:\：\｜]+$', '', cl_clean)
                if cl_clean:
                    cleaned_lines.append(cl_clean)
            
            full_char_text = " ".join(cleaned_lines)
            parts = [p.strip() for p in re.split(r'\t|\|', full_char_text) if p.strip()]
            
            if len(parts) >= 3:
                shadow_data[char] = {
                    "story": parts[0],
                    "delta": parts[1],
                    "highlight": parts[2]
                }
            elif len(parts) == 2:
                shadow_data[char] = {
                    "story": parts[0],
                    "delta": parts[1],
                    "highlight": ""
                }
            else:
                shadow_data[char] = {
                    "story": full_char_text,
                    "delta": "",
                    "highlight": ""
                }
    return shadow_data

def extract_scene_name(stage_content):
    lines = stage_content.split("\n")
    for idx, line in enumerate(lines):
        if "場景名稱" in line:
            bracket_match = re.search(r"「(.*?)」", line)
            if bracket_match:
                return bracket_match.group(1).strip()
            # Scan the next few lines
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
    
    # Locate endings and reflections using regex
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
        scene_plot_match = re.search(r"場景劇情\s*[\:\：]?(.*?)(?=玩家可選選項|主角可選選項|主角選|選項\s*[A-D]：|選項\s*[A-D]\s*[\:\：\s])", stage_content, re.DOTALL)
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
                    label = re.sub(r"^選項\s*[A-D]\s*[\:\：\s]*", "", label)
                
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
                
        conclusion = ""
        conclusion_match = re.search(rf"{st_title.split('：')[0]}結尾統一文字(.*?)(\Z)", stage_content, re.DOTALL)
        if not conclusion_match:
            conclusion_match = re.search(r"結尾統一文字(.*?)(\Z)", stage_content, re.DOTALL)
        if conclusion_match:
            conclusion_raw = conclusion_match.group(1)
            conclusion = clean_conclusion(conclusion_raw)
            
        game_data["stages"].append({
            "id": f"stage_{idx+1}",
            "title": st_title.split("：")[-1],
            "scene_name": scene_name,
            "scene_plot": scene_plot,
            "choices": choices,
            "conclusion": conclusion
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
    
    os.makedirs("static", exist_ok=True)
    
    with open("static/game_data.json", "w", encoding="utf-8") as f_out:
        json.dump(game_data, f_out, indent=2, ensure_ascii=False)
    print("Successfully built static/game_data.json!")

if __name__ == "__main__":
    build_data()

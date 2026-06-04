/* ==========================================================================
   《剛好及格的人生》- RPG Game Client Logic (JavaScript)
   ========================================================================== */

class BgmSequencer {
    constructor() {
        this.ctx = null;
        this.isPlaying = false;
        this.nextNoteTime = 0.0;
        this.step = 0;
        
        // Melody notes and bass notes
        this.melody = [
            261.63, null,   329.63, null,   392.00, 523.25, 392.00, null,
            349.23, null,   440.00, null,   523.25, 698.46, 523.25, null,
            293.66, null,   349.23, null,   392.00, 587.33, 392.00, null,
            392.00, null,   493.88, null,   587.33, 783.99, 587.33, null
        ];
        
        this.bass = [
            130.81, 130.81, 130.81, 130.81, 130.81, 130.81, 130.81, 130.81,
            174.61, 174.61, 174.61, 174.61, 174.61, 174.61, 174.61, 174.61,
            146.83, 146.83, 146.83, 146.83, 146.83, 146.83, 146.83, 146.83,
            196.00, 196.00, 196.00, 196.00, 196.00, 196.00, 196.00, 196.00
        ];
        
        this.tempo = 110;
        this.stepDuration = 60 / this.tempo / 2;
    }
    
    start(ctx) {
        if (this.isPlaying) return;
        this.ctx = ctx;
        this.isPlaying = true;
        this.step = 0;
        this.nextNoteTime = this.ctx.currentTime;
        this.schedulerInterval = setInterval(() => this.scheduler(), 50);
    }
    
    stop() {
        if (!this.isPlaying) return;
        this.isPlaying = false;
        clearInterval(this.schedulerInterval);
    }
    
    scheduler() {
        while (this.nextNoteTime < this.ctx.currentTime + 0.1) {
            this.scheduleNote(this.step, this.nextNoteTime);
            this.nextNoteTime += this.stepDuration;
            this.step = (this.step + 1) % this.melody.length;
        }
    }
    
    scheduleNote(step, time) {
        const mFreq = this.melody[step];
        const bFreq = this.bass[step];
        
        if (mFreq) {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = "triangle";
            osc.frequency.setValueAtTime(mFreq, time);
            
            gain.gain.setValueAtTime(0.0, time);
            gain.gain.linearRampToValueAtTime(0.015, time + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, time + this.stepDuration * 1.5);
            
            osc.start(time);
            osc.stop(time + this.stepDuration * 1.5);
        }
        
        if (bFreq && step % 2 === 0) {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = "square";
            osc.frequency.setValueAtTime(bFreq / 2, time);
            
            gain.gain.setValueAtTime(0.0, time);
            gain.gain.linearRampToValueAtTime(0.008, time + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.001, time + this.stepDuration * 1.8);
            
            osc.start(time);
            osc.stop(time + this.stepDuration * 2);
        }
    }
}

class AudioSystem {
    constructor() {
        this.ctx = null;
        this.isMuted = true;
        this.bgm = new BgmSequencer();
    }
    
    init() {
        if (this.ctx) return;
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            this.ctx = new AudioContextClass();
        }
    }
    
    playSelect() {
        this.init();
        if (!this.ctx || this.isMuted) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        
        osc.type = "square";
        const t = this.ctx.currentTime;
        osc.frequency.setValueAtTime(150, t);
        osc.frequency.exponentialRampToValueAtTime(600, t + 0.08);
        
        gain.gain.setValueAtTime(0.03, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
        
        osc.start(t);
        osc.stop(t + 0.08);
    }
    
    playChime() {
        this.init();
        if (!this.ctx || this.isMuted) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        
        const t = this.ctx.currentTime;
        const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = "square";
            osc.frequency.setValueAtTime(freq, t + idx * 0.08);
            gain.gain.setValueAtTime(0.03, t + idx * 0.08);
            gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.08 + 0.15);
            osc.start(t + idx * 0.08);
            osc.stop(t + idx * 0.08 + 0.2);
        });
    }
    
    playStageChime() {
        this.init();
        if (!this.ctx || this.isMuted) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        
        const t = this.ctx.currentTime;
        const notes = [392.00, 523.25, 659.25, 783.99]; // G4, C5, E5, G5
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = "triangle";
            osc.frequency.setValueAtTime(freq, t + idx * 0.06);
            gain.gain.setValueAtTime(0.04, t + idx * 0.06);
            gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.06 + 0.25);
            osc.start(t + idx * 0.06);
            osc.stop(t + idx * 0.06 + 0.3);
        });
    }
    
    playEndingChime() {
        this.init();
        if (!this.ctx || this.isMuted) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        
        const t = this.ctx.currentTime;
        const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = idx === notes.length - 1 ? "square" : "triangle";
            osc.frequency.setValueAtTime(freq, t + idx * 0.1);
            gain.gain.setValueAtTime(0.03, t + idx * 0.1);
            gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.1 + 0.4);
            osc.start(t + idx * 0.1);
            osc.stop(t + idx * 0.1 + 0.5);
        });
    }
    
    toggleBgm() {
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        
        this.isMuted = !this.isMuted;
        const btn = document.getElementById("btn-audio-toggle");
        
        if (this.isMuted) {
            btn.innerHTML = `<span class="audio-icon">🔇</span>`;
            this.bgm.stop();
        } else {
            btn.innerHTML = `<span class="audio-icon">🔊</span>`;
            this.bgm.start(this.ctx);
            this.playSelect();
        }
    }
    
    startBgm() {
        this.init();
        if (!this.ctx || this.isMuted) return;
        if (this.ctx.state === "suspended") this.ctx.resume();
        this.bgm.start(this.ctx);
    }
}

const audioSystem = new AudioSystem();

let gameData = null;
let currentStageIndex = 1; // 1 to 5
let selectedChoices = [];  // Array to store chosen options ['A', 'B', etc.]

// State tracking for text progression and pagination
let dialogueParagraphs = [];
let currentDialogueParaIndex = 0;

let introParagraphs = [];
let currentIntroParaIndex = 0;

let resultPhase = 1; // 1 = protagonist, 2 = shadows comparison

// Local state tracking to render HUD progress bars
let localStats = {
    resource: 10,
    learning: 5,
    stress: 5,
    info: 3,
    satisfaction: 0,
    stability: 0
};

// Character Showcase card rotation interval
let showcaseInterval = null;

// Standardize names in keys to handle radical characters
const SHADOW_NAME_MAP = {
    "林予安": "林予安",
    "陳佳禾": "陳佳禾",
    "陳佳⽲": "陳佳禾",
    "黃以真": "黃以真",
    "⿈以真": "黃以真"
};

// Initial state constant
const INITIAL_STATS = {
    resource: 10,
    learning: 5,
    stress: 5,
    info: 3,
    satisfaction: 0,
    stability: 0
};

document.addEventListener("DOMContentLoaded", () => {
    initGame();
});

async function initGame() {
    try {
        // 1. Fetch game data JSON
        const response = await fetch("static/game_data.json");
        gameData = await response.json();
        
        // 2. Bind event listeners
        bindEvents();
        setupAudioToggle();
        
        // Setup select sound on button clicks
        document.addEventListener("click", (e) => {
            const btn = e.target.closest("button") || e.target.closest(".choice-item-btn") || e.target.closest(".retro-btn");
            if (btn && btn.id !== "btn-audio-toggle") {
                audioSystem.playSelect();
            }
        });
        
        // 3. Setup Showcase rotation
        setupShowcaseRotation();
        
        // 4. Initial screen
        showScreen("screen-start");
    } catch (err) {
        console.error("Failed to load game data:", err);
    }
}

function setupAudioToggle() {
    const btn = document.getElementById("btn-audio-toggle");
    if (btn) {
        btn.addEventListener("click", () => {
            audioSystem.toggleBgm();
        });
    }
}

function bindEvents() {
    // Start Game button
    document.getElementById("btn-start-game").addEventListener("click", () => {
        audioSystem.init();
        audioSystem.playChime();
        if (!audioSystem.isMuted) {
            audioSystem.startBgm();
        }
        clearInterval(showcaseInterval);
        startIntro();
    });

    // Intro next button
    document.getElementById("btn-intro-next").addEventListener("click", () => {
        showNextIntroParagraph();
    });

    // Dialogue next button
    document.getElementById("btn-dialogue-next").addEventListener("click", () => {
        showNextDialogueParagraph();
    });

    // Result next button
    document.getElementById("btn-result-next").addEventListener("click", () => {
        if (resultPhase === 1) {
            // Transition to Phase 2: Show shadow character comparisons
            resultPhase = 2;
            document.getElementById("result-proto-col").classList.add("hidden");
            document.getElementById("result-shadow-col").classList.remove("hidden");
            document.getElementById("btn-result-next").innerHTML = `繼續 <span class="cursor">▶</span>`;
        } else {
            advanceNextStage();
        }
    });

    // Ending screen next button
    document.getElementById("btn-go-reflections").addEventListener("click", () => {
        startReflections();
    });

    // Replay Game button
    document.getElementById("btn-restart-game").addEventListener("click", () => {
        restartGame();
    });
}

function showScreen(screenId) {
    // Hide all screens
    const screens = document.querySelectorAll(".screen");
    screens.forEach(s => s.classList.remove("active"));

    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add("active");
        targetScreen.scrollTop = 0;
    }

    // Toggle HUD header visibility
    const header = document.getElementById("game-header");
    if (screenId === "screen-stage" || screenId === "screen-result") {
        header.classList.remove("hidden");
        updateHeaderStats();
    } else {
        header.classList.add("hidden");
    }
}

function updateHeaderStats() {
    const statsToUpdate = ["resource", "learning", "stress", "info"];
    statsToUpdate.forEach(stat => {
        const container = document.getElementById(`stat-${stat}`);
        if (container) {
            const val = localStats[stat];
            // Normalize val between 0 and 10 for bar representation
            const percentage = Math.min(100, Math.max(0, val * 10));
            const fill = container.querySelector(".stat-progress-fill");
            fill.style.width = `${percentage}%`;
            
            // Adjust bar colors dynamically if stress gets high, or resources get low
            if (stat === "stress") {
                if (val >= 8) fill.style.backgroundColor = "#ff0000"; // Critical red
                else if (val >= 6) fill.style.backgroundColor = "#ff8c00"; // Orange
                else fill.style.backgroundColor = "var(--stat-str)";
            } else if (stat === "resource") {
                if (val <= 3) fill.style.backgroundColor = "#ff3333"; // Depleted red
                else fill.style.backgroundColor = "var(--stat-res)";
            }
            
            container.querySelector(".stat-val").textContent = `${val}/10`;
        }
    });
}

// SETUP CHARACTER SHOWCASE CARDS (Blinks rotation on start screen)
function setupShowcaseRotation() {
    const cards = document.querySelectorAll(".showcase-card");
    let currentIdx = 0;
    
    // Allow user to click to inspect cards manually
    cards.forEach((card, idx) => {
        card.addEventListener("click", () => {
            clearInterval(showcaseInterval);
            cards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            currentIdx = idx;
        });
    });

    showcaseInterval = setInterval(() => {
        cards.forEach(c => c.classList.remove("active"));
        currentIdx = (currentIdx + 1) % cards.length;
        cards[currentIdx].classList.add("active");
    }, 3000);
}

// GAMEPLAY SEQUENCES
function startIntro() {
    showScreen("screen-intro");
    // Build intro paragraphs from game data
    const parts = [
        gameData.intro.bg,
        gameData.intro.prompt,  // "真的是這樣嗎？" - will be styled red
        gameData.intro.protagonist_intro,
        gameData.intro.system_reflection
    ];
    
    // Split each part by \n\n and flatten, keeping the prompt separate
    introParagraphs = [];
    parts.forEach((part, partIndex) => {
        const subParts = part.split("\n\n").map(p => p.trim()).filter(p => p.length > 0);
        subParts.forEach(sp => {
            introParagraphs.push({
                text: sp,
                isRedPrompt: (partIndex === 1) // The prompt part gets red styling
            });
        });
    });
    
    currentIntroParaIndex = 0;
    showNextIntroParagraph();
}

function showNextIntroParagraph() {
    if (currentIntroParaIndex < introParagraphs.length) {
        const para = introParagraphs[currentIntroParaIndex];
        const el = document.getElementById("intro-narrative-text");
        
        if (para.isRedPrompt) {
            el.innerHTML = `<span style="color: var(--text-red); font-size: 1.3em; font-weight: bold;">${para.text}</span>`;
        } else {
            el.textContent = "";
            // Use typeText for non-red paragraphs
            typeText("intro-narrative-text", para.text, 10);
        }
        
        currentIntroParaIndex++;
        
        const nextBtn = document.getElementById("btn-intro-next");
        if (currentIntroParaIndex === introParagraphs.length) {
            nextBtn.innerHTML = `進入第一關 <span class="cursor">▶</span>`;
        } else {
            nextBtn.innerHTML = `繼續 <span class="cursor">▶</span>`;
        }
    } else {
        // All intro paragraphs shown, proceed to stage 1
        startStage(1);
    }
}

function startStage(stageNum) {
    audioSystem.init();
    audioSystem.playStageChime();
    currentStageIndex = stageNum;
    const stageData = gameData.stages[stageNum - 1];
    
    showScreen("screen-stage");
    
    // Set titles
    document.getElementById("stage-number-tag").textContent = `STAGE ${stageNum}`;
    document.getElementById("stage-scene-title").textContent = stageData.scene_name;
    
    // Segment stage story/plot by paragraphs - smart merging to avoid mid-sentence breaks
    const rawParas = stageData.scene_plot.split("\n\n").map(p => p.trim()).filter(p => p.length > 0);
    dialogueParagraphs = smartMergeParagraphs(rawParas);
    currentDialogueParaIndex = 0;
    
    // Hide choices menu initially
    document.querySelector(".choices-container").classList.add("hidden");
    
    // Show dialogue next button
    const nextBtn = document.getElementById("btn-dialogue-next");
    nextBtn.classList.remove("hidden");
    
    // Render first paragraph
    showNextDialogueParagraph();
}

function showNextDialogueParagraph() {
    if (currentDialogueParaIndex < dialogueParagraphs.length) {
        const text = dialogueParagraphs[currentDialogueParaIndex];
        typeText("stage-scene-text", text, 8);
        currentDialogueParaIndex++;
        
        const nextBtn = document.getElementById("btn-dialogue-next");
        if (currentDialogueParaIndex === dialogueParagraphs.length) {
            nextBtn.innerHTML = `進入抉擇 <span class="cursor">▶</span>`;
        } else {
            nextBtn.innerHTML = `繼續 <span class="cursor">▶</span>`;
        }
    } else {
        // Hide next button and show choices menu
        document.getElementById("btn-dialogue-next").classList.add("hidden");
        document.querySelector(".choices-container").classList.remove("hidden");
        
        // Inject stage choices menu
        injectStageChoices();
    }
}

function injectStageChoices() {
    const stageData = gameData.stages[currentStageIndex - 1];
    const choicesList = document.getElementById("stage-choices-list");
    choicesList.innerHTML = "";
    
    for (const optKey in stageData.choices) {
        const opt = stageData.choices[optKey];
        const li = document.createElement("li");
        
        li.innerHTML = `
            <button class="choice-item-btn" data-choice="${optKey}">
                <span class="choice-selector">▶</span>
                <span class="choice-text"><strong>${optKey}.</strong> ${opt.label}</span>
            </button>
        `;
        choicesList.appendChild(li);
    }
    
    // Bind click events to choice buttons
    const choiceButtons = choicesList.querySelectorAll(".choice-item-btn");
    choiceButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const choice = btn.getAttribute("data-choice");
            makeChoice(choice);
        });
    });
}

function makeChoice(optionId) {
    selectedChoices.push(optionId);
    const stageData = gameData.stages[currentStageIndex - 1];
    const choiceData = stageData.choices[optionId];
    
    // Let's copy stats delta locally
    let localDelta = {};
    if (currentStageIndex === 1) {
        if (optionId === "A") localDelta = {"resource": -4, "learning": 2, "stress": 3, "info": 1};
        if (optionId === "B") localDelta = {"resource": -1, "learning": 1, "stress": 1, "info": 0};
        if (optionId === "C") localDelta = {"resource": 0, "learning": 1, "stress": 1, "info": 1};
        if (optionId === "D") localDelta = {"resource": 0, "learning": -1, "stress": 2, "info": -1};
    } else if (currentStageIndex === 2) {
        if (optionId === "A") localDelta = {"resource": 3, "learning": -3, "stress": 3, "info": 0};
        if (optionId === "B") localDelta = {"resource": 1, "learning": -1, "stress": 2, "info": 0};
        if (optionId === "C") localDelta = {"resource": -2, "learning": 2, "stress": 2, "info": 0};
        if (optionId === "D") {
            localDelta = {"resource": 2, "learning": 0, "stress": 1, "info": 2};
            // Stage 2 D conditional rules
            const prev = selectedChoices[0];
            if (prev === "C") localDelta["stress"] -= 1;
            if (prev === "D") localDelta["stress"] += 1;
        }
    } else if (currentStageIndex === 3) {
        if (optionId === "A") localDelta = {"resource": -4, "learning": -1, "stress": 3, "info": 2};
        if (optionId === "B") localDelta = {"resource": 0, "learning": 0, "stress": 1, "info": 1};
        if (optionId === "C") localDelta = {"resource": 0, "learning": 0, "stress": 0, "info": 2};
        if (optionId === "D") localDelta = {"resource": 0, "learning": 1, "stress": -1, "info": -1};
    } else if (currentStageIndex === 4) {
        if (optionId === "A") localDelta = {"resource": 0, "learning": 0, "stress": 2, "info": 0};
        if (optionId === "B") localDelta = {"resource": -1, "learning": 1, "stress": 1, "info": 0};
        if (optionId === "C") localDelta = {"resource": -3, "learning": 2, "stress": 2, "info": 1};
        if (optionId === "D") localDelta = {"resource": 0, "learning": 1, "stress": 1, "info": 1};
    } else if (currentStageIndex === 5) {
        if (optionId === "A") localDelta = {"satisfaction": 2, "stability": 0, "stress": 3, "info": 0};
        if (optionId === "B") localDelta = {"satisfaction": 0, "stability": 3, "stress": 1, "info": 0};
        if (optionId === "C") localDelta = {"satisfaction": -1, "stability": 2, "stress": 1, "info": 0};
        if (optionId === "D") localDelta = {"satisfaction": 1, "stability": 2, "stress": 1, "info": 2};
    }
    
    // Apply local delta to HUD
    for (const key in localDelta) {
        localStats[key] = (localStats[key] || 0) + localDelta[key];
    }
    
    // Reset two-phase result progression
    resultPhase = 1;
    document.getElementById("result-proto-col").classList.remove("hidden");
    document.getElementById("result-shadow-col").classList.add("hidden");
    document.getElementById("btn-result-next").innerHTML = `查看影子角色對照 <span class="cursor">▶</span>`;
    
    // Show results screen
    showScreen("screen-result");
    
    // Render result body - clean garbled text
    let storyText = choiceData.story || "";
    storyText = storyText.replace(/---\s*Table\s+\d+\s+on\s+Page\s+\d+\s*---/gi, '').trim();
    storyText = storyText.replace(/Page\s*\d+/gi, '').trim();
    storyText = storyText.replace(/狀態[\s]+變化[\s\S]*$/g, '').trim();
    // Remove stat summary lines like "資源 -4" at the end
    storyText = storyText.replace(/\n+(狀態|資源|學習力|壓力|資訊感)[\s\S]*$/g, '').trim();
    document.getElementById("result-story-text").textContent = storyText;
    
    // Protagonist monologue
    let monologueText = choiceData.monologue || "";
    // Clean: remove trailing "影子角色" text
    monologueText = monologueText.replace(/影子角色\s*$/g, '').trim();
    // Clean: remove garbled table/page markers
    monologueText = monologueText.replace(/---\s*Table\s+\d+\s+on\s+Page\s+\d+\s*---/gi, '').trim();
    monologueText = monologueText.replace(/Page\s*\d+/gi, '').trim();
    // Clean: remove tab-separated stat lines like "狀態\t變化..." patterns
    monologueText = monologueText.replace(/狀態[\t\s]+變化[\s\S]*$/g, '').trim();
    
    if (monologueText) {
        document.getElementById("result-monologue-text").textContent = `「${monologueText}」`;
        document.querySelector(".monologue-bubble").style.display = "block";
    } else {
        document.querySelector(".monologue-bubble").style.display = "none";
    }
    
    // Render Shadow Comparisons
    const shadowGrid = document.getElementById("result-shadow-grid");
    shadowGrid.innerHTML = "";
    
    const shadowConfigs = [
        { name: "林予安", avatar: "avatar_yu_an.png", class: "yu-an" },
        { name: "陳佳禾", avatar: "avatar_jia_he.png", class: "jia_he" },
        { name: "黃以真", avatar: "avatar_yi_zhen.png", class: "yi_zhen" }
    ];
    
    shadowConfigs.forEach(conf => {
        const shadowRawName = Object.keys(choiceData.shadows).find(k => SHADOW_NAME_MAP[k] === conf.name);
        const shadow = choiceData.shadows[shadowRawName || conf.name];
        
        if (shadow) {
            // Clean shadow story text - extract narrative from garbled column-merged PDF data
            let shadowStory = cleanShadowText(shadow.story || "");
            
            // Clean delta text  
            let shadowDelta = cleanShadowText(shadow.delta || "");
            
            // Clean highlight text
            let shadowHighlight = cleanShadowText(shadow.highlight || "");
            
            const card = document.createElement("div");
            card.className = `shadow-card ${conf.class}`;
            card.innerHTML = `
                <div class="shadow-card-avatar" style="background-image: url('static/assets/${conf.avatar}')"></div>
                <div class="shadow-card-content">
                    <div class="shadow-card-header">
                        <span class="shadow-card-name">${conf.name}</span>
                        <span class="shadow-card-delta yellow-text">${shadowDelta}</span>
                    </div>
                    <p class="shadow-card-story">${shadowStory}</p>
                    ${shadowHighlight ? `<div class="shadow-card-highlight">✦ ${shadowHighlight}</div>` : ""}
                </div>
            `;
            shadowGrid.appendChild(card);
        }
    });
}


function advanceNextStage() {
    if (currentStageIndex < 5) {
        startStage(currentStageIndex + 1);
    } else {
        // Complete stage 5, submit to resolve ending
        submitChoicesToBackend();
    }
}

async function submitChoicesToBackend() {
    try {
        const response = await fetch("/simulate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ choices: selectedChoices })
        });
        
        if (!response.ok) {
            throw new Error(`Simulation failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        renderEnding(result);
    } catch (err) {
        console.warn("API simulation unavailable, using local fallback resolution:", err);
        const fallbackEnding = localResolveEnding(localStats);
        renderEnding({ ending: fallbackEnding, core_stats: localStats });
    }
}

function renderEnding(apiResult) {
    audioSystem.init();
    audioSystem.playEndingChime();
    showScreen("screen-ending");
    
    const endingName = apiResult.ending.name;
    const endingData = gameData.endings[endingName];
    
    document.getElementById("ending-name").textContent = endingName;
    document.getElementById("ending-screen-text").textContent = endingData.screen;
    document.getElementById("ending-analysis-text").textContent = endingData.analysis;
    document.getElementById("ending-reflection-text").textContent = endingData.reflection;
    
    // Build ending stats table rows
    const tbody = document.getElementById("ending-stats-table-body");
    tbody.innerHTML = "";
    
    // Compile stats comparison
    const statLabels = {
        "resource": "資源 (RES)",
        "learning": "學習力 (LRN)",
        "stress": "壓力 (STR)",
        "info": "資訊感 (INF)",
        "satisfaction": "滿意度 (SAT)",
        "stability": "穩定度 (STA)"
    };
    
    // Fixed final stats for Shadow NPCs based on script definitions
    // These are cumulative values if they made optimal equivalent selections
    const shadowFinalStats = {
        "林予安": { resource: 9, learning: 9, stress: 2, info: 8, satisfaction: 2, stability: 2 },
        "陳佳禾": { resource: 4, learning: 5, stress: 7, info: 4, satisfaction: 0, stability: 1 },
        "黃以真": { resource: 6, learning: 7, stress: 5, info: 6, satisfaction: 1, stability: 2 }
    };
    
    for (const key in statLabels) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td style="text-align: left; font-weight: bold;">${statLabels[key]}</td>
            <td class="yellow-text">${apiResult.core_stats[key] ?? 0}</td>
            <td>${shadowFinalStats["林予安"][key] ?? 0}</td>
            <td>${shadowFinalStats["陳佳禾"][key] ?? 0}</td>
            <td>${shadowFinalStats["黃以真"][key] ?? 0}</td>
        `;
        tbody.appendChild(row);
    }
}

// REFLECTION QUESTIONS MANAGEMENT
let currentReflectionIndex = 0;
function startReflections() {
    currentReflectionIndex = 0;
    showScreen("screen-reflection");
    renderReflectionQuestion();
}

function renderReflectionQuestion() {
    const qData = gameData.reflections[currentReflectionIndex];
    document.getElementById("reflection-progress").textContent = `問題 ${currentReflectionIndex + 1} / 3`;
    document.getElementById("reflection-q-text").textContent = qData.question;
    
    // Inject options
    const choicesList = document.getElementById("reflection-choices-list");
    choicesList.innerHTML = "";
    
    const feedbackBox = document.getElementById("reflection-feedback-container");
    feedbackBox.classList.add("hidden");
    
    qData.options.forEach(opt => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.textContent = opt;
        btn.addEventListener("click", () => {
            showReflectionFeedback(qData);
        });
        li.appendChild(btn);
        choicesList.appendChild(li);
    });
}

function showReflectionFeedback(qData) {
    const feedbackBox = document.getElementById("reflection-feedback-container");
    const feedbackText = document.getElementById("reflection-feedback-text");
    const nextBtn = document.getElementById("btn-next-reflection");
    
    feedbackBox.classList.remove("hidden");
    
    // Inject feedback explanation text based on question number
    let feedback = "";
    if (qData.num === 1) {
        feedback = "張宇翔也有選擇的權利，但他選大型補習班需要考慮家庭生計，選全力讀書必須面臨不打工帶來的經濟焦慮。相較之下，林予安選興趣科系或補習班，幾乎不需要付出生存的機會成本。這代表，弱勢學生的『選擇自由』是伴隨著高昂代價與愧疚感的。";
    } else if (qData.num === 2) {
        feedback = "張宇翔的高中三年，大部分精力與時間並不是單純花在課業衝刺，而是在支撐家庭生計、處理長途打工造成的身體疲憊，以及努力去補足家庭無法提供的升學資訊落差。他的努力大多被『生活本身』消耗掉了。";
    } else if (qData.num === 3) {
        feedback = "政策改善不平等不能僅靠『提供更多考試名額』。提供免費的輔導諮詢、大學營隊的交通補助、AI 素養與設備引導，或是減少家庭生存負擔（減少被迫打工），才是讓每個人能站在相似的起跑線上，讓努力發揮價值的真正解方。";
    }
    
    feedbackText.textContent = feedback;
    
    if (currentReflectionIndex < 2) {
        nextBtn.textContent = "下一個問題 ▶";
        // Remove prior event listeners to prevent step skipping
        const newNextBtn = nextBtn.cloneNode(true);
        nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
        newNextBtn.addEventListener("click", () => {
            currentReflectionIndex++;
            renderReflectionQuestion();
        });
    } else {
        nextBtn.textContent = "查看結語與回顧 ▶";
        const newNextBtn = nextBtn.cloneNode(true);
        nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
        newNextBtn.addEventListener("click", () => {
            showScreen("screen-final");
        });
    }
}

function restartGame() {
    clearInterval(showcaseInterval);
    selectedChoices = [];
    currentStageIndex = 1;
    localStats = { ...INITIAL_STATS };
    setupShowcaseRotation();
    showScreen("screen-start");
}

// TYPING ANIMATION HELPER EFFECT (For Retro Dialogue Feel)
let typeTimeout = null;
function typeText(elementId, text, speed) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    clearTimeout(typeTimeout);
    element.textContent = "";
    
    let idx = 0;
    function type() {
        if (idx < text.length) {
            element.textContent += text.charAt(idx);
            idx++;
            typeTimeout = setTimeout(type, speed);
        }
    }
    type();
}

// LOCAL RESOLUTION FALLBACK (Matching Backend Resolving Logic)
function localResolveEnding(state) {
    if (state.learning <= 3 && state.stress >= 10 && state.info <= 2) {
        return { name: "被迫妥協型", priority: 1 };
    }
    if (state.learning >= 7 && state.stress >= 10) {
        return { name: "高壓達標型", priority: 2 };
    }
    if (
        state.learning >= 7 &&
        state.info >= 6 &&
        state.stress <= 9 &&
        state.satisfaction >= 1
    ) {
        return { name: "穩定探索型", priority: 3 };
    }
    if (state.stability >= 2 && state.satisfaction <= 0 && state.info <= 4) {
        return { name: "延後探索型", priority: 4 };
    }
    if (state.learning >= 4 && state.learning <= 6 && state.stress >= 8) {
        return { name: "剛好及格型／資源受限型", priority: 5 };
    }
    return { name: "普通前進型", priority: 6 };
}

function cleanShadowText(text) {
    if (!text) return "";
    return text.trim();
}

function smartMergeParagraphs(paras) {
    const merged = [];
    let temp = "";
    
    // Chinese punctuation marks that end a sentence
    const endingPunc = /[。！？」』…”）\.\!\?]$/;
    
    paras.forEach(p => {
        if (temp) {
            temp += p;
        } else {
            temp = p;
        }
        
        if (endingPunc.test(temp)) {
            merged.push(temp);
            temp = "";
        }
    });
    
    if (temp) {
        merged.push(temp);
    }
    
    return merged.length > 0 ? merged : paras;
}


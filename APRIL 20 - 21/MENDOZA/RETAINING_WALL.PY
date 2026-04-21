<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Retaining Wall Visualizer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            display: flex;
            gap: 30px;
            max-width: 1200px;
            width: 100%;
        }
        .controls-wrapper {
            flex: 1.2;
            display: flex;
            flex-direction: column;
        }
        .controls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .canvas-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #eef2f5;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;}
        h3 { margin: 10px 0 5px 0; color: #34495e; font-size: 16px; grid-column: span 2;}
        .slider-group { display: flex; flex-direction: column; }
        label { font-weight: bold; margin-bottom: 5px; display: flex; justify-content: space-between; font-size: 13px;}
        input[type=range] { width: 100%; cursor: pointer; }
        .results {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .result-box { background: white; padding: 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;}
        .result-title { font-size: 12px; color: #7f8c8d; text-transform: uppercase; font-weight: bold;}
        .fs-display { font-size: 20px; font-weight: bold; margin-top: 5px; }
        .pass { color: #27ae60; }
        .fail { color: #e74c3c; }
        canvas { border: 1px solid #dcdde1; background-color: white; }
    </style>
</head>
<body>

<div class="container">
    <div class="controls-wrapper">
        <h2>Wall Parameters & Analysis</h2>
        
        <div class="controls-grid">
            <h3>Geometry Inputs</h3>
            <div class="slider-group">
                <label>Stem Height: <span id="valHeight">3.50 m</span></label>
                <input type="range" id="H_stem" min="2.0" max="6.0" step="0.1" value="3.5">
            </div>
            <div class="slider-group">
                <label>Base Slab Thickness: <span id="valTBase">0.50 m</span></label>
                <input type="range" id="t_base" min="0.3" max="1.5" step="0.05" value="0.5">
            </div>
            <div class="slider-group">
                <label>Toe Width: <span id="valToe">0.90 m</span></label>
                <input type="range" id="B_toe" min="0.5" max="3.0" step="0.1" value="0.9">
            </div>
            <div class="slider-group">
                <label>Heel Width: <span id="valHeel">2.10 m</span></label>
                <input type="range" id="B_heel" min="1.0" max="4.0" step="0.1" value="2.1">
            </div>
            <div class="slider-group">
                <label>Stem Bottom Thick: <span id="valTStemBot">0.40 m</span></label>
                <input type="range" id="t_stem_bot" min="0.2" max="1.0" step="0.05" value="0.4">
            </div>

            <h3>Soil Mechanics</h3>
            <div class="slider-group">
                <label>Earth Pressure (Ka): <span id="valKa">0.33</span></label>
                <input type="range" id="Ka" min="0.2" max="0.6" step="0.01" value="0.33">
            </div>
            <div class="slider-group">
                <label>Base Friction (&mu;): <span id="valMu">0.40</span></label>
                <input type="range" id="mu" min="0.2" max="0.7" step="0.05" value="0.4">
            </div>
        </div>

        <div class="results">
            <div class="result-box">
                <div class="result-title">Overturning FS</div>
                <div id="outOT" class="fs-display">0.00</div>
            </div>
            <div class="result-box">
                <div class="result-title">Sliding FS</div>
                <div id="outSlide" class="fs-display">0.00</div>
            </div>
            <div class="result-box" style="grid-column: span 2;">
                <div class="result-title">Max Bearing Pressure (q_max)</div>
                <div id="outBearing" class="fs-display">0.00 kPa</div>
            </div>
        </div>
    </div>

    <div class="canvas-container">
        <canvas id="wallCanvas" width="500" height="550"></canvas>
    </div>
</div>

<script>
    // Canvas Setup
    const canvas = document.getElementById('wallCanvas');
    const ctx = canvas.getContext('2d');
    
    // Inputs
    const sl_H = document.getElementById('H_stem');
    const sl_Toe = document.getElementById('B_toe');
    const sl_Heel = document.getElementById('B_heel');
    const sl_TBase = document.getElementById('t_base');
    const sl_TStemBot = document.getElementById('t_stem_bot');
    const sl_Ka = document.getElementById('Ka');
    const sl_Mu = document.getElementById('mu');
    
    // Outputs
    const outOT = document.getElementById('outOT');
    const outSlide = document.getElementById('outSlide');
    const outBearing = document.getElementById('outBearing');

    // Constants (Can be made sliders later if needed)
    const t_stem_top = 0.25; 
    const gamma_s = 17.0; 
    const gamma_c = 23.54; 

    // Visualization Scale
    const originX = 60;   
    const originY = 450;  

    function calculateAndDraw() {
        // 1. Fetch values
        const Hs = parseFloat(sl_H.value);
        const Btoe = parseFloat(sl_Toe.value);
        const Bheel = parseFloat(sl_Heel.value);
        const tb = parseFloat(sl_TBase.value);
        const tbot = parseFloat(sl_TStemBot.value);
        const Ka = parseFloat(sl_Ka.value);
        const mu = parseFloat(sl_Mu.value);
        
        // Update Labels
        document.getElementById('valHeight').innerText = Hs.toFixed(2) + " m";
        document.getElementById('valToe').innerText = Btoe.toFixed(2) + " m";
        document.getElementById('valHeel').innerText = Bheel.toFixed(2) + " m";
        document.getElementById('valTBase').innerText = tb.toFixed(2) + " m";
        document.getElementById('valTStemBot').innerText = tbot.toFixed(2) + " m";
        document.getElementById('valKa').innerText = Ka.toFixed(2);
        document.getElementById('valMu').innerText = mu.toFixed(2);

        const Bbase = Btoe + tbot + Bheel;
        const Htotal = Hs + tb;

        // 2. ENGINEERING CALCULATIONS
        // Driving Forces
        const Pa = 0.5 * Ka * gamma_s * Math.pow(Htotal, 2);
        const M_driving = Pa * (Htotal / 3);

        // Resisting Vertical Forces & Moments (about Toe)
        const W_base = gamma_c * Bbase * tb;
        const arm_base = Bbase / 2;

        const W_stem_rect = gamma_c * t_stem_top * Hs;
        const arm_stem_rect = Btoe + tbot - (t_stem_top / 2);

        const W_stem_tri = gamma_c * 0.5 * (tbot - t_stem_top) * Hs;
        const arm_stem_tri = Btoe + (tbot - t_stem_top) * (2/3);

        const W_soil = gamma_s * Bheel * Hs;
        const arm_soil = Btoe + tbot + (Bheel / 2);

        const Sum_V = W_base + W_stem_rect + W_stem_tri + W_soil;
        const M_resisting = (W_base * arm_base) + (W_stem_rect * arm_stem_rect) + 
                            (W_stem_tri * arm_stem_tri) + (W_soil * arm_soil);

        // A. Overturning FS
        const FS_OT = M_resisting / M_driving;
        
        // B. Sliding FS
        const F_resist = Sum_V * mu;
        const FS_Slide = F_resist / Pa;

        // C. Bearing Pressure
        const x_R = (M_resisting - M_driving) / Sum_V;
        const e = (Bbase / 2) - x_R;
        let q_max = 0;
        
        if (Math.abs(e) <= Bbase / 6) {
            // Resultant in middle third (Trapezoidal pressure)
            q_max = (Sum_V / Bbase) * (1 + 6 * Math.abs(e) / Bbase);
        } else {
            // Resultant outside middle third (Triangular pressure)
            q_max = (2 * Sum_V) / (3 * x_R);
        }

        // 3. UPDATE UI RESULTS
        outOT.innerText = FS_OT.toFixed(2) + (FS_OT >= 2.0 ? " (PASS)" : " (FAIL)");
        outOT.className = "fs-display " + (FS_OT >= 2.0 ? "pass" : "fail");

        outSlide.innerText = FS_Slide.toFixed(2) + (FS_Slide >= 1.5 ? " (PASS)" : " (FAIL)");
        outSlide.className = "fs-display " + (FS_Slide >= 1.5 ? "pass" : "fail");

        outBearing.innerText = q_max.toFixed(1) + " kPa";
        // Assuming 150 kPa allowable for a quick visual pass/fail
        outBearing.className = "fs-display " + (q_max <= 150 ? "pass" : "fail");

        // 4. DRAW CANVAS
        // Dynamic scale based on total height to keep it in frame
        const SCALE = Math.min(50, 400 / Htotal); 
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Soil
        ctx.fillStyle = "rgba(139, 69, 19, 0.2)";
        ctx.fillRect(originX + (Btoe + tbot) * SCALE, originY - (Hs + tb) * SCALE, Bheel * SCALE + 50, Hs * SCALE);

        // Ground Line
        ctx.beginPath();
        ctx.moveTo(0, originY - tb * SCALE);
        ctx.lineTo(canvas.width, originY - tb * SCALE);
        ctx.strokeStyle = "#8b4513";
        ctx.stroke();

        // Wall Profile
        ctx.fillStyle = "#95a5a6";
        ctx.strokeStyle = "#2c3e50";
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(originX, originY); 
        ctx.lineTo(originX + Bbase * SCALE, originY);
        ctx.lineTo(originX + Bbase * SCALE, originY - tb * SCALE);
        ctx.lineTo(originX + (Btoe + tbot) * SCALE, originY - tb * SCALE);
        ctx.lineTo(originX + (Btoe + tbot) * SCALE, originY - (tb + Hs) * SCALE);
        ctx.lineTo(originX + (Btoe + tbot - t_stem_top) * SCALE, originY - (tb + Hs) * SCALE);
        ctx.lineTo(originX + Btoe * SCALE, originY - tb * SCALE);
        ctx.lineTo(originX, originY - tb * SCALE);
        ctx.closePath();
        
        ctx.fill();
        ctx.stroke();
    }

    // Event Listeners
    [sl_H, sl_Toe, sl_Heel, sl_TBase, sl_TStemBot, sl_Ka, sl_Mu].forEach(slider => {
        slider.addEventListener('input', calculateAndDraw);
    });

    // Init
    calculateAndDraw();
</script>

</body>
</html>
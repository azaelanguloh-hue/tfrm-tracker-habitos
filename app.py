import json
import random
from datetime import datetime
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="TFRM — Tracker de Hábitos", page_icon="✅", layout="centered")

CFG_PATH = Path(__file__).parent / "habitos_config.json"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ⚠️ IMPORTANTE: NO cacheamos el config para evitar que se quede “pegado” con la versión vieja
def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))

CFG = load_cfg()
HABITS = CFG["habits"]
DAYS = CFG.get("days_in_month", 31)
PHRASES = CFG.get("motivational_phrases", [])
RETOS = CFG.get("retos", [])

STATE_FILE = DATA_DIR / "mes1.json"

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "goal": "",
        "days": {str(d): {h: False for h in HABITS} for d in range(1, DAYS + 1)},
        "saved_at": None,
    }

def save_state(state: dict):
    state["saved_at"] = datetime.now().isoformat(timespec="seconds")
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def pick_phrase():
    return random.choice(PHRASES) if PHRASES else "¡Buen trabajo!"

# UI grande para móvil
st.markdown("""
<style>
div[data-testid="stTextInput"] input { font-size: 18px; padding: 14px 12px; }
div[data-testid="stSelectbox"] div { font-size: 18px; }
button[kind="primary"] { height: 52px; font-size: 18px; border-radius: 14px; }
button[kind="secondary"] { height: 48px; font-size: 16px; border-radius: 14px; }
div[data-testid="stCheckbox"] label { font-size: 18px; }

/* Grid mensual responsive */
.month-grid{
  display:grid;
  grid-template-columns: repeat(7, 1fr);
  gap:10px;
}
@media (max-width: 640px){
  .month-grid{ grid-template-columns: repeat(4, 1fr); }
}
.day-chip{
  padding:10px 10px;
  border-radius:14px;
  border:1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.9);
  font-size:16px;
  display:flex;
  justify-content:space-between;
  align-items:center;
}
</style>
""", unsafe_allow_html=True)

st.title("TFRM — Tracker de Hábitos")
st.caption("Palomea tu progreso día con día. Sin perfección. Con constancia.")

state = load_state()

st.subheader("¿Qué quiero lograr este mes?")
goal = st.text_input("Objetivo (corto):", value=state.get("goal", ""))
state["goal"] = goal

st.subheader("Retos del mes")
for r in RETOS:
    st.markdown(f"- **{r}**")

st.markdown("---")

st.subheader("Mis hábitos")
day = st.selectbox("Día:", list(range(1, DAYS + 1)), index=0)
st.caption("Marca lo que lograste hoy.")

day_key = str(day)
day_data = state["days"].get(day_key, {h: False for h in HABITS})
new_day_data = {}
for h in HABITS:
    new_day_data[h] = st.checkbox(h, value=bool(day_data.get(h, False)), key=f"{day}_{h}")

state["days"][day_key] = new_day_data

colA, colB = st.columns([1, 1])
with colA:
    if st.button("Guardar mi día", type="primary", use_container_width=True):
        save_state(state)
        st.success(pick_phrase())
with colB:
    if st.button("Limpiar este día", type="secondary", use_container_width=True):
        state["days"][day_key] = {h: False for h in HABITS}
        save_state(state)
        st.info("Listo. Día reiniciado.")

st.markdown("---")

st.subheader("Vista mensual (simple)")
st.caption("Cada día muestra tu nivel de avance (solo un vistazo).")

def badge(c):
    if c == 0: return "⬜"
    if c <= 3: return "🟠"
    if c <= 7: return "🟡"
    if c <= 10: return "🟢"
    return "✅"

chips_html = '<div class="month-grid">'
for d in range(1, DAYS + 1):
    dd = state["days"].get(str(d), {})
    count = sum(1 for v in dd.values() if v)
    chips_html += f'<div class="day-chip"><b>{d}</b><span>{badge(count)}</span></div>'
chips_html += "</div>"

st.markdown(chips_html, unsafe_allow_html=True)
st.caption("Leyenda: ⬜ 0 | 🟠 1–3 | 🟡 4–7 | 🟢 8–10 | ✅ 11+")

if state.get("saved_at"):
    st.caption(f"Último guardado: {state['saved_at']}")

import json
import random
from datetime import datetime
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="TFRM — Tracker de Hábitos", page_icon="✅", layout="centered")

CFG_PATH = Path(__file__).parent / "habitos_config.json"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

@st.cache_data(show_spinner=False)
def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))

CFG = load_cfg()
HABITS = CFG["habits"]
DAYS = CFG.get("days_in_month", 31)
PHRASES = CFG.get("motivational_phrases", [])

def month_key(label: str) -> str:
    return "mes1" if label.lower().endswith("1") else "mes2"

def file_for(month_label: str) -> Path:
    return DATA_DIR / f"{month_key(month_label)}.json"

def load_state(month_label: str) -> dict:
    fp = file_for(month_label)
    if fp.exists():
        return json.loads(fp.read_text(encoding="utf-8"))
    return {
        "goal": "",
        "days": {str(d): {h: False for h in HABITS} for d in range(1, DAYS+1)},
        "saved_at": None,
    }

def save_state(month_label: str, state: dict):
    state["saved_at"] = datetime.now().isoformat(timespec="seconds")
    file_for(month_label).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def pick_phrase():
    return random.choice(PHRASES) if PHRASES else "¡Buen trabajo!"

st.markdown("""
<style>
div[data-testid="stTextInput"] input { font-size: 18px; padding: 14px 12px; }
div[data-testid="stSelectbox"] div { font-size: 18px; }
button[kind="primary"] { height: 52px; font-size: 18px; border-radius: 14px; }
button[kind="secondary"] { height: 48px; font-size: 16px; border-radius: 14px; }
div[data-testid="stCheckbox"] label { font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.title("TFRM — Tracker de Hábitos")
st.caption("Palomea tu progreso día con día. Sin perfección. Con constancia.")

tabs = st.tabs(["Mes 1", "Mes 2"])

for i, month_label in enumerate(["Mes 1", "Mes 2"]):
    with tabs[i]:
        state = load_state(month_label)

        st.subheader("¿Qué quiero lograr este mes?")
        goal = st.text_input("Objetivo (corto):", value=state.get("goal", ""), key=f"goal_{month_label}")
        state["goal"] = goal

        st.subheader("Retos")
        for r in CFG["months"][month_label]["retos"]:
            st.markdown(f"- **{r}**")

        st.markdown("---")

        st.subheader("Mis hábitos")
        day = st.selectbox("Día:", list(range(1, DAYS+1)), key=f"day_{month_label}")
        st.caption("Marca lo que lograste hoy.")

        day_key = str(day)
        day_data = state["days"].get(day_key, {h: False for h in HABITS})
        new_day_data = {}
        for h in HABITS:
            new_day_data[h] = st.checkbox(h, value=bool(day_data.get(h, False)), key=f"{month_label}_{day}_{h}")

        state["days"][day_key] = new_day_data

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("Guardar mi día", type="primary", use_container_width=True, key=f"save_{month_label}"):
                save_state(month_label, state)
                st.success(pick_phrase())
        with colB:
            if st.button("Limpiar este día", type="secondary", use_container_width=True, key=f"clear_{month_label}"):
                state["days"][day_key] = {h: False for h in HABITS}
                save_state(month_label, state)
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

        rows = []
        for d in range(1, DAYS+1):
            dd = state["days"].get(str(d), {})
            count = sum(1 for v in dd.values() if v)
            rows.append((d, count))

        cols = st.columns(7)
        for idx, (d, c) in enumerate(rows):
            with cols[idx % 7]:
                st.markdown(f"**{d}** {badge(c)}")

        st.caption("Leyenda: ⬜ 0 | 🟠 1–3 | 🟡 4–7 | 🟢 8–10 | ✅ 11+")

        if state.get("saved_at"):
            st.caption(f"Último guardado: {state['saved_at']}")

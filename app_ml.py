import streamlit as st
import requests
import time
import base64
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse
from pathlib import Path

st.set_page_config(
    page_title="Kryla Pechinchas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ETIQUETA_ML = "krylastore"

CATEGORIAS = {
    "Todos":               None,
    "📱 Celulares":        "MLB1051",
    "💻 Computação":       "MLB1648",
    "🎧 Áudio":            "MLB1144",
    "⚡ Eletrônicos":      "MLB1000",
    "🏠 Eletrodomésticos": "MLB1574",
    "🎮 Games":            "MLB1246",
    "🛋️ Casa":             "MLB5726",
}

def get_b64(filename):
    p = Path(__file__).parent / filename
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

logo_b64 = get_b64("kryla_store1.png")
asa_b64  = get_b64("asafogo.png")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*, *::before, *::after { box-sizing: border-box; font-family: 'Inter', sans-serif !important; }

.stApp { background: #fff7f0 !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── navbar ── */
.navbar {
  background: #fff;
  padding: 0 40px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 3px solid #ff6b1a;
  box-shadow: 0 2px 12px #ff6b1a22;
}
.nav-logo { width: 220px; height: auto; object-fit: contain; }
.nav-badge {
  background: #ff6b1a;
  color: #fff;
  padding: 8px 20px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 2px 8px #ff6b1a44;
}

/* ── hero ── */
.hero {
  background: linear-gradient(135deg, #ff6b1a 0%, #ff8c42 50%, #ffaa6b 100%);
  padding: 32px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.hero-left   { display: flex; align-items: center; gap: 24px; }
.hero-icon   { width: 110px; height: auto; filter: drop-shadow(0 0 20px #fff8); }
.hero-title  { font-size: 32px; font-weight: 900; color: #fff; letter-spacing: -1px; margin: 0; }
.hero-sub    { font-size: 14px; color: #ffe0cc; margin-top: 6px; }
.hero-stats  { display: flex; gap: 32px; }
.hs-num      { font-size: 28px; font-weight: 800; color: #fff; text-align: center; }
.hs-label    { font-size: 11px; color: #ffe0cc; text-align: center; margin-top: 2px; }

/* ── filtros ── */
.filters {
  background: #fff;
  padding: 14px 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #ffe0cc;
  flex-wrap: wrap;
  box-shadow: 0 2px 6px #ff6b1a11;
}
.fchip {
  padding: 8px 20px;
  border-radius: 999px;
  border: 2px solid #ffe0cc;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #ff6b1a;
  white-space: nowrap;
  cursor: pointer;
}
.fchip.active {
  background: #ff6b1a;
  color: #fff;
  border-color: #ff6b1a;
}

/* ── grid ── */
.deals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
  padding: 28px 40px;
}

/* ── card ── */
.deal-card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  border: 2px solid #ffe0cc;
  transition: transform .15s, box-shadow .15s;
  position: relative;
}
.deal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px #ff6b1a22;
  border-color: #ff6b1a;
}
.card-img-wrap {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: #fff7f0;
  overflow: hidden;
}
.card-img-wrap img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 14px;
}
.card-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52px;
}
.card-disc {
  position: absolute;
  top: 12px; left: 12px;
  background: #ff6b1a;
  color: #fff;
  font-size: 13px; font-weight: 800;
  padding: 4px 12px;
  border-radius: 999px;
  z-index: 2;
  box-shadow: 0 2px 8px #ff6b1a66;
}
.card-hot {
  position: absolute;
  top: 12px; right: 12px;
  background: #fff3ed;
  color: #ff6b1a;
  font-size: 10px; font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #ff6b1a66;
  z-index: 2;
}
.card-body  { padding: 16px; }
.card-title {
  font-size: 13px; font-weight: 600; color: #333;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 38px;
  margin-bottom: 12px;
}
.card-price-now { font-size: 22px; font-weight: 800; color: #ff6b1a; }
.card-price-was { font-size: 12px; color: #ccc; text-decoration: line-through; margin-left: 4px; }
.card-economy   { font-size: 11px; color: #e05a00; font-weight: 600; margin-top: 3px; }
.card-store     { font-size: 11px; color: #bbb; margin-top: 8px; }
.card-btn {
  display: block;
  margin: 12px 16px 12px;
  background: #ff6b1a;
  color: #fff !important;
  text-align: center;
  padding: 10px;
  border-radius: 12px;
  font-size: 13px; font-weight: 700;
  text-decoration: none !important;
  box-shadow: 0 3px 10px #ff6b1a44;
}
.card-btn:hover { background: #e55a0a; }
.card-link {
  margin: 0 16px 16px;
  background: #fff7f0;
  border: 1px solid #ffe0cc;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 10px;
  color: #ff6b1a;
  font-family: monospace !important;
  word-break: break-all;
}

/* ── empty ── */
.empty { text-align: center; padding: 80px 20px; }
.emsg  { font-size: 22px; font-weight: 800; color: #ff6b1a; margin-top: 16px; }
.esub  { font-size: 14px; color: #bbb; margin-top: 8px; }

/* ── streamlit overrides ── */
.stButton > button {
  background: #ff6b1a !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  padding: 12px 28px !important;
  width: 100%;
  box-shadow: 0 3px 10px #ff6b1a44 !important;
}
.stButton > button:hover { background: #e55a0a !important; }
div[data-testid="stSlider"] { padding-top: 8px; }
div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
div[data-testid="stSlider"] div[data-testid="stTickBarMax"] { color: #ff6b1a !important; }
</style>
""", unsafe_allow_html=True)


# ─── FUNÇÕES ───────────────────────────────────────────────
def gerar_link(url):
    p = urlparse(url)
    return urlunparse(p._replace(query=urlencode({"matt_tool":"aff_id","matt_word":ETIQUETA_ML})))


def buscar_ml(cat_id, desc_min):
    """Busca SEM autenticação — API pública do ML funciona assim"""
    try:
        r = requests.get(
            "https://api.mercadolibre.com/sites/MLB/search",
            params={
                "category": cat_id,
                "sort": "price_asc",
                "limit": 50,
                "condition": "new",
                "has_pictures": "true",
            },
            timeout=15
        )
        r.raise_for_status()
        items = r.json().get("results", [])
    except Exception as e:
        st.warning(f"Erro ao buscar {cat_id}: {e}")
        return []

    out = []
    for item in items:
        preco = item.get("price", 0)
        orig  = item.get("original_price") or preco
        if orig <= preco or preco == 0: continue
        desc = round((1 - preco / orig) * 100)
        if desc < desc_min: continue
        out.append({
            "id":       item.get("id", ""),
            "titulo":   item.get("title", ""),
            "preco":    preco,
            "original": orig,
            "desconto": desc,
            "economia": round(orig - preco, 2),
            "link":     gerar_link(item.get("permalink", "")),
            "thumb":    item.get("thumbnail", "").replace("I.jpg", "O.jpg"),
            "vendedor": item.get("seller", {}).get("nickname", ""),
            "hora":     datetime.now().strftime("%H:%M"),
            "cat":      "",
        })
    return out


def fmt(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


# ─── ESTADO ────────────────────────────────────────────────
if "deals"    not in st.session_state: st.session_state.deals    = []
if "scan"     not in st.session_state: st.session_state.scan     = None
if "cat"      not in st.session_state: st.session_state.cat      = "Todos"
if "desc_min" not in st.session_state: st.session_state.desc_min = 30

deals   = st.session_state.deals
queimas = sum(1 for d in deals if d["desconto"] >= 50)
eco     = sum(d["economia"] for d in deals)

# ─── NAVBAR ────────────────────────────────────────────────
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo">' \
            if logo_b64 else \
            '<span style="font-size:24px;font-weight:900;color:#ff6b1a">🔥 KRYLA</span>'

st.markdown(f"""
<div class="navbar">
  {logo_html}
  <span class="nav-badge">🔥 {len(deals)} pechinchas hoje</span>
</div>""", unsafe_allow_html=True)

# ─── HERO ──────────────────────────────────────────────────
asa_html = f'<img src="data:image/png;base64,{asa_b64}" class="hero-icon">' \
           if asa_b64 else '<span style="font-size:72px">🔥</span>'

st.markdown(f"""
<div class="hero">
  <div class="hero-left">
    {asa_html}
    <div>
      <div class="hero-title">Caçador de Pechinchas</div>
      <div class="hero-sub">Links <b>krylastore</b> gerados automaticamente · Mercado Livre</div>
    </div>
  </div>
  <div class="hero-stats">
    <div><div class="hs-num">{len(deals)}</div><div class="hs-label">Pechinchas</div></div>
    <div><div class="hs-num">{queimas}</div><div class="hs-label">Queimas</div></div>
    <div><div class="hs-num">R${eco:,.0f}</div><div class="hs-label">Economia</div></div>
  </div>
</div>""", unsafe_allow_html=True)

# ─── CONTROLES ─────────────────────────────────────────────
st.markdown('<div style="background:#fff;padding:16px 40px;border-bottom:1px solid #ffe0cc">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 3, 2])
with c1:
    buscar = st.button("🔍  Buscar pechinchas agora")
with c2:
    desc_min = st.slider("", 10, 70, st.session_state.desc_min,
                         step=5, format="Desconto mínimo: %d%%")
    st.session_state.desc_min = desc_min
with c3:
    cat_sel = st.selectbox("", list(CATEGORIAS.keys()),
                           index=list(CATEGORIAS.keys()).index(st.session_state.cat))
    st.session_state.cat = cat_sel
st.markdown('</div>', unsafe_allow_html=True)

# ─── CHIPS ─────────────────────────────────────────────────
chips = "".join(
    f'<span class="fchip {"active" if n == st.session_state.cat else ""}">{n}</span>'
    for n in CATEGORIAS
)
st.markdown(f'<div class="filters">{chips}</div>', unsafe_allow_html=True)

# ─── BUSCA ─────────────────────────────────────────────────
if buscar:
    cats = {k: v for k, v in CATEGORIAS.items() if k != "Todos" and v}
    novos = []
    ids   = {d["id"] for d in st.session_state.deals}
    prog  = st.progress(0, text="Iniciando busca...")

    for i, (nome, cat_id) in enumerate(cats.items()):
        prog.progress(i / len(cats), text=f"Varrendo {nome}...")
        for d in buscar_ml(cat_id, desc_min):
            if d["id"] not in ids:
                d["cat"] = nome
                novos.append(d)
                ids.add(d["id"])

    prog.progress(1.0, text="Concluído!")
    time.sleep(0.4)
    prog.empty()

    st.session_state.deals = novos + st.session_state.deals
    st.session_state.scan  = datetime.now().strftime("%H:%M:%S")

    if novos:
        st.success(f"✅ {len(novos)} pechinchas encontradas!")
    else:
        st.warning("⚠️ Nenhuma pechincha nova agora. O ML pode estar limitando — tente novamente em 1 minuto.")
    st.rerun()

# ─── GRID ──────────────────────────────────────────────────
deals  = st.session_state.deals
exibir = deals if st.session_state.cat == "Todos" else \
         [d for d in deals if d.get("cat") == st.session_state.cat]

if not deals:
    st.markdown(f"""
    <div class="empty">
      {asa_html.replace('class="hero-icon"','style="width:120px;filter:drop-shadow(0 0 20px #ff6b1a88)"') if asa_b64 else '<div style="font-size:80px">🔥</div>'}
      <div class="emsg">Nenhuma pechincha ainda!</div>
      <div class="esub">Clique em <b style="color:#ff6b1a">Buscar pechinchas agora</b> para começar</div>
    </div>""", unsafe_allow_html=True)
else:
    html = '<div class="deals-grid">'
    for d in exibir:
        hot = '<span class="card-hot">🔥 QUEIMA</span>' if d["desconto"] >= 50 else ""
        img = f'<img src="{d["thumb"]}" onerror="this.style.display=\'none\'">' \
              if d["thumb"] else '<div class="card-placeholder">🛒</div>'
        html += f"""
        <div class="deal-card">
          <div class="card-img-wrap">{img}
            <span class="card-disc">-{d["desconto"]}%</span>{hot}
          </div>
          <div class="card-body">
            <div class="card-title">{d["titulo"]}</div>
            <div>
              <span class="card-price-now">{fmt(d["preco"])}</span>
              <span class="card-price-was">{fmt(d["original"])}</span>
            </div>
            <div class="card-economy">Economia: {fmt(d["economia"])}</div>
            <div class="card-store">🏪 {d["vendedor"]} · ⏱ {d["hora"]}</div>
          </div>
          <a href="{d['link']}" target="_blank" class="card-btn">🛒 Ver oferta no ML</a>
          <div class="card-link">🔗 {d['link']}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    linhas = [f"{d['titulo']} | {fmt(d['preco'])} (-{d['desconto']}%) | {d['link']}" for d in deals]
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button("⬇️ Exportar lista TXT", "\n".join(linhas),
                           f"kryla_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", "text/plain")

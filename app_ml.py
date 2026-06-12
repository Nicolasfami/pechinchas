import streamlit as st
import requests
import time
import base64
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse
from pathlib import Path

st.set_page_config(
    page_title="Kryla · Pechinchas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CREDENCIAIS ML ────────────────────────────────────────
ML_CLIENT_ID     = "1059265064005867"
ML_CLIENT_SECRET = "0EICxKO8e82e7yIclw5tBscSDMP2UWUP"
ETIQUETA_ML      = "krylastore"

CATEGORIAS = {
    "📱 Celulares":        "MLB1051",
    "💻 Computação":       "MLB1648",
    "🎧 Áudio":            "MLB1144",
    "⚡ Eletrônicos":      "MLB1000",
    "🏠 Eletrodomésticos": "MLB1574",
    "🎮 Games":            "MLB1246",
    "🛋️ Casa":             "MLB5726",
}

# ─── ESTILO KRYLA ──────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

  * { font-family: 'Inter', sans-serif !important; }

  .stApp { background: #111318; }
  [data-testid="stSidebar"] {
    background: #16191f;
    border-right: 1px solid #23272f;
  }

  /* header */
  .kryla-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 28px;
    background: #16191f;
    border: 1px solid #23272f;
    border-radius: 16px;
    margin-bottom: 24px;
  }
  .kryla-title {
    font-size: 22px;
    font-weight: 900;
    color: #fff;
    letter-spacing: -0.5px;
  }
  .kryla-sub { font-size: 13px; color: #666; margin-top: 3px; }

  /* stat cards */
  .stat-card {
    background: #16191f;
    border: 1px solid #23272f;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
  }
  .stat-num   { font-size: 28px; font-weight: 800; color: #fff; }
  .stat-label { font-size: 12px; color: #555; margin-top: 4px; }

  /* deal row */
  .deal-row {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #16191f;
    border: 1px solid #23272f;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color .15s;
  }
  .deal-row:hover { border-color: #ff6b1a; }

  /* badges */
  .badge-hot  { background:#2a0f00; color:#ff6b1a; border:1px solid #ff6b1a44;
                padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
  .badge-good { background:#0a2200; color:#5ddd6e; border:1px solid #5ddd6e44;
                padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
  .badge-ok   { background:#221a00; color:#ffd166; border:1px solid #ffd16644;
                padding:3px 10px; border-radius:20px; font-size:11px; }

  /* desconto pill */
  .desc-pill {
    background: linear-gradient(135deg, #ff6b1a, #ff3d00);
    color: #fff;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 800;
  }

  /* preços */
  .price-now { font-size: 22px; font-weight: 800; color: #5ddd6e; }
  .price-was { font-size: 13px; color: #444; text-decoration: line-through; }

  /* link afiliado */
  .aff-box {
    background: #0d0f14;
    border: 1px solid #23272f;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: monospace !important;
    font-size: 11px;
    color: #ff6b1a;
    word-break: break-all;
    margin-top: 8px;
  }

  /* botões */
  .stButton > button {
    background: #1a1d24 !important;
    color: #ff6b1a !important;
    border: 1px solid #ff6b1a44 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 12px !important;
  }
  .stButton > button:hover {
    background: #ff6b1a !important;
    color: #fff !important;
    border-color: #ff6b1a !important;
  }

  /* sidebar */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] .stMarkdown { color: #999 !important; }

  /* progress */
  .stProgress > div > div { background: #ff6b1a !important; }

  /* inputs */
  .stTextInput input, .stSelectbox select {
    background: #0d0f14 !important;
    border: 1px solid #23272f !important;
    color: #fff !important;
    border-radius: 8px !important;
  }

  hr { border-color: #23272f !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ─── TOKEN ML ──────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_token():
    try:
        r = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     ML_CLIENT_ID,
                "client_secret": ML_CLIENT_SECRET,
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        st.sidebar.error(f"Erro token ML: {e}")
        return None


# ─── FUNÇÕES ───────────────────────────────────────────────
def gerar_link_afiliado(url: str) -> str:
    parsed = urlparse(url)
    params = {"matt_tool": "aff_id", "matt_word": ETIQUETA_ML}
    return urlunparse(parsed._replace(query=urlencode(params)))


def buscar_ml(categoria_id: str, desconto_min: int, token: str) -> list:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = requests.get(
            "https://api.mercadolibre.com/sites/MLB/search",
            params={"category": categoria_id, "sort": "price_asc",
                    "limit": 50, "condition": "new"},
            headers=headers,
            timeout=12,
        )
        r.raise_for_status()
        items = r.json().get("results", [])
    except Exception as e:
        return []

    resultado = []
    for item in items:
        preco    = item.get("price", 0)
        original = item.get("original_price") or preco
        if original <= preco or preco == 0:
            continue
        desc = round((1 - preco / original) * 100)
        if desc < desconto_min:
            continue
        link = item.get("permalink", "")
        resultado.append({
            "id":       item.get("id", ""),
            "titulo":   item.get("title", ""),
            "preco":    preco,
            "original": original,
            "desconto": desc,
            "economia": round(original - preco, 2),
            "link_aff": gerar_link_afiliado(link),
            "thumb":    item.get("thumbnail", "").replace("I.jpg", "O.jpg"),
            "vendedor": item.get("seller", {}).get("nickname", ""),
            "hora":     datetime.now().strftime("%H:%M"),
        })
    return resultado


def nivel(desc):
    if desc >= 50: return "🔥 Queima", "badge-hot"
    if desc >= 35: return "⚡ Forte",  "badge-good"
    return           "💰 Boa",         "badge-ok"

def fmt(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configurações")
    st.markdown("---")
    cats_sel = st.multiselect("Categorias", list(CATEGORIAS.keys()),
                              default=["📱 Celulares","🎧 Áudio","🎮 Games"])
    desc_min = st.slider("Desconto mínimo", 10, 70, 30, step=5, format="%d%%")
    st.markdown("---")
    auto = st.toggle("Auto-varredura", value=False)
    if auto:
        intervalo = st.select_slider("Intervalo", [1,2,5,10,15,30],
                                     value=5, format_func=lambda x: f"{x} min")
    st.markdown("---")
    st.markdown(f"**Etiqueta:** `{ETIQUETA_ML}`")
    st.caption("Links gerados automaticamente")


# ─── HEADER ────────────────────────────────────────────────
st.markdown("""
<div class="kryla-header">
  <div style="font-size:40px;line-height:1">🔥</div>
  <div>
    <div class="kryla-title">KRYLA · Caçador de Pechinchas</div>
    <div class="kryla-sub">Mercado Livre · Links de afiliado krylastore gerados automaticamente</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── ESTADO ────────────────────────────────────────────────
if "deals" not in st.session_state: st.session_state.deals = []
if "scan"  not in st.session_state: st.session_state.scan  = None

# ─── BUSCAR ────────────────────────────────────────────────
col_btn, col_info = st.columns([2, 5])
with col_btn:
    buscar = st.button("🔍 Buscar pechinchas agora", use_container_width=True)
with col_info:
    if st.session_state.scan:
        st.caption(f"Última varredura: {st.session_state.scan} · "
                   f"{len(st.session_state.deals)} pechinchas")

if buscar:
    if not cats_sel:
        st.warning("Selecione ao menos uma categoria.")
    else:
        token = get_token()
        novos = []
        prog  = st.progress(0, text="Buscando...")
        ids   = {d["id"] for d in st.session_state.deals}

        for i, nome in enumerate(cats_sel):
            prog.progress(i/len(cats_sel), text=f"Varrendo {nome}...")
            for d in buscar_ml(CATEGORIAS[nome], desc_min, token):
                if d["id"] not in ids:
                    novos.append(d)
                    ids.add(d["id"])

        prog.progress(1.0, text="Pronto!")
        time.sleep(0.3)
        prog.empty()

        st.session_state.deals = novos + st.session_state.deals
        st.session_state.scan  = datetime.now().strftime("%H:%M:%S")

        if novos:
            st.success(f"✅ {len(novos)} pechinchas encontradas!")
        else:
            st.info("Nenhuma pechincha nova agora. Tente em alguns minutos.")

# ─── STATS ─────────────────────────────────────────────────
deals = st.session_state.deals
if deals:
    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    queimas = sum(1 for d in deals if d["desconto"]>=50)
    eco     = sum(d["economia"] for d in deals)
    maior   = max(deals, key=lambda d: d["desconto"])

    with c1: st.markdown(f'<div class="stat-card"><div class="stat-num">{len(deals)}</div><div class="stat-label">Pechinchas hoje</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#ff6b1a">{queimas}</div><div class="stat-label">Queimas totais</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#5ddd6e">R${eco:,.0f}</div><div class="stat-label">Economia potencial</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#ffd166">-{maior["desconto"]}%</div><div class="stat-label">Maior desconto</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # filtros
    f1,f2,f3 = st.columns([2,2,3])
    with f1: fnivel = st.selectbox("Nível", ["Todos","🔥 Queima (50%+)","⚡ Forte (35%+)","💰 Boa oferta"])
    with f2: forden = st.selectbox("Ordenar", ["Maior desconto","Menor preço","Maior economia"])
    with f3: ftexto = st.text_input("Buscar", placeholder="Ex: fone, TV, celular...")

    exibir = deals.copy()
    if fnivel == "🔥 Queima (50%+)":   exibir = [d for d in exibir if d["desconto"]>=50]
    elif fnivel == "⚡ Forte (35%+)":  exibir = [d for d in exibir if d["desconto"]>=35]
    if ftexto: exibir = [d for d in exibir if ftexto.lower() in d["titulo"].lower()]
    if forden == "Maior desconto": exibir.sort(key=lambda d: d["desconto"], reverse=True)
    elif forden == "Menor preço":  exibir.sort(key=lambda d: d["preco"])
    else:                          exibir.sort(key=lambda d: d["economia"], reverse=True)

    st.caption(f"Mostrando {len(exibir)} de {len(deals)} pechinchas")
    st.markdown("---")

    # ─── CARDS EM FILEIRA ──────────────────────────────────
    for d in exibir:
        rotulo, classe = nivel(d["desconto"])
        ci, cd = st.columns([1, 6])

        with ci:
            if d["thumb"]:
                try: st.image(d["thumb"], width=85)
                except: st.markdown("🖼️")

        with cd:
            st.markdown(
                f'<span class="{classe}">{rotulo}</span> '
                f'<span class="desc-pill">-{d["desconto"]}%</span> '
                f'<span style="font-size:11px;color:#444;margin-left:6px">⏱ {d["hora"]}</span>',
                unsafe_allow_html=True)

            st.markdown(f'<span style="font-size:15px;font-weight:700;color:#fff">{d["titulo"]}</span>', unsafe_allow_html=True)

            st.markdown(
                f'<span class="price-now">{fmt(d["preco"])}</span> '
                f'<span class="price-was">{fmt(d["original"])}</span> '
                f'<span style="color:#555;font-size:12px"> · economia {fmt(d["economia"])}</span>',
                unsafe_allow_html=True)

            st.caption(f"🏪 {d['vendedor']}")

            st.markdown(f'<div class="aff-box">🔗 {d["link_aff"]}</div>', unsafe_allow_html=True)

            b1, b2 = st.columns([1,1])
            with b1: st.link_button("🛒 Ver no ML", d["link_aff"], use_container_width=True)
            with b2:
                if st.button("📋 Copiar", key=f"c_{d['id']}", use_container_width=True):
                    st.code(d["link_aff"], language=None)

        st.markdown('<hr style="border-color:#1e2128;margin:6px 0">', unsafe_allow_html=True)

    if exibir:
        st.markdown("---")
        linhas = [f"{d['titulo']} | {fmt(d['preco'])} (-{d['desconto']}%) | {d['link_aff']}" for d in exibir]
        st.download_button("⬇️ Exportar TXT", "\n".join(linhas),
                           f"kryla_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", "text/plain")

else:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px">
      <div style="font-size:72px;margin-bottom:20px">🔥</div>
      <div style="font-size:22px;color:#fff;font-weight:800">Nenhuma pechincha ainda</div>
      <div style="font-size:14px;color:#555;margin-top:10px">
        Selecione as categorias e clique em
        <span style="color:#ff6b1a;font-weight:700">Buscar pechinchas agora</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

if auto and st.session_state.scan:
    time.sleep(intervalo * 60)
    st.rerun()

import streamlit as st
import requests
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse

st.set_page_config(
    page_title="Krylastore · Pechinchas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

ETIQUETA_ML = "krylastore"

CATEGORIAS = {
    "📱 Celulares":        "MLB1051",
    "💻 Computação":       "MLB1648",
    "🎧 Áudio":            "MLB1144",
    "⚡ Eletrônicos":      "MLB1000",
    "🏠 Eletrodomésticos": "MLB1574",
    "🎮 Games":            "MLB1246",
    "🛋️ Casa":             "MLB5726",
}

st.markdown("""
<style>
  /* ── base ── */
  .stApp { background: #f0f4ff; }
  [data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #dde6ff;
  }

  /* ── header ── */
  .header-box {
    background: linear-gradient(135deg, #1a6fff 0%, #0ad4fa 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 4px 24px #1a6fff33;
  }
  .header-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .header-sub { font-size: 13px; color: #d0eeff; margin: 4px 0 0; }

  /* ── stat cards ── */
  .stat-card {
    background: #ffffff;
    border: 1.5px solid #dde6ff;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 2px 12px #1a6fff11;
  }
  .stat-num   { font-size: 30px; font-weight: 800; color: #1a6fff; }
  .stat-label { font-size: 12px; color: #8899bb; margin-top: 4px; }

  /* ── badges ── */
  .badge-hot  {
    background: #fff0f0; color: #e03030;
    border: 1.5px solid #ffbbbb;
    padding: 3px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 700;
  }
  .badge-good {
    background: #f0fff4; color: #1a9e50;
    border: 1.5px solid #b2f0c8;
    padding: 3px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 600;
  }
  .badge-ok {
    background: #fffbf0; color: #b87800;
    border: 1.5px solid #ffe599;
    padding: 3px 12px; border-radius: 20px;
    font-size: 12px;
  }

  /* ── discount pill ── */
  .discount {
    background: #1a6fff;
    color: #fff;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 2px 8px #1a6fff44;
  }

  /* ── deal card ── */
  .deal-card {
    background: #ffffff;
    border: 1.5px solid #dde6ff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 12px #1a6fff0d;
    transition: box-shadow .2s, border-color .2s;
  }
  .deal-card:hover {
    border-color: #1a6fff;
    box-shadow: 0 4px 20px #1a6fff22;
  }

  /* ── prices ── */
  .price-now  { font-size: 26px; font-weight: 800; color: #1a9e50; }
  .price-was  { font-size: 14px; color: #aabbcc; text-decoration: line-through; }

  /* ── link afiliado ── */
  .aff-link {
    background: #f0f7ff;
    border: 1.5px solid #c0d8ff;
    border-radius: 10px;
    padding: 10px 14px;
    font-family: monospace;
    font-size: 11px;
    color: #4477bb;
    word-break: break-all;
    margin-top: 10px;
  }
  .aff-link span { color: #1a6fff; font-weight: 600; }

  /* ── botões ── */
  .stButton > button {
    background: #f0f7ff !important;
    color: #1a6fff !important;
    border: 1.5px solid #c0d8ff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
  }
  .stButton > button:hover {
    background: #1a6fff !important;
    color: #fff !important;
    border-color: #1a6fff !important;
  }

  /* ── sidebar labels ── */
  .stSidebar label, .stSidebar .stMarkdown {
    color: #334466 !important;
  }

  /* ── divider ── */
  hr { border-color: #dde6ff !important; }

  /* ── esconde padrão streamlit ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)


def gerar_link_afiliado(url: str) -> str:
    parsed = urlparse(url)
    params = {"matt_tool": "aff_id", "matt_word": ETIQUETA_ML}
    return urlunparse(parsed._replace(query=urlencode(params)))


def buscar_ml(categoria_id: str, desconto_min: int, limite: int = 48) -> list:
    try:
        resp = requests.get(
            "https://api.mercadolibre.com/sites/MLB/search",
            params={"category": categoria_id, "sort": "price_asc",
                    "limit": limite, "condition": "new"},
            timeout=12,
        )
        resp.raise_for_status()
        items = resp.json().get("results", [])
    except Exception as e:
        st.sidebar.error(f"Erro API ML: {e}")
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
        link_orig = item.get("permalink", "")
        resultado.append({
            "id":        item.get("id", ""),
            "titulo":    item.get("title", ""),
            "preco":     preco,
            "original":  original,
            "desconto":  desc,
            "economia":  round(original - preco, 2),
            "link_orig": link_orig,
            "link_aff":  gerar_link_afiliado(link_orig),
            "thumb":     item.get("thumbnail", "").replace("I.jpg", "O.jpg"),
            "vendedor":  item.get("seller", {}).get("nickname", ""),
            "achado_em": datetime.now().strftime("%H:%M:%S"),
        })
    return resultado


def nivel(desc: int):
    if desc >= 50: return "🔥 Queima total",  "badge-hot"
    if desc >= 35: return "⚡ Oferta forte",  "badge-good"
    return           "💰 Boa oferta",          "badge-ok"


# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")
    cats_sel = st.multiselect(
        "Categorias",
        list(CATEGORIAS.keys()),
        default=["📱 Celulares", "🎧 Áudio", "🎮 Games"],
    )
    desc_min = st.slider("Desconto mínimo", 10, 70, 30, step=5, format="%d%%")
    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-varredura", value=False)
    if auto_refresh:
        intervalo = st.select_slider(
            "Intervalo", [1, 2, 5, 10, 15, 30],
            value=5, format_func=lambda x: f"{x} min"
        )
    st.markdown("---")
    st.markdown(f"**Etiqueta:** `{ETIQUETA_ML}`")
    st.caption("Links gerados automaticamente com sua etiqueta krylastore")


# ── HEADER ───────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <div style="font-size:42px;line-height:1">🔥</div>
  <div>
    <p class="header-title">Krylastore · Caçador de Pechinchas</p>
    <p class="header-sub">Mercado Livre · Links de afiliado gerados automaticamente</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ESTADO ───────────────────────────────────────────────
if "deals"       not in st.session_state: st.session_state.deals = []
if "ultima_scan" not in st.session_state: st.session_state.ultima_scan = None

# ── BOTÃO BUSCAR ─────────────────────────────────────────
col_btn, col_status = st.columns([2, 5])
with col_btn:
    buscar = st.button("🔍 Buscar pechinchas agora", use_container_width=True)
with col_status:
    if st.session_state.ultima_scan:
        st.caption(f"Última varredura: {st.session_state.ultima_scan} · "
                   f"{len(st.session_state.deals)} pechinchas encontradas")

# ── BUSCA ─────────────────────────────────────────────────
if buscar:
    if not cats_sel:
        st.warning("Selecione ao menos uma categoria.")
    else:
        novos = []
        prog  = st.progress(0, text="Iniciando varredura...")
        ids_existentes = {d["id"] for d in st.session_state.deals}

        for i, nome_cat in enumerate(cats_sel):
            prog.progress(i / len(cats_sel), text=f"Varrendo {nome_cat}...")
            for d in buscar_ml(CATEGORIAS[nome_cat], desc_min):
                if d["id"] not in ids_existentes:
                    novos.append(d)
                    ids_existentes.add(d["id"])

        prog.progress(1.0, text="Concluído!")
        time.sleep(0.4)
        prog.empty()

        st.session_state.deals      = novos + st.session_state.deals
        st.session_state.ultima_scan = datetime.now().strftime("%H:%M:%S")

        if novos:
            st.success(f"✅ {len(novos)} pechinchas novas encontradas!")
        else:
            st.info("Nenhuma pechincha nova agora. Tente em alguns minutos.")

# ── STATS ────────────────────────────────────────────────
deals = st.session_state.deals
if deals:
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    queimas       = sum(1 for d in deals if d["desconto"] >= 50)
    economia_total = sum(d["economia"] for d in deals)
    maior         = max(deals, key=lambda d: d["desconto"])

    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(deals)}</div>'
                    f'<div class="stat-label">Pechinchas hoje</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#e03030">'
                    f'{queimas}</div><div class="stat-label">Queimas totais</div></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#1a9e50">'
                    f'R${economia_total:,.0f}</div>'
                    f'<div class="stat-label">Economia potencial</div></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#b87800">'
                    f'-{maior["desconto"]}%</div>'
                    f'<div class="stat-label">Maior desconto</div></div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    # ── FILTROS ──────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        filtro_nivel = st.selectbox("Filtrar por nível", [
            "Todos", "🔥 Queima total (50%+)",
            "⚡ Oferta forte (35%+)", "💰 Boa oferta"
        ])
    with fc2:
        ordenar = st.selectbox("Ordenar por", [
            "Maior desconto", "Menor preço",
            "Maior economia", "Mais recente"
        ])
    with fc3:
        busca_texto = st.text_input("🔎 Buscar produto",
                                    placeholder="Ex: fone, celular...")

    exibir = deals.copy()
    if filtro_nivel == "🔥 Queima total (50%+)":
        exibir = [d for d in exibir if d["desconto"] >= 50]
    elif filtro_nivel == "⚡ Oferta forte (35%+)":
        exibir = [d for d in exibir if d["desconto"] >= 35]
    if busca_texto:
        exibir = [d for d in exibir if busca_texto.lower() in d["titulo"].lower()]
    if ordenar == "Maior desconto":
        exibir.sort(key=lambda d: d["desconto"], reverse=True)
    elif ordenar == "Menor preço":
        exibir.sort(key=lambda d: d["preco"])
    elif ordenar == "Maior economia":
        exibir.sort(key=lambda d: d["economia"], reverse=True)

    st.caption(f"Mostrando {len(exibir)} de {len(deals)} pechinchas")

    # ── CARDS ────────────────────────────────────────────
    for d in exibir:
        rotulo, classe = nivel(d["desconto"])

        col_img, col_info = st.columns([1, 5])
        with col_img:
            if d["thumb"]:
                try:    st.image(d["thumb"], width=90)
                except: st.markdown("🖼️")

        with col_info:
            st.markdown(
                f'<span class="{classe}">{rotulo}</span> '
                f'&nbsp;<span class="discount">-{d["desconto"]}%</span> '
                f'<span style="font-size:11px;color:#aabbcc;margin-left:8px">'
                f'⏱ {d["achado_em"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**{d['titulo']}**")
            economia_fmt = f"R$ {d['economia']:,.2f}".replace(",","X").replace(".",",").replace("X",".")
            preco_fmt    = f"R$ {d['preco']:,.2f}".replace(",","X").replace(".",",").replace("X",".")
            orig_fmt     = f"R$ {d['original']:,.2f}".replace(",","X").replace(".",",").replace("X",".")
            st.markdown(
                f'<span class="price-now">{preco_fmt}</span>'
                f'&nbsp;<span class="price-was">{orig_fmt}</span>'
                f'&nbsp;<span style="color:#8899bb;font-size:13px">economia de {economia_fmt}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"🏪 {d['vendedor']}")
            st.markdown(
                f'<div class="aff-link">🔗 Seu link afiliado: '
                f'<span>{d["link_aff"]}</span></div>',
                unsafe_allow_html=True,
            )
            cb1, cb2 = st.columns([1, 1])
            with cb1:
                st.link_button("🛒 Ver no ML", d["link_aff"], use_container_width=True)
            with cb2:
                if st.button("📋 Copiar link", key=f"cp_{d['id']}", use_container_width=True):
                    st.code(d["link_aff"])

        st.markdown('<hr style="border-color:#dde6ff;margin:8px 0">', unsafe_allow_html=True)

    # ── EXPORTAR ─────────────────────────────────────────
    if exibir:
        st.markdown("---")
        linhas = [f"{d['titulo']} | R${d['preco']} (-{d['desconto']}%) | {d['link_aff']}"
                  for d in exibir]
        st.download_button(
            "⬇️ Exportar lista (TXT)",
            data="\n".join(linhas),
            file_name=f"pechinchas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px">
      <div style="font-size:64px;margin-bottom:16px">🔍</div>
      <div style="font-size:20px;color:#334466;font-weight:700">Nenhuma pechincha ainda</div>
      <div style="font-size:14px;color:#8899bb;margin-top:8px">
        Selecione as categorias e clique em
        <b style="color:#1a6fff">Buscar pechinchas agora</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

if auto_refresh and st.session_state.ultima_scan:
    time.sleep(intervalo * 60)
    st.rerun()

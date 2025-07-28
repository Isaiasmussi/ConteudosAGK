import streamlit as st
import datetime
import sqlite3
from calendar import monthcalendar
from dateutil.relativedelta import relativedelta

# --- Configurações da Página ---
st.set_page_config(
    page_title="Agendador de Conteúdo - Agrolink",
    page_icon="https://www.agrolink.com.br/images/icons/favicon-32x32-24-v3.png",
    layout="wide"
)

# --- Configuração do Banco de Dados SQLite ---
DB_NAME = "agrolink_calendar.db"

def init_db():
    """Cria a tabela de eventos no banco de dados se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def load_events():
    """Carrega todos os eventos do banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, event_date, type FROM events")
    events = []
    for row in cursor.fetchall():
        events.append({
            "id": row[0],
            "title": row[1],
            "date": datetime.datetime.strptime(row[2], '%Y-%m-%d').date(),
            "type": row[3]
        })
    conn.close()
    return events

def save_event(title, event_date, event_type):
    """Salva um novo evento no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, event_date, type) VALUES (?, ?, ?)",
        (title, event_date.strftime('%Y-%m-%d'), event_type)
    )
    conn.commit()
    conn.close()

# Inicializa o banco de dados na primeira execução
init_db()


# --- CSS Customizado ---
st.markdown("""
<style>
    /* Esconde o menu hamburger e o footer do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    /* Alinhamento vertical para os elementos do cabeçalho */
    div[data-testid="stHorizontalBlock"] > div {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .calendar-day {
        border-right: 1px solid #444;
        border-bottom: 1px solid #444;
        border-radius: 0;
        padding: 8px;
        height: 140px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
        overflow-y: auto;
    }
    .calendar-day-first { border-left: 1px solid #444; }
    .calendar-week-first .calendar-day { border-top: 1px solid #444; }
    .other-month .day-number { color: #666; }
    .day-number {
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 8px;
        padding: 4px 8px;
        border-radius: 50%;
        line-height: 1;
        text-align: center;
        min-width: 28px;
    }
    .today .day-number {
        background-color: #1a73e8;
        color: white;
    }
    .event-card {
        padding: 2px 5px;
        border-radius: 4px;
        margin-bottom: 4px;
        width: 100%;
        font-size: 0.85em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do Estado da Sessão ---
if 'events' not in st.session_state:
    st.session_state.events = load_events()

if 'content_types' not in st.session_state:
    st.session_state.content_types = ["Notícia", "Post Instagram", "Publi", "Reels", "Artigo Blog"]

if 'current_view_date' not in st.session_state:
    st.session_state.current_view_date = datetime.date.today().replace(day=1)

# --- Funções Auxiliares ---
def get_color_for_type(content_type):
    hash_val = hash(content_type)
    r, g, b = (hash_val & 0xFF0000) >> 16, (hash_val & 0x00FF00) >> 8, hash_val & 0x0000FF
    return f"#{r:02x}{g:02x}{b:02x}"

def change_month(delta):
    st.session_state.current_view_date += relativedelta(months=delta)

def go_to_today():
    st.session_state.current_view_date = datetime.date.today().replace(day=1)


# --- Barra Lateral (Sidebar) ---
logo_url = "https://www.agrolink.com.br/images/logos/agrolink-logo-v2.png"
st.sidebar.image(logo_url, use_column_width='always') # CORRIGIDO: use_column_width='always'
st.sidebar.title("Agendador")

with st.sidebar.form("new_event_form", clear_on_submit=True):
    st.subheader("Agendar Conteúdo")
    event_title = st.text_input("Título do Conteúdo:")
    event_date = st.date_input("Data:", value=datetime.date.today())
    event_type = st.selectbox("Formato do Conteúdo:", options=st.session_state.content_types)
    submitted = st.form_submit_button("Salvar Agendamento", use_container_width=True)

    if submitted and event_title:
        save_event(event_title, event_date, event_type)
        st.session_state.events = load_events()
        st.sidebar.success("Conteúdo agendado e salvo!")
        st.experimental_rerun()
    elif submitted:
        st.sidebar.error("Por favor, adicione um título.")

with st.sidebar.expander("Gerenciar Formatos de Conteúdo"):
    with st.form("new_type_form", clear_on_submit=True):
        new_type_name = st.text_input("Nome do Novo Formato:")
        add_type_submitted = st.form_submit_button("Adicionar Formato", use_container_width=True)
        if add_type_submitted and new_type_name and new_type_name not in st.session_state.content_types:
            st.session_state.content_types.append(new_type_name)
            st.success(f"Formato '{new_type_name}' adicionado!")
            st.experimental_rerun()
        elif add_type_submitted:
            st.warning("Formato inválido ou já existente.")

    st.write("Formatos existentes:")
    for content_type in st.session_state.content_types:
        color = get_color_for_type(content_type)
        st.markdown(f"<span style='color:{color}; font-weight: bold;'>●</span> {content_type}", unsafe_allow_html=True)


# --- Calendário Principal ---
month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
view_date = st.session_state.current_view_date

# Cabeçalho de navegação (versão robusta)
st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
        <h1 style="margin: 0;">Agenda</h1>
        <div style="display: flex; align-items: center;">
            <!-- Botões funcionais do Streamlit (serão colocados abaixo e podem ser escondidos se necessário) -->
        </div>
        <h2 style="margin: 0;">{month_names_pt[view_date.month]} de {view_date.year}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Botões de navegação (separados para estabilidade)
nav_cols = st.columns([6, 1, 0.5, 0.5, 5])
with nav_cols[1]:
    st.button("Hoje", on_click=go_to_today, use_container_width=True)
with nav_cols[2]:
    st.button("<", on_click=change_month, args=(-1,), use_container_width=True, key="prev_month")
with nav_cols[3]:
    st.button(">", on_click=change_month, args=(1,), use_container_width=True, key="next_month")


# Dias da semana
week_headers = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
cols = st.columns(7)
for col, header in zip(cols, week_headers):
    col.markdown(f"<div style='text-align: center; font-weight: bold; color: #aaa; margin: 10px 0;'>{header}</div>", unsafe_allow_html=True)

# Lógica de Geração da Grade do Calendário
today = datetime.date.today()
first_day_of_month = view_date.replace(day=1)
start_date = first_day_of_month - datetime.timedelta(days=(first_day_of_month.weekday() + 1) % 7)

for week_num in range(6):
    is_first_week_class = "calendar-week-first" if week_num == 0 else ""
    st.markdown(f"<div class='{is_first_week_class}'>", unsafe_allow_html=True)
    cols = st.columns(7)
    for day_num in range(7):
        current_date = start_date + datetime.timedelta(days=(week_num * 7 + day_num))
        
        with cols[day_num]:
            day_class = "calendar-day" + (" calendar-day-first" if day_num == 0 else "")
            if current_date.month != view_date.month: day_class += " other-month"
            if current_date == today: day_class += " today"
            
            day_number_html = f"<div class='day-number'>{current_date.day}</div>"
            
            events_for_day = sorted([e for e in st.session_state.events if e["date"] == current_date], key=lambda x: x['title'])
            for event in events_for_day:
                event_color = get_color_for_type(event['type'])
                day_number_html += f"""
                <div class="event-card" style="background-color: {event_color}40; border-left: 3px solid {event_color};" title="{event['type']}: {event['title']}">
                    {event['title']}
                </div>
                """
            st.markdown(f"<div class='{day_class}'>{day_number_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

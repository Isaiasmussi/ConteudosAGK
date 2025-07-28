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

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Cria as tabelas no banco de dados se elas não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabela de eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)
    # Tabela de tipos de conteúdo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    # Popula com valores padrão se estiver vazia
    cursor.execute("SELECT COUNT(*) FROM content_types")
    if cursor.fetchone()[0] == 0:
        default_types = ["Notícia", "Post Instagram", "Publi", "Reels", "Artigo Blog"]
        for c_type in default_types:
            cursor.execute("INSERT INTO content_types (name) VALUES (?)", (c_type,))
    conn.commit()
    conn.close()

# --- Funções de CRUD (Create, Read, Update, Delete) ---

def load_data(table):
    """Carrega todos os dados de uma tabela."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = [dict(row) for row in cursor.fetchall()]
    # Converte a data de string para objeto date
    if table == 'events':
        for item in data:
            item['date'] = datetime.datetime.strptime(item['event_date'], '%Y-%m-%d').date()
    conn.close()
    return data

def save_event(title, event_date, event_type):
    """Salva um novo evento no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, event_date, type) VALUES (?, ?, ?)",
        (title, event_date.strftime('%Y-%m-%d'), event_type)
    )
    conn.commit()
    conn.close()

def delete_event(event_id):
    """Deleta um evento pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

def save_content_type(name):
    """Salva um novo tipo de conteúdo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO content_types (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning("Este formato de conteúdo já existe.")
    finally:
        conn.close()

def update_content_type(old_name, new_name):
    """Atualiza o nome de um tipo de conteúdo e propaga a mudança para os eventos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Atualiza na tabela de tipos
    cursor.execute("UPDATE content_types SET name = ? WHERE name = ?", (new_name, old_name))
    # Atualiza em todos os eventos existentes
    cursor.execute("UPDATE events SET type = ? WHERE type = ?", (new_name, old_name))
    conn.commit()
    conn.close()

def delete_content_type(name):
    """Deleta um tipo de conteúdo se não estiver em uso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events WHERE type = ?", (name,))
    if cursor.fetchone()[0] > 0:
        st.error(f"Não é possível excluir '{name}', pois ele está sendo usado em agendamentos.")
    else:
        cursor.execute("DELETE FROM content_types WHERE name = ?", (name,))
        conn.commit()
        st.success(f"Formato '{name}' excluído.")
    conn.close()

# Inicializa o banco de dados
init_db()

# --- CSS Customizado ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    div[data-testid="stHorizontalBlock"] > div { display: flex; flex-direction: column; justify-content: center; }
    .calendar-day-button {
        background-color: transparent;
        border: none;
        width: 100%;
        height: 140px;
        border-right: 1px solid #444;
        border-bottom: 1px solid #444;
        border-radius: 0;
        padding: 8px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
        overflow-y: auto;
    }
    .calendar-day-button:hover { background-color: #333; }
    .calendar-day-first { border-left: 1px solid #444; }
    .calendar-week-first .calendar-day-button { border-top: 1px solid #444; }
    .other-month .day-number { color: #666; }
    .day-number { font-weight: bold; font-size: 0.9em; margin-bottom: 8px; padding: 4px 8px; border-radius: 50%; line-height: 1; text-align: center; min-width: 28px; }
    .today .day-number { background-color: #1a73e8; color: white; }
    .event-card { padding: 2px 5px; border-radius: 4px; margin-bottom: 4px; width: 100%; font-size: 0.85em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: left; }
</style>
""", unsafe_allow_html=True)

# --- Inicialização do Estado da Sessão ---
if 'events' not in st.session_state:
    st.session_state.events = load_data('events')
if 'content_types' not in st.session_state:
    st.session_state.content_types = [ct['name'] for ct in load_data('content_types')]
if 'current_view_date' not in st.session_state:
    st.session_state.current_view_date = datetime.date.today().replace(day=1)
if 'editing_type' not in st.session_state:
    st.session_state.editing_type = None

# --- Funções de Callback ---
def get_color_for_type(content_type):
    hash_val = hash(content_type)
    r, g, b = (hash_val & 0xFF0000) >> 16, (hash_val & 0x00FF00) >> 8, hash_val & 0x0000FF
    return f"#{r:02x}{g:02x}{b:02x}"

def change_month(delta):
    st.session_state.current_view_date += relativedelta(months=delta)

def go_to_today():
    st.session_state.current_view_date = datetime.date.today().replace(day=1)

def set_editing_state(type_name):
    st.session_state.editing_type = type_name

def clear_editing_state():
    st.session_state.editing_type = None

def handle_data_refresh():
    st.session_state.events = load_data('events')
    st.session_state.content_types = [ct['name'] for ct in load_data('content_types')]
    clear_editing_state()
    st.rerun() # CORRIGIDO: de st.experimental_rerun() para st.rerun()

# --- Barra Lateral (Sidebar) ---
logo_url = "https://www.agrolink.com.br/images/logos/agrolink-logo-v2.png"
st.sidebar.image(logo_url, use_container_width=True)
st.sidebar.title("Agendador")

with st.sidebar.form("new_event_form", clear_on_submit=True):
    st.subheader("Agendar Conteúdo")
    event_title = st.text_input("Título do Conteúdo:")
    event_date = st.date_input("Data:", value=datetime.date.today())
    event_type = st.selectbox("Formato do Conteúdo:", options=st.session_state.content_types)
    
    # Opção de repetição
    is_recurring = st.checkbox("Repetir diariamente")
    end_date = None
    if is_recurring:
        end_date = st.date_input("Repetir até:", value=event_date + datetime.timedelta(days=7))

    submitted = st.form_submit_button("Salvar Agendamento", use_container_width=True)

    if submitted and event_title:
        if is_recurring and end_date:
            current_date = event_date
            while current_date <= end_date:
                save_event(event_title, current_date, event_type)
                current_date += datetime.timedelta(days=1)
            st.sidebar.success("Eventos recorrentes salvos!")
        else:
            save_event(event_title, event_date, event_type)
            st.sidebar.success("Conteúdo agendado e salvo!")
        
        handle_data_refresh()

with st.sidebar.expander("Gerenciar Formatos de Conteúdo", expanded=True):
    for c_type in st.session_state.content_types:
        if st.session_state.editing_type == c_type:
            with st.form(f"edit_form_{c_type}", clear_on_submit=True):
                new_name = st.text_input("Novo nome:", value=c_type)
                c1, c2 = st.columns(2)
                if c1.form_submit_button("Salvar", use_container_width=True):
                    update_content_type(c_type, new_name)
                    handle_data_refresh()
                if c2.form_submit_button("Cancelar", use_container_width=True):
                    clear_editing_state()
        else:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"<span style='color:{get_color_for_type(c_type)};'>●</span> {c_type}", unsafe_allow_html=True)
            c2.button("✏️", key=f"edit_{c_type}", on_click=set_editing_state, args=(c_type,), use_container_width=True)
            if c3.button("🗑️", key=f"del_{c_type}", use_container_width=True):
                delete_content_type(c_type)
                handle_data_refresh()

    with st.form("new_type_form", clear_on_submit=True):
        new_type_name = st.text_input("Adicionar Novo Formato:")
        if st.form_submit_button("Adicionar", use_container_width=True):
            if new_type_name:
                save_content_type(new_type_name)
                handle_data_refresh()

# --- Calendário Principal ---
month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
view_date = st.session_state.current_view_date

header_cols = st.columns([2, 1, 0.5, 0.5, 5])
with header_cols[0]: st.title("Agenda")
with header_cols[1]: st.button("Hoje", on_click=go_to_today, use_container_width=True)
with header_cols[2]: st.button("<", on_click=change_month, args=(-1,), use_container_width=True, key="prev_month")
with header_cols[3]: st.button(">", on_click=change_month, args=(1,), use_container_width=True, key="next_month")
with header_cols[4]: st.subheader(f"{month_names_pt[view_date.month]} de {view_date.year}")

week_headers = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
cols = st.columns(7)
for col, header in zip(cols, week_headers):
    col.markdown(f"<div style='text-align: center; font-weight: bold; color: #aaa; margin: 10px 0;'>{header}</div>", unsafe_allow_html=True)

today = datetime.date.today()
first_day_of_month = view_date.replace(day=1)
start_date = first_day_of_month - datetime.timedelta(days=(first_day_of_month.weekday() + 1) % 7)

# Dialog para detalhes do dia
@st.dialog("Detalhes do Dia")
def view_day_details(date):
    st.subheader(f"Agendamentos para {date.strftime('%d/%m/%Y')}")
    events_for_day = [e for e in st.session_state.events if e["date"] == date]
    if not events_for_day:
        st.write("Nenhum conteúdo agendado para este dia.")
    for event in events_for_day:
        c1, c2 = st.columns([4, 1])
        event_color = get_color_for_type(event['type'])
        c1.markdown(f"""
            <div class="event-card" style="background-color: {event_color}40; border-left: 3px solid {event_color};">
                <small style="color: {event_color}; font-weight: bold;">{event['type']}</small><br>
                {event['title']}
            </div>
        """, unsafe_allow_html=True)
        if c2.button("Excluir", key=f"del_event_{event['id']}", use_container_width=True):
            delete_event(event['id'])
            st.session_state.events = load_data('events')
            st.rerun()

# Grade do Calendário
for week_num in range(6):
    is_first_week_class = "calendar-week-first" if week_num == 0 else ""
    st.markdown(f"<div class='{is_first_week_class}'>", unsafe_allow_html=True)
    cols = st.columns(7)
    for day_num in range(7):
        current_date = start_date + datetime.timedelta(days=(week_num * 7 + day_num))
        with cols[day_num]:
            day_class = "calendar-day-button" + (" calendar-day-first" if day_num == 0 else "")
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
            
            if st.button(label=str(current_date.day), key=f"day_{current_date}", use_container_width=True):
                 view_day_details(current_date)
            # Hack para preencher o botão com o conteúdo
            st.markdown(f"""
            <script>
                const btn = window.parent.document.querySelector('button[data-testid="st.button(label=\'{current_date.day}\', key=\'day_{current_date}\')"]');
                if (btn) {{
                    btn.classList.add('{day_class.replace("calendar-day-button", "")}');
                    btn.innerHTML = `{day_number_html.replace('`', '\\`')}`;
                }}
            </script>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

import sqlite3
import os
import json
import xml.etree.ElementTree as ET
import re
import argparse
import glob
from datetime import datetime
import getpass
import locale
import sys
import ctypes

# Script Logos -> Markdown (Versão Final Otimizada)
# Foco exclusivo em Notas e Sermões Pessoais
# Autor: Gemini CLI

# --- Internationalization ---
TRANSLATIONS = {
    'en': {
        'folder_notes': 'Notes',
        'folder_sermons': 'Sermons',
        'folder_vault': 'Logos_Vault',
        'label_illustration': 'Illustration',
        'label_references': 'References',
        'no_title': 'No_Title',
        'no_notebook': 'No Notebook',
        'default_note_name': 'Note',
        'default_sermon_name': 'Sermon',
        'msg_exporting_notes': 'Exporting {count} Notes...',
        'msg_exporting_sermons': 'Exporting {count} Sermons...',
        'err_logos_path_not_found': 'Error: Logos path not found: "{path}"',
        'err_logos_path_usage': 'Use --logos-path to specify the path manually.',
        'err_dbs_not_found': 'Error: No Logos databases found in: {path}',
        'err_dbs_hint': "Check if the path points to the 'Logos' folder inside AppData/Local.",
        'msg_success': "\nSuccess! Your Notes and Sermons are in: '{path}'",
        'arg_desc': 'Logos Notes and Sermons to Markdown Exporter.',
        'arg_logos_path': 'Logos folder path (AppData/Local/Logos)',
        'arg_output': 'Destination folder for Markdown files',
        'source_notes': 'Logos Notes',
        'source_sermons': 'Logos Sermon Builder',
    },
    'pt_br': {
        'folder_notes': 'Notas',
        'folder_sermons': 'Sermoes',
        'folder_vault': 'Logos_Vault',
        'label_illustration': 'Ilustração',
        'label_references': 'Referências',
        'no_title': 'Sem_Titulo',
        'no_notebook': 'Sem Caderno',
        'default_note_name': 'Nota',
        'default_sermon_name': 'Sermao',
        'msg_exporting_notes': 'Exportando {count} Notas...',
        'msg_exporting_sermons': 'Exportando {count} Sermões...',
        'err_logos_path_not_found': "Erro: O caminho do Logos não foi encontrado: '{path}'",
        'err_logos_path_usage': 'Use --logos-path para especificar o caminho manualmente.',
        'err_dbs_not_found': 'Erro: Não foram encontrados bancos de dados do Logos em: {path}',
        'err_dbs_hint': "Verifique se o caminho aponta para a pasta 'Logos' dentro de AppData/Local.",
        'msg_success': "\nSucesso! Suas Notas e Sermões estão em: '{path}'",
        'arg_desc': 'Exportador de Notas e Sermões do Logos para Markdown.',
        'arg_logos_path': 'Caminho da pasta do Logos (AppData/Local/Logos)',
        'arg_output': 'Pasta de destino para os arquivos Markdown',
        'source_notes': 'Logos Notas',
        'source_sermons': 'Logos Sermon Builder',
    }
}

def get_language():
    """Detecta se o ambiente é pt-br ou en de forma robusta (Windows/Linux)."""
    # 1. Windows: Pega o idioma da interface do usuário
    if sys.platform == 'win32':
        try:
            windll = ctypes.windll.kernel32
            lang_id = windll.GetUserDefaultUILanguage()
            lang_code = locale.windows_locale.get(lang_id, "")
            if 'pt_BR' in lang_code or 'pt_PT' in lang_code or 'Portuguese' in lang_code:
                return 'pt_br'
        except: pass

    # 2. Linux/macOS/Geral: Variáveis de ambiente
    for env in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        val = os.environ.get(env)
        if val and ('pt_BR' in val or 'pt-BR' in val or 'Portuguese' in val):
            return 'pt_br'
            
    # 3. Fallback: locale module
    try:
        lang, _ = locale.getlocale()
        if lang and ('pt_BR' in lang or 'Portuguese' in lang):
            return 'pt_br'
    except: pass
            
    return 'en'

# Inicializa as traduções
lang_code = get_language()
t = TRANSLATIONS[lang_code]

# --- Core Functions ---

def parse_logos_data(data, kind=None, indent=0):
    """Extrai texto de um dado que pode ser XML ou Texto Puro"""
    if not data: return ""
    
    if isinstance(data, bytes):
        start_idx = data.find(b'<')
        if start_idx != -1:
            try:
                xml_part = data[start_idx:].decode('utf-8', errors='ignore')
                return parse_logos_xml(xml_part, kind, indent)
            except: pass
        try:
            text = data.decode('utf-8', errors='ignore')
            return re.sub(r'[\x00-\x1f]', '', text)
        except: return ""

    return parse_logos_xml(str(data), kind, indent)

def parse_logos_xml(xml_content, kind=None, indent=0):
    if not xml_content: return ""
    xml_content = xml_content.replace('\x00', '').strip()
    
    if not xml_content.startswith('<') and '<Run' not in xml_content:
        return re.sub(r'[\x00-\x1f]', '', xml_content)

    try:
        clean_xml = xml_content.replace("&quot;", "\"").replace("&nbsp;", " ").replace("&amp;", "&")
        if not clean_xml.endswith('>'):
            last_gt = clean_xml.rfind('>')
            if last_gt != -1:
                clean_xml = clean_xml[:last_gt+1]
            
        root = ET.fromstring(f"<root>{clean_xml}</root>")
        md_blocks = []
        
        paragraphs = root.findall(".//Paragraph")
        if paragraphs:
            for para in paragraphs:
                style = para.get("Style", "")
                para_text = []
                for run in para.findall(".//Run"):
                    text = run.get("Text", "")
                    if not text: continue
                    
                    bold = (run.get("Bold") or "").lower() == "true" or (run.get("FontBold") or "").lower() == "true"
                    italic = (run.get("Italic") or "").lower() == "true" or (run.get("FontItalic") or "").lower() == "true"
                    underline = (run.get("Underline") or "").lower() == "true" or (run.get("FontUnderline") or "").lower() == "true"
                    strikethrough = (run.get("Strikethrough") or "").lower() == "true" or (run.get("FontStrikethrough") or "").lower() == "true"

                    if bold: text = f"**{text}**"
                    if italic: text = f"*{text}*"
                    if underline: text = f"<u>{text}</u>"
                    if strikethrough: text = f"~~{text}~~"
                    
                    href = run.get("Hyperlink")
                    if href: text = f"[{text}]({href})"
                    para_text.append(text)
                
                content = "".join(para_text).strip()
                if not content: continue
                
                prefix = ""
                if "Heading 1" in style: prefix = "# "
                elif "Heading 2" in style: prefix = "## "
                elif "Heading 3" in style: prefix = "### "
                elif "Blockquote" in style: prefix = "> "
                
                list_level = para.get("ListLevel")
                if list_level:
                    try: prefix = ("  " * (int(list_level) - 1)) + "- "
                    except: prefix = "- "
                
                md_blocks.append(prefix + content)
        else:
            current_text = []
            for run in root.findall(".//Run"):
                text = run.get("Text", "")
                if not text: continue
                
                bold = (run.get("Bold") or "").lower() == "true" or (run.get("FontBold") or "").lower() == "true"
                italic = (run.get("Italic") or "").lower() == "true" or (run.get("FontItalic") or "").lower() == "true"
                
                if bold: text = f"**{text}**"
                if italic: text = f"*{text}*"
                
                href = run.get("Hyperlink")
                if href: text = f"[{text}]({href})"
                current_text.append(text)
                
            content = "".join(current_text).strip()
            if content:
                prefix = ""
                if kind:
                    if "heading1" in kind: prefix = "# "
                    elif "heading2" in kind: prefix = "## "
                    elif "heading3" in kind: prefix = "### "
                    elif "blockquote" in kind: prefix = "> "
                    elif "number" in kind: prefix = "1. "
                    elif "illustration" in kind: prefix = f"*{t['label_illustration']}:* "
                
                if indent > 0:
                    prefix = ("  " * indent) + (prefix or "- ")
                
                md_blocks.append(prefix + content)
            
        return "\n\n".join(md_blocks)
    except Exception:
        text = re.sub(r'<[^>]+>', '', xml_content)
        return re.sub(r'[\x00-\x1f]', '', text)

def sanitize_filename(name):
    if not name: return t['no_title']
    name = str(name).replace('\x00', '')
    name = re.sub(r'[\x00-\x1f]', '', name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return name[:120]

def find_databases(logos_base_path):
    dbs = {'notes': None, 'sermons': None}
    doc_path = os.path.join(logos_base_path, "Documents", "*")
    
    # Notas
    m = glob.glob(os.path.join(doc_path, "NotesToolManager", "notestool.db"))
    if m: dbs['notes'] = m[0]
    
    # Sermões
    m = glob.glob(os.path.join(doc_path, "Documents", "Sermon", "Sermon.db"))
    if m: dbs['sermons'] = m[0]
    
    return dbs

def export_notes(db_path, base_output):
    output_dir = os.path.join(base_output, t['folder_notes'])
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, nb.Title as NotebookTitle
        FROM Notes n
        LEFT JOIN Notebooks nb ON n.NotebookExternalId = nb.ExternalId
        WHERE n.IsDeleted = 0 AND n.IsTrashed = 0
    """)
    notes = cursor.fetchall()
    print(t['msg_exporting_notes'].format(count=len(notes)))
    for note in notes:
        nb_name = sanitize_filename(note['NotebookTitle'] or t['no_notebook'])
        folder = os.path.join(output_dir, nb_name)
        if not os.path.exists(folder): os.makedirs(folder)
        
        anchors_text = ""
        title = parse_logos_data(note['ClippingTitleRichText']).strip()
        if note['AnchorsJson']:
            try:
                anchors = json.loads(note['AnchorsJson'])
                refs = [a['reference']['raw'].split('+')[-1].replace('.', ' ') for a in anchors if 'reference' in a]
                if refs:
                    anchors_text = f"\n\n**{t['label_references']}:** " + ", ".join(refs)
                if not title and refs:
                    title = refs[0]
            except: pass
            
        if not title: title = f"{t['default_note_name']}_{note['NoteId']}"
        
        filename = f"{sanitize_filename(title)}_{note['NoteId']}.md"
        content = parse_logos_data(note['ContentRichText'])
        
        md = f"---\ntitle: \"{title}\"\ncreated: {note['CreatedDate']}\nsource: {t['source_notes']}\n---\n\n{content}{anchors_text}"
        with open(os.path.join(folder, filename), "w", encoding="utf-8") as f: f.write(md)
    conn.close()

def export_sermons(db_path, base_output):
    output_dir = os.path.join(base_output, t['folder_sermons'])
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Documents WHERE IsDeleted = 0")
        sermons = cursor.fetchall()
    except: return
    
    print(t['msg_exporting_sermons'].format(count=len(sermons)))
    for sermon in sermons:
        s_id = sermon['Id']
        title = sermon['Title'] or f"{t['default_sermon_name']}_{s_id}"
        cursor.execute("SELECT Content, Kind, Indent FROM Blocks WHERE DocumentId = ? AND IsDeleted = 0 ORDER BY Rank", (s_id,))
        blocks = cursor.fetchall()
        
        full_text = []
        for b in blocks:
            if b['Content']:
                t_content = parse_logos_data(b['Content'], kind=b['Kind'], indent=b['Indent'])
                if t_content: full_text.append(t_content)
        
        filename = f"{sanitize_filename(title)}.md"
        md = f"---\ntitle: \"{title}\"\ndate: {sermon['Date'] or sermon['ModifiedDate']}\nsource: {t['source_sermons']}\n---\n\n" + "\n\n".join(full_text)
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f: f.write(md)
    conn.close()

def get_default_logos_path():
    """Tenta detectar o caminho padrão do Logos baseado no SO."""
    if os.name == 'nt':  # Windows
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return os.path.join(local_app_data, "Logos")
    else:  # Linux/Unix (Assume-se oudedetai ou caminho customizado)
        home = os.path.expanduser("~")
        user = getpass.getuser()
        possible_paths = [
            os.path.join(home, ".local/share/FaithLife-Community/oudedetai/data/wine64_bottle/drive_c/users", user, "AppData/Local/Logos"),
            os.path.join(home, ".local/share/LogosBibleSoftware/Data/wine64_bottle/drive_c/users", user, "AppData/Local/Logos")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=t['arg_desc'])
    
    default_logos = get_default_logos_path()
    
    parser.add_argument('--logos-path', '-l', default=default_logos, help=t['arg_logos_path'])
    parser.add_argument('--output', '-o', default=t['folder_vault'], help=t['arg_output'])

    args = parser.parse_args()
    
    if not args.logos_path or not os.path.exists(args.logos_path):
        print(t['err_logos_path_not_found'].format(path=args.logos_path))
        print(t['err_logos_path_usage'])
        exit(1)

    dbs = find_databases(args.logos_path)

    if not dbs['notes'] and not dbs['sermons']:
        print(t['err_dbs_not_found'].format(path=args.logos_path))
        print(t['err_dbs_hint'])
        exit(1)

    if dbs['notes']: export_notes(dbs['notes'], args.output)
    if dbs['sermons']: export_sermons(dbs['sermons'], args.output)
    
    print(t['msg_success'].format(path=args.output))

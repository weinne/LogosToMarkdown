import sqlite3
import os
import json
import xml.etree.ElementTree as ET
import re
import argparse
import glob
from datetime import datetime

# Script Logos -> Obsidian (Versão Final Otimizada)
# Foco exclusivo em Notas e Sermões Pessoais
# Autor: Gemini CLI

def parse_logos_data(data):
    """Extrai texto de um dado que pode ser XML ou Texto Puro"""
    if not data: return ""
    
    if isinstance(data, bytes):
        # Tenta encontrar o início de uma tag XML
        start_idx = data.find(b'<')
        if start_idx != -1:
            try:
                xml_part = data[start_idx:].decode('utf-8', errors='ignore')
                return parse_logos_xml(xml_part)
            except: pass
        
        # Fallback: decodificação limpa
        try:
            text = data.decode('utf-8', errors='ignore')
            return re.sub(r'[\x00-\x1f]', '', text)
        except:
            return ""

    return parse_logos_xml(str(data))

def parse_logos_xml(xml_content):
    if not xml_content: return ""
    xml_content = xml_content.replace('\x00', '').strip()
    
    if not xml_content.startswith('<'):
        return re.sub(r'[\x00-\x1f]', '', xml_content)

    try:
        clean_xml = xml_content.replace("&quot;", "\"").replace("&nbsp;", " ").replace("&amp;", "&")
        if not clean_xml.endswith('>'):
            clean_xml = clean_xml[:clean_xml.rfind('>')+1]
            
        root = ET.fromstring(f"<root>{clean_xml}</root>")
        md_text = []
        
        # Captura tags Run de forma recursiva (suporta Bold e Italic)
        for run in root.findall(".//Run"):
            text = run.get("Text", "")
            if not text: continue
            if run.get("Bold") == "true" or run.get("FontBold") == "true": 
                text = f"**{text}**"
            if run.get("Italic") == "true" or run.get("FontItalic") == "true": 
                text = f"*{text}*"
            md_text.append(text)
            
        return "".join(md_text)
    except Exception:
        text = re.sub(r'<[^>]+>', '', xml_content)
        return re.sub(r'[\x00-\x1f]', '', text)

def sanitize_filename(name):
    if not name: return "Sem_Titulo"
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
    output_dir = os.path.join(base_output, "Notas")
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
    print(f"Exportando {len(notes)} Notas...")
    for note in notes:
        nb_name = sanitize_filename(note['NotebookTitle'] or "Sem Caderno")
        folder = os.path.join(output_dir, nb_name)
        if not os.path.exists(folder): os.makedirs(folder)
        
        title = parse_logos_data(note['ClippingTitleRichText']).strip()
        if not title and note['AnchorsJson']:
            try:
                anchors = json.loads(note['AnchorsJson'])
                title = anchors[0]['reference']['raw'].split('+')[-1].replace('.', ' ')
            except: pass
        if not title: title = f"Nota_{note['NoteId']}"
        
        filename = f"{sanitize_filename(title)}_{note['NoteId']}.md"
        content = parse_logos_data(note['ContentRichText'])
        
        md = f"---\ntitle: \"{title}\"\ncreated: {note['CreatedDate']}\nsource: Logos Notes\n---\n\n{content}"
        with open(os.path.join(folder, filename), "w", encoding="utf-8") as f: f.write(md)
    conn.close()

def export_sermons(db_path, base_output):
    output_dir = os.path.join(base_output, "Sermoes")
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Documents WHERE IsDeleted = 0")
        sermons = cursor.fetchall()
    except: return
    
    print(f"Exportando {len(sermons)} Sermões...")
    for sermon in sermons:
        s_id = sermon['Id']
        title = sermon['Title'] or f"Sermao_{s_id}"
        cursor.execute("SELECT Content FROM Blocks WHERE DocumentId = ? AND IsDeleted = 0 ORDER BY Rank", (s_id,))
        blocks = cursor.fetchall()
        
        full_text = []
        for b in blocks:
            if b['Content']:
                t = parse_logos_data(b['Content'])
                if t: full_text.append(t)
        
        filename = f"{sanitize_filename(title)}.md"
        md = f"---\ntitle: \"{title}\"\ndate: {sermon['Date'] or sermon['ModifiedDate']}\nsource: Logos Sermon Builder\n---\n\n" + "\n\n".join(full_text)
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f: f.write(md)
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Exportador de Notas e Sermões do Logos para Obsidian.')
    default_logos = "/home/weinne/.local/share/FaithLife-Community/oudedetai/data/wine64_bottle/drive_c/users/weinne/AppData/Local/Logos"
    parser.add_argument('--logos-path', '-l', default=default_logos, help='Caminho da pasta do Logos')
    parser.add_argument('--output', '-o', default='Logos_Vault', help='Pasta de destino')

    args = parser.parse_args()
    dbs = find_databases(args.logos_path)

    if dbs['notes']: export_notes(dbs['notes'], args.output)
    if dbs['sermons']: export_sermons(dbs['sermons'], args.output)
    
    print(f"\nSucesso! Suas Notas e Sermões estão em: '{args.output}'")

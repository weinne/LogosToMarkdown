# Logos to Obsidian Export

Este script automatiza a exportação de Notas e Sermões do **Logos Bible Software** para arquivos Markdown compatíveis com o **Obsidian**.

## Funcionalidades
- **Notas:** Exporta suas notas organizadas por cadernos (Notebooks).
- **Sermões:** Exporta seus sermões do Sermon Builder.
- **Formatação:** Preserva negrito e itálico básicos e metadados (YAML frontmatter).

## Pré-requisitos

Para rodar este script, você precisará ter o **Python 3** instalado em seu computador.

### Como instalar o Python

#### No Windows:
1. Acesse [python.org](https://www.python.org/downloads/).
2. Clique no botão de download para a versão mais recente.
3. **Importante:** Durante a instalação, marque a caixa **"Add Python to PATH"**.
4. Siga as instruções até o final.

#### No Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3
```

## Como Usar

1. Baixe o arquivo `logos_to_markdown.py`.
2. Abra o terminal ou prompt de comando na pasta onde o arquivo está.
3. Execute o script:

```bash
python3 logos_to_markdown.py --output Logos_Vault
```

### Onde está o diretório do Logos?

O script tenta detectar automaticamente o caminho do Logos, mas se ele não encontrar, você precisará informá-lo usando o parâmetro `--logos-path`.

#### No Windows:
Geralmente fica em:
`C:\Users\SEU_USUARIO\AppData\Local\Logos`

Para usar no comando:
```bash
python3 logos_to_markdown.py --logos-path "C:\Users\NomeDoUsuario\AppData\Local\Logos" --output MinhasNotas
```

#### No Linux:
Se você usa o script `oudedetai` da FaithLife-Community, o caminho costuma ser algo como:
`~/.local/share/FaithLife-Community/oudedetai/data/wine64_bottle/drive_c/users/SEU_USUARIO/AppData/Local/Logos`

Exemplo de uso:
```bash
python3 logos_to_markdown.py --logos-path "/caminho/para/o/logos" --output Logos_Vault
```

## Parâmetros Disponíveis

- `--logos-path` ou `-l`: Caminho manual para a pasta do Logos.
- `--output` ou `-o`: Nome da pasta onde os arquivos `.md` serão criados (Padrão: `Logos_Vault`).

## Aviso Importante
Este script acessa os bancos de dados SQLite locais do Logos em modo leitura. Certifique-se de que o Logos esteja fechado ao rodar o script para evitar conflitos de acesso aos arquivos.

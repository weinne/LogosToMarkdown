# Logos To Markdown

Exportador de Notas e Sermões do Logos Bible Software para arquivos Markdown.

## Novas Funcionalidades

- **Cópia Temporária**: O script agora cria uma cópia dos bancos de dados antes de processá-los, permitindo a execução mesmo com o Logos aberto.
- **Arquivo de Configuração**: Suporte a `.logostomarkdown.conf` para salvar seus caminhos preferidos. O arquivo é criado automaticamente na primeira execução.
- **Sincronização Inteligente**: Só atualiza arquivos que realmente foram alterados no Logos, preservando metadados do sistema de arquivos.
- **Formatação Aprimorada**: Correções na conversão de negrito, itálico e outros estilos para garantir um Markdown limpo.

## Como usar

1.  Certifique-se de ter o Python instalado.
2.  Execute o script:
    ```bash
    python logos_to_markdown.py
    ```
3.  Na primeira execução, um arquivo `.logostomarkdown.conf` será criado na pasta atual. Você pode editá-lo para fixar o caminho do seu Logos ou a pasta de destino.

## Arquivo de Configuração

O arquivo busca configurações nos seguintes locais:
1.  Pasta atual
2.  Pasta do script
3.  `~/.config/logostomarkdown/` (Linux)
4.  `%APPDATA%\logostomarkdown\` (Windows)

Exemplo de conteúdo:
```json
{
    "logos_path": "C:\\Users\\Usuario\\AppData\\Local\\Logos",
    "output": "D:\\Notas\\Logos_Vault"
}
```

## Requisitos

- Python 3.x
- Bibliotecas padrão (`sqlite3`, `xml`, etc.)

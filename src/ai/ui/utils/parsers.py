import re

def parse_markdown(text):
    """Parse Markdown text and return a list of tuples (text, tag).
    # Heading 1

    ## Heading 2

    ### Heading 3

    Here is some `inline code`. This is a **bold** text and this is an *italic words* text. 

    ```
    test = 'Amit'
    print(f"{test}")
    ```

    | Column 1 | Column 2 |
    |----------|----------|
    | Row 1    | Data 1   |
    | Row 2    | Data 2   |

    This line contains an emoji 😀.

    """
    parsed_text = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            parsed_text.append(("\n", "newline"))
        elif is_heading(line):
            parsed_text.append(parse_heading(line))
        elif line.startswith('```'):
            code_text, i = parse_multiline_code(lines, i)
            parsed_text.append((f"\n", "x"))
            parsed_text.append((f"{code_text}\n", "code"))
            parsed_text.append((f"\n", "x"))
            continue
        elif '|' in line:
            table_text, i = parse_table(lines, i)
            parsed_text.append((f"\n", "x"))
            parsed_text.append((f"{table_text}", "table"))
            parsed_text.append((f"\n", "x"))
            continue
        elif '`' in line:
            parsed_text.extend(parse_inline_code(line))
        elif '**' in line:
            parsed_text.extend(parse_bold(line))
        elif '*' in line:
            parsed_text.extend(parse_italic(line))
        elif contains_emoji(line):
            parsed_text.extend(parse_emoji(line))
        else:
            parsed_text.append((line, None))
        i += 1
    return parsed_text

def is_heading(line):
    return line.startswith('# ') or line.startswith('## ') or line.startswith('### ')

def parse_heading(line):
    if line.startswith('# '):
        return (f"\n{line[2:]}\n", "heading1")
    elif line.startswith('## '):
        return (f"\n{line[3:]}\n", "heading2")
    elif line.startswith('### '):
        return (f"\n{line[4:]}\n", "heading3")

def parse_bold(line):
    parts = line.split('**')
    parsedParts = []
    for j, part in enumerate(parts):
        if j % 2 == 1:
            parsedParts.append((part, "bold"))
        else:
            for italic in parse_italic(part):
                parsedParts.append(italic)
    return parsedParts

def parse_italic(line):
    parts = re.split(r'(\*[^*\s][^*]*[^*\s]\*)', line)  # Ensures proper *word* structure
    parsed = []
    
    for part in parts:
        if re.fullmatch(r'\*[^*\s].*[^*\s]\*', part):  # Matches *italic*
            parsed.append((part[1:-1], "italic"))
        else:
            parsed.append((part, None))
    return parsed

def parse_inline_code(line):
    parts = line.split('`')
    parsedParts = []
    for j, part in enumerate(parts):
        if j % 2 == 1:
            parsedParts.append((part, "code-inline"))
        else:
            for bold in parse_bold(part):
                parsedParts.append(bold)
    return parsedParts

def parse_multiline_code(lines, i):
    code_lines = []
    i += 1
    while i < len(lines) and not lines[i].startswith('```'):
        code_lines.append(lines[i])
        i += 1
    # Increment i to skip the closing ```
    i += 1
    print(code_lines)
    return '\n'.join(code_lines), i

def parse_table(lines, i):
    table_lines = []
    while i < len(lines) and '|' in lines[i]:
        table_lines.append(lines[i])
        i += 1
    
    # Split the table into rows and columns
    table_rows = [line.split('|') for line in table_lines]
    
    # Determine the maximum width for each column
    col_widths = [max(len(cell.strip()) for cell in col) for col in zip(*table_rows)]
    
    # Format the table with equal width columns
    formatted_table = []
    for row in table_rows:
        formatted_row = '|'.join(cell.strip().ljust(width) for cell, width in zip(row, col_widths))
        formatted_table.append(formatted_row)
    
    table_text = '\n'.join(formatted_table)
    return table_text, i

def contains_emoji(line):
    return any(char in line for char in "😀😃😄😁😆😅😂🤣")

def parse_emoji(line):
    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F]')
    emojis = emoji_pattern.findall(line)
    return [(emoji, "emoji") for emoji in emojis]

import re
from dataclasses import dataclass
from enum import Enum
from typing import List

class InstructionType(Enum):
    TEXT = "text"
    BOLD_START = "bold_start"
    BOLD_END = "bold_end"
    ITALIC_START = "italic_start"
    ITALIC_END = "italic_end"
    HEADING_START = "heading_start"
    HEADING_END = "heading_end"
    NEWLINE = "newline"

@dataclass
class TypingInstruction:
    type: InstructionType
    content: str = ""
    heading_level: int = 0

class MarkdownParser:
    def __init__(self):
        self.bold_pattern = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
        self.italic_pattern = re.compile(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)')
        self.heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)

    def parse(self, markdown_text: str) -> List[TypingInstruction]:
        instructions = []
        lines = markdown_text.split('\n')
        
        for i, line in enumerate(lines):
            line_instructions = self._parse_line(line)
            instructions.extend(line_instructions)
            
            if i < len(lines) - 1:
                instructions.append(TypingInstruction(InstructionType.NEWLINE))
        
        return instructions

    def _parse_line(self, line: str) -> List[TypingInstruction]:
        instructions = []
        
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            instructions.append(TypingInstruction(
                InstructionType.HEADING_START,
                heading_level=level
            ))
            instructions.extend(self._parse_inline(content))
            instructions.append(TypingInstruction(
                InstructionType.HEADING_END,
                heading_level=level
            ))
            return instructions
        
        instructions.extend(self._parse_inline(line))
        return instructions

    def _parse_inline(self, text: str) -> List[TypingInstruction]:
        instructions = []
        
        tokens = self._tokenize(text)
        
        for token in tokens:
            if token['type'] == 'bold':
                instructions.append(TypingInstruction(InstructionType.BOLD_START))
                instructions.extend(self._parse_inline(token['content']))
                instructions.append(TypingInstruction(InstructionType.BOLD_END))
            elif token['type'] == 'italic':
                instructions.append(TypingInstruction(InstructionType.ITALIC_START))
                instructions.extend(self._parse_inline(token['content']))
                instructions.append(TypingInstruction(InstructionType.ITALIC_END))
            else:
                if token['content']:
                    instructions.append(TypingInstruction(
                        InstructionType.TEXT,
                        content=token['content']
                    ))
        
        return instructions

    def _tokenize(self, text: str) -> List[dict]:
        tokens = []
        current_pos = 0
        
        combined_pattern = re.compile(
            r'(\*\*(.+?)\*\*|__(.+?)__)|'
            r'((?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_))'
        )
        
        for match in combined_pattern.finditer(text):
            if match.start() > current_pos:
                tokens.append({
                    'type': 'text',
                    'content': text[current_pos:match.start()]
                })
            
            if match.group(1):
                content = match.group(2) or match.group(3)
                tokens.append({'type': 'bold', 'content': content})
            elif match.group(4):
                content = match.group(5) or match.group(6)
                tokens.append({'type': 'italic', 'content': content})
            
            current_pos = match.end()
        
        if current_pos < len(text):
            tokens.append({'type': 'text', 'content': text[current_pos:]})
        
        return tokens

    def get_plain_text_length(self, markdown_text: str) -> int:
        instructions = self.parse(markdown_text)
        length = 0
        for inst in instructions:
            if inst.type == InstructionType.TEXT:
                length += len(inst.content)
            elif inst.type == InstructionType.NEWLINE:
                length += 1
        return length


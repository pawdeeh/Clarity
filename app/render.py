# app/render.py
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from xml.etree import ElementTree as etree
import re


# ====== CUSTOM MARKDOWN EXTENSIONS ======

class RemarkExtension(Extension):
    """Extension for rendering remarks (note, info, warning, tip)"""
    
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(RemarkProcessor(md.parser), 'remark', 105)


class RemarkProcessor(BlockProcessor):
    RE = re.compile(r'^!!\s*\[\s*(note|info|warning|tip)\s*\]\s*\((.+?)\)$', re.IGNORECASE | re.MULTILINE)
    
    def test(self, parent, block):
        return bool(self.RE.match(block.split('\n')[0]))
    
    def run(self, parent, blocks):
        block = blocks.pop(0)
        lines = block.split('\n')
        first_line = lines[0]
        m = self.RE.match(first_line)
        
        if m:
            remark_type = m.group(1).lower()
            title = m.group(2)
            content = '\n'.join(lines[1:])
            
            div = etree.SubElement(parent, 'div')
            div.set('class', f'remark remark-{remark_type}')
            
            header = etree.SubElement(div, 'div')
            header.set('class', 'remark-title')
            header.text = title.capitalize()
            
            body = etree.SubElement(div, 'div')
            body.set('class', 'remark-content')
            body.text = content


class TabsExtension(Extension):
    """Extension for rendering tab groups and tabs"""
    
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(TabGroupProcessor(md.parser), 'tabgroup', 105)


class TabGroupProcessor(BlockProcessor):
    RE = re.compile(r'^~~~tabs\s*$', re.MULTILINE)
    
    def test(self, parent, block):
        return bool(self.RE.search(block))
    
    def run(self, parent, blocks):
        block = blocks.pop(0)
        
        # Parse tab blocks
        tab_pattern = r'tab\s*:\s*"(.+?)"\s*\n(.*?)(?=tab\s*:|~~~tabs|\Z)'
        tabs = re.findall(tab_pattern, block, re.DOTALL)
        
        if tabs:
            tab_group = etree.SubElement(parent, 'div')
            tab_group.set('class', 'tab-group')
            
            # Create tab buttons
            buttons_container = etree.SubElement(tab_group, 'div')
            buttons_container.set('class', 'tab-buttons')
            
            for idx, (label, content) in enumerate(tabs):
                btn = etree.SubElement(buttons_container, 'button')
                btn.set('class', f'tab-button {"active" if idx == 0 else ""}')
                btn.set('data-tab', f'tab-{idx}')
                btn.text = label
            
            # Create tab content
            content_container = etree.SubElement(tab_group, 'div')
            content_container.set('class', 'tab-content')
            
            for idx, (label, content) in enumerate(tabs):
                panel = etree.SubElement(content_container, 'div')
                panel.set('class', f'tab-panel {"active" if idx == 0 else ""}')
                panel.set('data-panel', f'tab-{idx}')
                panel.text = content


class VariableExtension(Extension):
    """Extension for variable substitution (conditionals and variables)"""
    
    def __init__(self, variables: dict = None):
        self.variables = variables or {}
        super().__init__()
    
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            VariablePattern(r'\{\{(\w+)\}\}', md, self.variables),
            'variable',
            190
        )


class VariablePattern(InlineProcessor):
    def __init__(self, pattern, md, variables):
        super().__init__(pattern, md)
        self.variables = variables
    
    def handleMatch(self, m, data):
        var_name = m.group(1)
        el = etree.Element('span')
        el.set('class', 'variable')
        el.text = str(self.variables.get(var_name, f'{{{{{var_name}}}}}'))
        return el, m.start(0), m.end(0)


class IncludeExtension(Extension):
    """Extension for including content from other files"""
    
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(IncludeProcessor(md.parser), 'include', 105)


class IncludeProcessor(BlockProcessor):
    RE = re.compile(r'^!include\s*\(\s*(.+?)\s*\)$', re.MULTILINE)
    
    def test(self, parent, block):
        return bool(self.RE.search(block))
    
    def run(self, parent, blocks):
        block = blocks.pop(0)
        lines = block.split('\n')
        
        for line in lines:
            m = self.RE.match(line)
            if m:
                filepath = m.group(1)
                # In a real implementation, you'd read from the actual file
                # For now, we'll create a placeholder
                div = etree.SubElement(parent, 'div')
                div.set('class', 'include')
                div.set('data-include', filepath)
                div.text = f'[Include: {filepath}]'


class CodeBlockExtension(Extension):
    """Extension for enhanced code blocks with language highlight and line numbers"""
    
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CodeBlockProcessor(md.parser), 'codeblock', 105)


class CodeBlockProcessor(BlockProcessor):
    RE = re.compile(r'^```(\w+)?\n(.*?)^```$', re.MULTILINE | re.DOTALL)
    
    def test(self, parent, block):
        return bool(self.RE.search(block))
    
    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        
        if m:
            language = m.group(1) or 'plaintext'
            code_content = m.group(2).strip()
            
            pre = etree.SubElement(parent, 'pre')
            pre.set('class', f'highlight language-{language}')
            
            code = etree.SubElement(pre, 'code')
            code.set('class', f'language-{language}')
            code.text = code_content


# ====== MAIN RENDERING FUNCTION ======

def render_markdown_to_html(
    markdown_content: str,
    variables: dict = None,
    enable_extras: bool = True
) -> str:
    """
    Convert markdown text to HTML with support for custom extensions.
    
    Args:
        markdown_content: The markdown text to render
        variables: Dictionary of variables for substitution
        enable_extras: Whether to enable all custom extensions
    
    Returns:
        HTML string
    """
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list',
    ]
    
    if enable_extras:
        extensions.extend([
            RemarkExtension(),
            TabsExtension(),
            IncludeExtension(),
            CodeBlockExtension(),
        ])
    
    # Add variable extension with provided variables
    extensions.append(VariableExtension(variables or {}))
    
    return markdown.markdown(markdown_content, extensions=extensions)

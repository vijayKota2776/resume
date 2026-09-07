import os
import tempfile
import subprocess
from typing import Dict, Any
from jinja2 import Environment, DictLoader

# Simple Jinja2 templates for LaTeX
# Note: LaTeX uses { and } heavily, so we configure Jinja2 to use different delimiters.
JINJA_ENV_KWARGS = {
    'block_start_string': '<%',
    'block_end_string': '%>',
    'variable_start_string': '<<',
    'variable_end_string': '>>',
    'comment_start_string': '<#',
    'comment_end_string': '#>',
}

TEMPLATES = {
    "modern": r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{hyperref}

\begin{document}
\begin{center}
    {\Huge \textbf{<< name | default('Your Name') >>}} \\
    \vspace{2mm}
    << contact | default('Email: user@example.com | Phone: (123) 456-7890') >>
\end{center}

\section*{Summary}
<< summary >>

\section*{Experience}
<% for exp in work_experience %>
\noindent\textbf{<< exp.role >>} \hfill << exp.dates | default('') >>\\
\textit{<< exp.company >>}
\begin{itemize}
<% for item in exp.bullet_points %>
    \item << item >>
<% endfor %>
\end{itemize}
<% endfor %>

\section*{Skills}
<< skills | join(', ') >>

\end{document}""",

    "classic": r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{letterpaper, margin=0.8in}
\usepackage{times}

\begin{document}
\begin{center}
    {\LARGE \textsc{<< name | default('Your Name') >>}} \\
    \vspace{2mm}
    << contact | default('Email: user@example.com | Phone: (123) 456-7890') >>
\end{center}
\vspace{4mm}

\begin{minipage}[t]{0.7\textwidth}
\noindent \textbf{SUMMARY}\\
\rule{\linewidth}{0.4pt}\\
<< summary >>
\vspace{4mm}

\noindent \textbf{EXPERIENCE}\\
\rule{\linewidth}{0.4pt}\\
<% for exp in work_experience %>
\noindent\textbf{<< exp.role >>, << exp.company >>} \hfill \textit{<< exp.dates | default('') >>}
\begin{itemize}
<% for item in exp.bullet_points %>
    \item << item >>
<% endfor %>
\end{itemize}
<% endfor %>

\noindent \textbf{EDUCATION}\\
\rule{\linewidth}{0.4pt}\\
<% for edu in education %>
\noindent\textbf{<< edu.degree >>} \hfill \textit{<< edu.year | default('') >>} \\
<< edu.institution >>
\vspace{2mm}
<% endfor %>
\end{minipage}%
\hfill
\begin{minipage}[t]{0.25\textwidth}
\noindent \textbf{SKILLS}\\
\rule{\linewidth}{0.4pt}\\
\begin{itemize}
<% for skill in skills %>
    \item << skill >>
<% endfor %>
\end{itemize}
\end{minipage}

\end{document}"""
}

env = Environment(loader=DictLoader(TEMPLATES), **JINJA_ENV_KWARGS)

def escape_latex(s: str) -> str:
    """Very basic LaTeX escaping. Expand for production use."""
    if not isinstance(s, str):
        return s
    escape_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}'
    }
    return "".join(escape_chars.get(c, c) for c in s)

def recursive_escape(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: recursive_escape(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_escape(v) for v in data]
    elif isinstance(data, str):
        return escape_latex(data)
    return data

def generate_pdf(tailored_json: Dict[str, Any], template_choice: str = "modern") -> bytes:
    if template_choice not in TEMPLATES:
        template_choice = "modern"
        
    template = env.get_template(template_choice)
    escaped_data = recursive_escape(tailored_json)
    tex_content = template.render(**escaped_data)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, 'resume.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(tex_content)
            
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'resume.tex'],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"pdflatex failed: {result.stdout}\n{result.stderr}")
                
            pdf_path = os.path.join(tmpdir, 'resume.pdf')
            with open(pdf_path, 'rb') as f:
                return f.read()
                
        except FileNotFoundError:
            # Fallback to web API
            import requests
            try:
                # Assuming this API accepts raw text in body or a specific form
                # This is a placeholder as requested.
                response = requests.post("https://latexresu.me/api", data=tex_content.encode('utf-8'))
                if response.status_code == 200:
                    return response.content
                else:
                    raise Exception(f"Fallback API failed: {response.status_code} {response.text}")
            except Exception as api_err:
                raise Exception(f"pdflatex is not installed, and fallback API failed. Please install pdflatex or use Docker. Error: {api_err}")

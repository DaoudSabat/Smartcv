import os
import pdfkit
from jinja2 import Environment, FileSystemLoader

class TemplateRenderer:
    def __init__(self, template_name):
        self.template_name = template_name
        self.template_dir = os.path.join(os.getcwd(), "html_templates")
        self.template_file = f"{template_name}.html"

    def render_cv(self, sections: dict, output_file: str = "SmartCV_TemplateFilled.pdf"):
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template_file)

        html_content = template.render(sections)

        html_path = os.path.join(os.getcwd(), "temp.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        exe_path = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=exe_path)
        options = {
            "print-media-type": "",
            "page-size": "A4",
            "encoding": "UTF-8"
        }

        pdfkit.from_file(html_path, output_file, configuration=config, options=options)
        return output_file

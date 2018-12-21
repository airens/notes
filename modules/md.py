import markdown
from os import path


class Md:
    template = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <style>
                    {css}
                </style>
            </head>
            <body>
                {body}
            </body>
        </html>
    """
    extension_configs = {
        'codehilite': {
            'linenums': False,
            'guess_lang': False,
        },
    }

    def __init__(self, *argsv):
        self.css = ""
        for css_file in argsv:
            filename = path.join(path.dirname(__file__), css_file)
            if path.exists(filename):
                with open(filename) as file:
                    self.css += file.read()
            else:
                print(f"File not found: {filename}")

    @staticmethod
    def _clean_up(html):
        # return html
        return html.replace("&amp;lt", "&lt").replace("&amp;gt", "&gt")

    def render_html(self, text):
        body = markdown.markdown(text=text, extensions=["codehilite", "nl2br", "tables", "fenced_code", "sane_lists"],
                                 extension_configs=self.extension_configs)
        html = self._clean_up(self.template.format(css=self.css, body=body))
        # with open("test.html", 'w', encoding="utf-8") as file:
        #     file.write(html)
        return html


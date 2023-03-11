from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _


class SVGFieldPanel(FieldPanel):
    class BoundPanel(FieldPanel.BoundPanel):       

        class msg:
            file_label = _("Read data from file")
            no_script = _("SVG with embedded JavaScript not supported")
            no_viewbox = _("SVG must have a valid viewBox attribute")
            please_enter = _("Please enter a valid SVG element")

        def render_html(self, parent_context = None):
            html = super().render_html(parent_context)
            return mark_safe(html + self.file_to_text_with_preview())

        def file_to_text_with_preview(self):
            return '''
                <label for="svgFile"> 
                    <h4 class="w-panel__heading w-panel__heading--label svg-panel-label">
                        ''' + self.msg.file_label + '''
                    </h4> 
                </label> 
                <input 
                    type="file" 
                    id="''' + self.field_name + '''File" 
                    accept=".svg" 
                    style="border-style: none; padding: 0; display: block; width: fit-content;" 
                />
                <h4 
                    class="w-panel__heading w-panel__heading--label svg-panel-label" 
                    id="''' + self.field_name + '''-svgPreviewLabel"
                >
                    ''' + _("Preview") + '''
                </h4> 
                <div class="svg-preview" id="''' + self.field_name + '''-svgPreview"></div>
                <script> 
                    const svgFile = document.getElementById("''' + self.field_name + '''File"); 
                    const svgField = document.getElementById("''' + self.id_for_label() + '''");
                    const svgPreview = document.getElementById("''' + self.field_name + '''-svgPreview");
                    const msgNoScript = "''' + self.msg.no_script + '''";
                    const msgNoViewBox = "''' + self.msg.no_viewbox + '''";
                    const msgPleaseEnter = "''' + self.msg.please_enter + '''";
                </script>'''    

import re

from bs4 import BeautifulSoup
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.panels import FieldPanel

from .panels import SVGFieldPanel


class SVGIconForm(WagtailAdminModelForm):
    def clean(self) -> None:
        # check valid svg has been entered
        cleaned_data = super().clean()
        code = cleaned_data.get("svg")
        if code:
            # strip any xmlns:svg definition as it corrupts BSoup output.
            code = re.sub(r"xmlns:svg=\"\S+\"", "", code)
            soup = BeautifulSoup(code, "xml")
            svg = soup.find("svg")
            if svg:
                del svg["height"]
                del svg["width"]
                del svg["preserveAspectRatio"]
                # remove this next loop if you wany to allow <script> tags in <svg> icons
                for script in svg.find_all("script"):
                    script.extract()
                if not svg.has_attr("viewBox"):
                    self.add_error(
                        "svg", _("SVG element must include a valid viewBox attribute.")
                    )
                cleaned_data["svg"] = str(svg.prettify())
            else:
                self.add_error(
                    "svg", _("Please enter a valid SVG including the SVG element.")
                )
        return cleaned_data


class SVGIcon(models.Model):
    base_form_class = SVGIconForm

    label = models.CharField(max_length=255, verbose_name=_("label"), unique=True)
    svg = models.TextField(
        verbose_name="SVG",
        help_text=_("Height and width attributes will be stripped on save."),
    )

    panels = [
        FieldPanel("label"),
        SVGFieldPanel("svg"),
    ]

    def __str__(self):
        return self.label

    def icon(self):
        return mark_safe(
            f'<div class="svg-viewset-cell">\
                <div class="svg-viewset-item">\
                    {self.svg}\
                </div>\
            </div>'
        )

    icon.short_description = "Icon"
    
    class Meta:
        verbose_name = _("SVG Icon")

class SVGFilterSet(WagtailFilterSet):
    class Meta:
        model = SVGIcon
        fields = ["label"]

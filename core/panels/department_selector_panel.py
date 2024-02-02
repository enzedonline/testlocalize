from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel

class DepartmentSelectorPanel(FieldPanel):

    class BoundPanel(FieldPanel.BoundPanel):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.form.fields[self.field_name].widget.choices = self.choice_list

        @property
        def choice_list(self):
            # Get the queryset with the group objects
            user_groups = get_user_model().objects.get(id=self.request.user.id).groups.filter(name__endswith='News Admin')
            # Populate the choices using the group PK as the value and the group name as the display text
            return [(None, '--------')] + [(group.pk, str(group)) for group in user_groups]
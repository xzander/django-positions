from __future__ import unicode_literals
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from functools import update_wrapper
from django.conf.urls import url
from django.contrib.admin.utils import unquote, quote
from django.http import HttpResponseRedirect, HttpRequest
from django.utils.html import format_html
from django.db.models import Model
from django.contrib.admin import AdminSite
from django.db.models.fields import Field
from typing import SupportsInt, Text

from .fields import PositionField

class PositionAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        # type: (Model, AdminSite) -> None
        super(PositionAdmin, self).__init__(model, admin_site)
        for field in model._meta.get_fields(): # type: Field
            if isinstance(field, PositionField):
                self.position_field = field
                break

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        meta = self.model._meta
        view_params = meta.app_label, meta.module_name, self.position_field.name
        return [
            url(r'^(.+)/{}-(up)/$'.format(self.position_field.name), wrap(self.position_view), name='{}_{}_{}_up'.format(*view_params)),
            url(r'^(.+)/{}-(down)/$'.format(self.position_field.name), wrap(self.position_view), name='{}_{}_{}_down'.format(*view_params)),
            url(r'^(.+)/{}-(set)/$'.format(self.position_field.name), wrap(self.position_view), name='{}_{}_{}_set'.format(*view_params)),
        ] + super(PositionAdmin, self).get_urls()

    def position_view(self, request, object_id, direction):
        # type: (HttpRequest, SupportsInt, Text) -> HttpResponseRedirect
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        meta = self.model._meta

        position_change_function = getattr(obj, self.position_field.name + '_' + direction)
        position_change_function()

        referer = request.referer
        redirect_url = referer if referer else reverse('admin:{}_{}'.format(meta.app_label, meta.model_name))
        return HttpResponseRedirect(redirect_url)

    def position_up_down_links(self, obj):
        # type: (Model) -> Text
        meta = self.model._meta

        view_params = meta.app_label, meta.module_name, self.position_field.name

        url_up = reverse('admin:{}_{}_{}_up'.format(*view_params), args=(quote(obj.pk),))
        url_down = reverse('admin:{}_{}_{}_down'.format(*view_params), args=(quote(obj.pk),))
        return format_html('<a href="{}"><img src="{}positions/img/arrow-up.gif" alt="Position Up" /></a>'
                           '<a href="{}"><img src="{}positions/img/arrow-down.gif" alt="Position Down" /></a>',
                           url_up, url_down, settings.STATIC_URL, settings.STATIC_URL)

    position_up_down_links.allow_tags = True

    position_up_down_links.short_description = 'Position'
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from functools import update_wrapper
from django.conf.urls import url
from django.contrib.admin.utils import unquote, quote
from django.http import HttpResponseRedirect
from django.utils.html import format_html


class PositionAdmin(admin.ModelAdmin):
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name
        return [
            url(r'^(.+)/position-(up)/$', wrap(self.position_view), name='%s_%s_position_up' % info),
            url(r'^(.+)/position-(down)/$', wrap(self.position_view), name='%s_%s_position_down' % info),
        ] + super(PositionAdmin, self).get_urls()

    def position_view(self, request, object_id, direction):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        if direction == 'up':
            obj.position_up()
        else:
            obj.position_down()
        return HttpResponseRedirect('../../')

    def position_up_down_links(self, obj):
        opts = self.model._meta
        url_up = reverse('admin:%s_%s_position_up' % (opts.app_label, opts.model_name), args=(quote(obj.pk),))
        url_down = reverse('admin:%s_%s_position_down' % (opts.app_label, opts.model_name), args=(quote(obj.pk),))
        return format_html('<a href="{}"><img src="{}positions/img/arrow-up.gif" alt="Position Up" /></a>'
                           '<a href="{}"><img src="{}positions/img/arrow-down.gif" alt="Position Down" /></a>',
                           url_up, url_down, settings.STATIC_URL, settings.STATIC_URL)

    position_up_down_links.allow_tags = True

    position_up_down_links.short_description = 'Position'
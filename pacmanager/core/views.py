from decimal import Decimal
from datetime import datetime
import logging

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, FormView, View
from django.views.generic.detail import SingleObjectMixin
from django.utils import simplejson as json
from django.contrib import messages

from eveapi import EVEAPIConnection, Error
from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from .tasks import import_wallet_journal
from .forms import KeyForm, CorporationContactForm, ManualAdjustmentForm
from .models import Corporation, Key, APICache, Transaction, MonthTotal

class KeyListView(LoginRequiredMixin, ListView):

    model = Key
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.has_perm('core.view_all_keys'):
            return self.model.objects.all()
        else:
            return Key.objects.filter(corporation__contact=self.request.user)


class KeyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

    model = Key
    form_class = KeyForm
    permission_required = 'core.add_key'
    success_url = reverse_lazy('key-list')


class KeyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

    model = Key
    permission_required = 'core.delete_key'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype="application/json")
        messages.success(request, 'Key %s deleted sucessfully' % self.object.pk)
        return HttpResponseRedirect(self.get_success_url())


class KeyRefreshView(LoginRequiredMixin, SingleObjectMixin, View):

    model = Key

    def get(self, request, *args,**kwargs):
        self.object = self.get_object()
        self.object.save()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype="application/json")
        messages.success(request, 'Key %s refreshed sucessfully' % self.object.pk)
        return HttpResponseRedirect(self.get_success_url())


class KeyImportView(LoginRequiredMixin, SingleObjectMixin, View):

    model = Key
    
    def get_success_url(self):
        return reverse_lazy('key-list')

    def get(self, request, *args,**kwargs):
        self.object = self.get_object()
        import_wallet_journal(self.object.corporation.pk)
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype="application/json")
        messages.success(request, 'Key %s wallet records imported sucessfully' % self.object.pk)
        totals['%s-%s' % (dt.year, dt.month)]


class CorporationListView(LoginRequiredMixin, ListView):

    model = Corporation
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.has_perm('core.view_all_corporation'):
            return self.model.objects.all()
        else:
            return self.request.user.corporations.all()


class CorporationUpdateContactView(LoginRequiredMixin, UpdateView):

    model = Corporation
    form_class = CorporationContactForm
    template_name = 'core/corporation_contact.html'
    success_url = reverse_lazy('corporation-list')


class CorporationDetailView(LoginRequiredMixin, DetailView):
    model = Corporation
    
    def get_context_data(self, **kwargs):
        ctx = super(CorporationDetailView, self).get_context_data(**kwargs)
        
        api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())
        balances = []
        last_update = None
        for key in self.object.keys.all():
            try:
                res = api.auth(keyID=key.pk, vCode=key.vcode).corp.AccountBalance()
                for acc in res.accounts:
                    balances.append((int(acc.accountKey) - 1000, Decimal(str(acc.balance))))
                last_update = datetime.fromtimestamp(res._meta.currentTime)
                break
            except Error:
                continue
        ctx.update({
            'balances': balances,
            'last_update': last_update,
        })
        
        return ctx

class ManualAdjustmentView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):

    model = Corporation
    form_class = ManualAdjustmentForm
    permission_required = 'core.add_transaction'
    template_name = 'core/corporation_manualadjustment.html'
    
    def get_success_url(self):
        return reverse('corporation-detail', args=[self.object.pk])
    
    def get_initial(self):
        initial = super(ManualAdjustmentView, self).get_initial()
        self.object = self.get_object()
        initial.update({'corporation': self.object })
        return initial
        
    def form_valid(self, form):
        data = form.cleaned_data
        trans = Transaction.objects.create(corporation=data['corporation'], value=data['amount'], comment=data['comment'], type=Transaction.TRANSACTION_TYPE_MANUAL)
        self.object.balance += trans.value
        self.object.save()
        messages.success(self.request, 'Manual adjustment of %s ISK has been added to %s' % (trans.value, trans.corporation))
        return super(ManualAdjustmentView, self).form_valid(form)


class ChargeTotalView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, View):

    model = MonthTotal
    permission_required = 'core.charge_monthtotal'
    
    def get(self, *args, **kwargs):
        self.object = self.get_object()
        
        self.object.corporation.balance -= Decimal(str(self.object.fees_due))
        self.object.charged = True
        
        self.object.save()
        self.object.corporation.save()
        
        Transaction.objects.create(corporation=self.object.corporation, type=Transaction.TRANSACTION_TYPE_CHARGE, value=Decimal(str(-self.object.fees_due)), comment="Charges for period %s-%s" % (self.object.year, self.object.month))
        
        if self.request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype="application/json")
        messages.success(self.request, 'Total of %s ISK has been billed successfully' % self.object.fees_due)
        return HttpResponseRedirect(reverse('corporation-detail', args=[self.object.corporation.pk]))
        


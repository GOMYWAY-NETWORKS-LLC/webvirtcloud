from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from accounts.models import UserInstance
from instances.models import Instance
from accounts.forms import UserAddForm


def profile(request):
    """
    :param request:
    :return:
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'profile.html', locals())


def accounts(request):
    """
    :param request:
    :return:
    """

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    error_messages = []
    users = User.objects.filter(is_staff=False, is_superuser=False)

    if request.method == 'POST':
        if 'create' in request.POST:
            form = UserAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
            else:
                for msg_err in form.errors.values():
                    error_messages.append(msg_err.as_text())
            if not error_messages:
                new_user = User.objects.create_user(data['name'], None, data['password'])
                new_user.save()
                return HttpResponseRedirect(request.get_full_path())
        if 'edit' in request.POST:
            user_id = request.POST.get('user_id', '')
            user_pass = request.POST.get('user_pass', '')
            user_edit = User.objects.get(id=user_id)
            user.password = user_pass
            user_edit.save()
            return HttpResponseRedirect(request.get_full_path())
        if 'block' in request.POST:
            user_id = request.POST.get('user_id', '')
            user_block = User.objects.get(id=user_id)
            user_block.is_active = False
            user_block.save()
            return HttpResponseRedirect(request.get_full_path())
        if 'unblock' in request.POST:
            user_id = request.POST.get('user_id', '')
            user_unblock = User.objects.get(id=user_id)
            user_unblock.is_active = True
            user_unblock.save()
            return HttpResponseRedirect(request.get_full_path())
        if 'delete' in request.POST:
            user_id = request.POST.get('user_id', '')
            try:
                del_user_inst = UserInstance.objects.filter(user_id=user_id)
                del_user_inst.delete()
            finally:
                user_delete = User.objects.get(id=user_id)
                user_delete.delete()
            return HttpResponseRedirect(request.get_full_path())

    return render(request, 'accounts.html', locals())


def account(request, user_id):
    """
    :param request:
    :return:
    """

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    error_messages = []
    user = User.objects.get(id=user_id)
    user_insts = UserInstance.objects.filter(user_id=user_id)
    instances = Instance.objects.all()

    if request.method == 'POST':
        if 'delete' in request.POST:
            user_inst = request.POST.get('user_inst', '')
            del_user_inst = UserInstance.objects.get(id=user_inst)
            del_user_inst.delete()
            return HttpResponseRedirect(request.get_full_path())
        if 'permission' in request.POST:
            user_inst = request.POST.get('user_inst', '')
            inst_change = request.POST.get('inst_change', '')
            inst_delete = request.POST.get('inst_delete', '')
            edit_user_inst = UserInstance.objects.get(id=user_inst)
            edit_user_inst.is_change = bool(inst_change)
            edit_user_inst.is_delete = bool(inst_delete)
            edit_user_inst.save()
            return HttpResponseRedirect(request.get_full_path())
        if 'add' in request.POST:
            inst_id = request.POST.get('inst_id', '')
            try:
                check_inst = UserInstance.objects.get(instance_id=int(inst_id))
                msg = _("Instance already added")
                error_messages.append(msg)
            except UserInstance.DoesNotExist:
                add_user_inst = UserInstance(instance_id=int(inst_id), user_id=user_id)
                add_user_inst.save()
                return HttpResponseRedirect(request.get_full_path())

    return render(request, 'account.html', locals())
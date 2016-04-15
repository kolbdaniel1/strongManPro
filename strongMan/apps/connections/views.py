from collections import OrderedDict
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

import strongMan.apps.connections.forms.add_wizard
import strongMan.apps.connections.forms.core
from .models import Connection, Secret, Address
from . import models
from . import forms
from strongMan.apps.vici.wrapper.wrapper import ViciWrapper
from strongMan.apps.vici.wrapper.exception import ViciSocketException, ViciLoadException, ViciInitiateException, ViciTerminateException
from .request_handler.CreateHandler import CreateHandler
from .request_handler.UpdateHandler import UpdateHandler


@require_http_methods('GET')
@login_required
def overview(request):
    try:
        vici_wrapper = ViciWrapper()
        for connection in Connection.objects.all():
            connection.state = vici_wrapper.is_connection_established(connection.profile)
            connection.save()
    except ViciSocketException as e:
        return render(request, 'index.html')
    except ViciLoadException as e:
        messages.warning(request, str(e))

    connections = []

    for cls in Connection.get_types():
        connection_class = getattr(models, cls)
        for connection in connection_class.objects.all():
            connection_dict = dict(id=connection.id, profile=connection.profile, state=connection.state)
            address = Address.objects.filter(remote_addresses=connection).first()
            connection_dict['remote'] = address.value
            connection_dict['edit'] = "/connections/" + str(connection.id)
            connection_dict['connection_type'] = cls
            connection_dict['delete'] = "/connections/delete/" + str(connection.id)
            connections.append(connection_dict)

    context = dict(connections=connections)
    return render(request, 'index.html', context)


@login_required
@require_http_methods(['POST', 'GET'])
def create(request):
    handler = CreateHandler(request)
    return handler.handle()


@login_required
def update(request, id):
    handler = UpdateHandler(request, id)
    return handler.handle()


@login_required
@require_http_methods('POST')
def toggle_connection(request):
    connection = Connection.objects.get(id=request.POST['id']).subclass()
    response = dict(id=request.POST['id'], success=False)
    try:
        vici_wrapper = ViciWrapper()
        if vici_wrapper.is_connection_established(connection.profile) is False:
            vici_wrapper.load_connection(connection.dict())
            for secret in Secret.objects.filter(connection=connection):
                vici_wrapper.load_secret(secret.dict())
            for child in connection.children.all():
                reports = vici_wrapper.initiate(child.name, connection.profile)
            connection.state = True
        else:
            vici_wrapper.unload_connection(connection.profile)
            vici_wrapper.terminate_connection(connection.profile)
            connection.state = False
        connection.save()
        response['success'] = True
    except ViciSocketException as e:
        response['message'] = str(e)
    except ViciLoadException as e:
        response['message'] = str(e)
    except ViciInitiateException as e:
        response['message'] = str(e)
    except ViciTerminateException as e:
        response['message'] = str(e)
    finally:
        return JsonResponse(response)


@login_required
def delete_connection(request, id):
    connection = Connection.objects.get(id=id).subclass()
    try:
        vici_wrapper = ViciWrapper()
        if vici_wrapper.is_connection_loaded(connection.profile) is True:
            vici_wrapper.unload_connection(connection.profile)
    except ViciSocketException as e:
        messages.warning(request, str(e))
    except ViciInitiateException as e:
        messages.warning(request, str(e))
    finally:
        connection.delete_all_connected_models()
        connection.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def _get_title(form):
    return form.get_choice_name()


def _get_type_name(cls):
    return type(cls).__name__


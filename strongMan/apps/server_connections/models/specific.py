from collections import OrderedDict

from django.db import models
from django.dispatch import receiver

from strongMan.apps.certificates.models import UserCertificate, CertificateDoNotDelete, PrivateKey
from strongMan.helper_apps.encryption import fields
from .authentication import Authentication
from .common import CertConDoNotDeleteMessage, KeyConDoNotDeleteMessage


@receiver(UserCertificate.should_prevent_delete_signal, sender=UserCertificate)
def prevent_cert_delete_if_cert_is_in_use(sender, **kwargs):
    cert = kwargs['instance']
    authentications = [ident.tls_identity for ident in cert.identities] + [ident.cert_identity for ident in
                                                                           cert.identities] + \
                      [cert.server_ca_cert_authentication]

    for auth in authentications:
        if auth.count() > 0:
            raise CertificateDoNotDelete(CertConDoNotDeleteMessage(auth.first().connection))
    return False, ""


@receiver(PrivateKey.should_prevent_delete_signal, sender=PrivateKey)
def prevent_key_delete_if_cert_is_in_use(sender, **kwargs):
    cert = kwargs['usercertificate']
    authentications = [ident.tls_identity for ident in cert.identities] + [ident.cert_identity for ident in
                                                                           cert.identities]
    for auth in authentications:
        if auth.count() > 0:
            raise CertificateDoNotDelete(KeyConDoNotDeleteMessage(auth.first().connection))
    return False, ""


class Child(models.Model):
    START_ACTION_CHOICES = (
        ('', "none"),
        ('start', "start"),
        ('trap', "trap"),
    )

    name = models.TextField()
    mode = models.TextField()
    start_action = models.CharField(max_length=5, choices=START_ACTION_CHOICES, null=True, blank=True, default=None)
    connection = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None,
                                   related_name='server_children')

    def dict(self):
        child = OrderedDict()
        local_ts = [local_t.value for local_t in self.server_local_ts.all()]
        if local_ts[0] is not '':
            child['local_ts'] = local_ts
        remote_ts = [remote_t.value for remote_t in self.server_remote_ts.all()]
        if remote_ts[0] is not '':
            child['remote_ts'] = remote_ts
        child['esp_proposals'] = [esp_proposal.type for esp_proposal in self.server_esp_proposals.all()]
        if self.start_action is not '':
            child['start_action'] = self.start_action
        return child


class Address(models.Model):
    value = models.TextField()
    local_ts = models.ForeignKey(Child, null=True, blank=True, default=None, related_name='server_local_ts')
    remote_ts = models.ForeignKey(Child, null=True, blank=True, default=None, related_name='server_remote_ts')
    remote_addresses = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None,
                                         related_name='server_remote_addresses')
    local_addresses = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None,
                                        related_name='server_local_addresses')


class Proposal(models.Model):
    type = models.TextField()
    child = models.ForeignKey(Child, null=True, blank=True, default=None, related_name='server_esp_proposals')
    connection = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None,
                                   related_name='server_proposals')


class LogMessage(models.Model):
    connection = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

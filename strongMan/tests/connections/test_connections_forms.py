import os
from django.test import TestCase
from django.http import QueryDict
from strongMan.apps.certificates.container_reader import X509Reader, PKCS1Reader
from strongMan.apps.connections.forms.add_wizard import ChooseTypeForm, Ike2CertificateForm, Ike2EapForm, \
    Ike2EapCertificateForm
from strongMan.apps.certificates.models import Certificate
from strongMan.apps.certificates.services import UserCertificateManager


class ConnectionFormsTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        bytes = Paths.X509_googlecom.read()
        manager = UserCertificateManager()
        manager.add_keycontainer(bytes)
        manager.add_keycontainer(Paths.X509_rsa_ca.read())
        manager.add_keycontainer(Paths.PKCS1_rsa_ca.read())

        self.certificate = Certificate.objects.first().subclass()
        self.usercert = Certificate.objects.get(pk=2)

        self.identity = self.certificate.identities.first()

    def test_ChooseTypeForm(self):
        form_data = {'current_form':"ChooseTypeForm", 'form_name':  "Ike2CertificateForm"}
        form = ChooseTypeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ChooseTypeForm_invalid(self):
        form_data = {'current_form':"ChooseTypeForm", 'form_name':  "sting"}
        form = ChooseTypeForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_ConnectionForm_server_as_caidentity(self):
        form_data = {'current_form': Ike2CertificateForm, 'gateway': "gateway", 'profile': 'profile', 'identity': self.usercert.identities.first().pk,
                     'certificate': self.usercert.pk, 'certificate_ca': self.certificate.pk, 'is_server_identity': True}
        form = Ike2CertificateForm(data=form_data)
        form.update_certificates()
        self.assertTrue(form.is_valid())

    def test_ConnectionForm_server_as_caidentity_unchecked(self):
        form_data = {'current_form': Ike2CertificateForm, 'gateway': "gateway", 'profile': 'profile', 'identity': self.usercert.identities.first().pk,
                     'certificate': self.usercert.pk, 'certificate_ca': self.certificate.pk, 'identity_ca': "gateway"}
        form = Ike2CertificateForm(data=form_data)
        form.update_certificates()
        self.assertTrue(form.is_valid())

    def test_ConnectionForm_server_as_caidentity_empty_identity_ca(self):
        form_data = {'current_form': Ike2CertificateForm, 'gateway': "gateway", 'profile': 'profile', 'identity': self.usercert.identities.first().pk,
                     'certificate': self.usercert.pk, 'certificate_ca': self.certificate.pk}
        form = Ike2CertificateForm(data=form_data)
        form.update_certificates()
        self.assertFalse(form.is_valid())

    def test_Ike2CertificateForm(self):
        form_data = {'gateway': "gateway", 'profile': 'profile', 'identity': self.identity.pk, 'certificate': self.certificate.pk}
        form = Ike2CertificateForm(data=form_data)
        #TODO Update Choices Field
        self.assertFalse(form.is_valid())

    def test_Ike2CertificateForm_invalid(self):
        form_data = {'gateway': "gateway", 'profile': 'profile'}
        form = Ike2CertificateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_Ike2EapCertificateForm(self):
        form_data = {'gateway': "gateway", 'username': "username", 'password': 'password', 'profile': 'profile', 'certificate': self.identity.id}
        form = Ike2EapCertificateForm(data=form_data)
        #TODO Update Choices Field
        self.assertFalse(form.is_valid())

    def test_Ike2EapForm(self):
        form_data = {'current_form':"Ike2EapForm", 'gateway': "gateway", 'username': "username", 'password': 'password',
                     'profile': 'profile', 'certificate_ca': self.certificate.pk, 'identity_ca': "yolo"}
        form = Ike2EapForm(data=form_data)
        form.update_certificates()
        valid = form.is_valid()
        self.assertTrue(valid)


    def test_Ike2EapForm_invalid(self):
        form_data = {'gateway': "gateway", 'username': "username", 'password': 'password'}
        form = Ike2EapForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_Ike2EapCertificateForm_invalid(self):
        form_data = {'gateway': "gateway", 'username': "username", 'password': 'password', 'profile': 'profile'}
        form = Ike2EapCertificateForm(data=form_data)
        self.assertFalse(form.is_valid())

class TestCert:
    def __init__(self, path):
        self.path = path
        self.parent_dir = os.path.join(os.path.dirname(__file__), os.pardir)

    def read(self):
        absolute_path = self.parent_dir + "/certificates/certs/" + self.path
        with open(absolute_path, 'rb') as f:
            return f.read()

    def read_x509(self, password=None):
        bytes = self.read()
        reader = X509Reader.by_bytes(bytes, password)
        reader.parse()
        return reader

    def read_pkcs1(self, password=None):
        bytes = self.read()
        reader = PKCS1Reader.by_bytes(bytes, password)
        reader.parse()
        return reader


class Paths:
    X509_rsa_ca = TestCert("ca.crt")
    X509_rsa_ca_samepublickey_differentserialnumber = TestCert("hsrca_doppelt_gleicher_publickey.crt")
    X509_rsa_ca_samepublickey_differentserialnumber_san = TestCert("cacert_gleicher_public_anderer_serial.der")
    PKCS1_rsa_ca = TestCert("ca2.key")
    PKCS1_rsa_ca_encrypted = TestCert("ca.key")
    PKCS8_rsa_ca = TestCert("ca2.pkcs8")
    PKCS8_ec = TestCert("ec.pkcs8")
    PKCS8_rsa_ca_encrypted = TestCert("ca_enrypted.pkcs8")
    X509_rsa_ca_der = TestCert("cacert.der")
    X509_ec = TestCert("ec.crt")
    PKCS1_ec = TestCert("ec2.key")
    X509_rsa = TestCert("warrior.crt")
    PKCS12_rsa = TestCert("warrior.pkcs12")
    PKCS12_rsa_encrypted = TestCert("warrior_encrypted.pkcs12")
    X509_googlecom = TestCert("google.com_der.crt")

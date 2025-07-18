from django.urls import reverse

from oscar.apps.partner import models
from oscar.core.loading import get_class
from oscar.test.testcases import WebTestCase

DashboardPermission = get_class("dashboard.permissions", "DashboardPermission")


class TestPartnerDashboard(WebTestCase):
    is_staff = True
    permissions = DashboardPermission.get("partner")

    def test_allows_a_partner_user_to_be_created(self):
        partner = models.Partner.objects.create(name="Acme Ltd")

        url = reverse("dashboard:partner-list")
        list_page = self.get(url)
        detail_page = list_page.click("Manage partner and users")
        user_page = detail_page.click("Link a new user")
        form = user_page.forms["user_partner_form"]
        form["first_name"] = "Maik"
        form["last_name"] = "Hoepfel"
        form["email"] = "maik@gmail.com"
        form["password1"] = "helloworld"
        form["password2"] = "helloworld"
        form.submit()

        self.assertEqual(1, partner.users.all().count())

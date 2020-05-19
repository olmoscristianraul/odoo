from odoo import api, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    def is_ar_portal_user(self):
        """ Is a portal user in an argentinian company """
        self.ensure_one()
        if self.has_group('base.group_portal') and self.company_ids.filtered(lambda x: x.country_id == self.env.ref('base.ar')):
            return True
        return False

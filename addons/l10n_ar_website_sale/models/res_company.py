# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_public_user(self):
        if self.env.company.country_id == self.env.ref('base.ar'):
            # We need sudo to be able to see public users from others companies too
            public_users = self.env.ref('base.group_public').sudo().with_context(active_test=False).users
            public_users_for_website = public_users.filtered(lambda user: user.company_id == self)

            if public_users_for_website:
                return public_users_for_website[0]
            else:
                return self.env['res.users'].sudo().create({
                    'name': 'Public user for %s' % self.name,
                    'login': 'public-user@company-%s.com' % self.id,
                    'company_id': self.id,
                    'company_ids': [(6, 0, [self.id])],
                    'active': False,
                    'groups_id': [(6, 0, [self.env.ref('base.group_public').id])],
                })
        return super()._get_public_user()

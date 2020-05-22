from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        """ When invoice is created from a website sale order then we need to fix the journal to use: local journal vs exportation journals """
        # TODO take into account journal for bono fiscal?
        res = super().create(values)
        if res.team_id.name == 'Website':  # TODO change this. why source_id is False :(? y team_id = 'Website'
            res._onchange_partner_journal()
        return res
